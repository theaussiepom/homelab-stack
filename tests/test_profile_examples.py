"""Real canonical profile compositions, not target installation acceptance."""
import copy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints')]
import compile as compiler
import component_sources
import component_lower
from component_errors import ComponentError
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]
from profile_example_cases import PROFILE_EXAMPLES, CREATION_EXAMPLES


def no_native(*args, **kwargs):
    raise AssertionError('Profile example tests cannot execute a process or contact a target')


def compile_examples():
    paths = {path for path, _ in [*PROFILE_EXAMPLES.values(), *CREATION_EXAMPLES.values()]}
    results = {}
    with patch('subprocess.run', side_effect=no_native), \
         patch('subprocess.check_output', side_effect=no_native), \
         patch('socket.create_connection', side_effect=no_native):
        for path in sorted(paths):
            plan = compiler.resolve_plan(ROOT, ROOT / path, [])
            packets = compiler.lower_plan(plan)
            results[path] = (plan, packets)
    return results


class ProfileExampleIntegrations(unittest.TestCase):
    def test_renovate_has_one_explicit_postgresql_owner_and_no_ingress_dependency(self):
        plan, packets = self.examples['examples/catalogue/renovate.yaml']
        self.assertEqual(plan.resolved['guest_dependencies']['renovate'], ['postgresql'])
        self.assertEqual(plan.resolved['app_dependencies']['renovate'], ['postgresql'])
        self.assertEqual(set(plan.resolved['apps']), {'renovate','postgresql'})
        worker, database = (plan.resolved['apps'][name] for name in ('renovate','postgresql'))
        self.assertEqual(database['secret_bindings']['application_database_password'], worker['secret_bindings']['database_password'])
        self.assertEqual(database['settings']['client_access'][-1], {
            'source_address':'198.18.20.18','database':'renovate','user':'renovate','method':'scram-sha-256'})
        service = json.loads(packets['renovate']['files']['compose-renovate.yml'])['services']['renovate']
        self.assertNotIn('ports', service)
        self.assertTrue(service['read_only'])
        self.assertNotIn('MEND_RNV_ACCEPT_TOS', service['environment'])
        self.assertNotIn('PGPASSWORD', service['environment'])
        self.assertEqual(service['environment']['PGHOST'], '198.18.20.10')
        self.invalid_source('examples/catalogue/renovate.yaml',
            lambda value: value['apps']['postgresql']['properties'].pop('application_database'),
            ComponentError, 'component.database-binding')
        self.invalid_source('examples/catalogue/renovate.yaml',
            lambda value: value['apps']['renovate']['properties'].update(repositories=['example/*']),
            ComponentError, 'component.renovate-repositories')

    def test_radio_watchdog_compiles_only_the_selected_environment_setting(self):
        path = 'examples/catalogue/messaging-radio.yaml'
        selected, packets = self.examples[path]
        self.assertEqual(selected.resolved['apps']['radio']['properties']['watchdog'], 'default')
        current = json.loads(packets['radio']['files']['compose-radio.yml'])
        self.assertEqual(current['services']['radio_zigbee2mqtt']['environment'].pop('Z2M_WATCHDOG'), 'default')
        source, _ = component_sources.site(ROOT / path)
        self.assertEqual(source['apps']['radio']['properties'].pop('watchdog'), 'default')
        with tempfile.TemporaryDirectory() as tmp:
            omitted = Path(tmp).resolve() / 'site.json'
            omitted.write_text(json.dumps(source))
            with patch('subprocess.run', side_effect=no_native), \
                 patch('subprocess.check_output', side_effect=no_native), \
                 patch('socket.create_connection', side_effect=no_native):
                baseline = compiler.lower_plan(compiler.resolve_plan(ROOT, omitted, []))
        self.assertEqual(current, json.loads(baseline['radio']['files']['compose-radio.yml']))
        for guest in packets:
            if guest != 'radio':
                self.assertEqual(packets[guest], baseline[guest])

    @classmethod
    def setUpClass(cls):
        cls.examples = compile_examples()

    def test_ha_dual_web_preserves_the_entire_service_provider_and_core_probe(self):
        import render
        import component_checks
        selected, _ = self.examples['examples/catalogue/existing-automation-dual-web.yaml']
        source, _ = component_sources.site(ROOT/'examples/catalogue/existing-automation-dual-web.yaml')
        source['apps']['homeassistant']['profile'] = 'homeassistant-bound'
        source['apps']['homeassistant']['interfaces'].pop('transition_web_interface')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve()/'site.json'; path.write_text(json.dumps(source))
            with patch('subprocess.run', side_effect=no_native), \
                 patch('subprocess.check_output', side_effect=no_native), \
                 patch('socket.create_connection', side_effect=no_native):
                original = compiler.resolve_plan(ROOT, path, [])
                compiler.lower_plan(original)
        for guest in selected.resolved['guests']:
            self.assertEqual(component_lower.provider_config(selected, guest),
                             component_lower.provider_config(original, guest))
            current = component_lower.runtime_config(selected, guest)
            previous = component_lower.runtime_config(original, guest)
            self.assertEqual(render.compositions(current), render.compositions(previous))
        old = component_lower.runtime_config(original, 'homeassistant')['applications']['homeassistant']
        new = component_lower.runtime_config(selected, 'homeassistant')['applications']['homeassistant']
        self.assertEqual(component_checks._homeassistant(new, None)[0],
                         component_checks._homeassistant(old, None)[0])
        self.assertEqual(selected.resolved['endpoints']['app/homeassistant/web_endpoint'],
                         original.resolved['endpoints']['app/homeassistant/web_endpoint'])
        self.assertEqual(selected.resolved['endpoints']['app/homeassistant/transition_web_endpoint']['address'],
                         '198.18.40.20')

    def test_ha_dual_web_requires_the_transition_role_and_prepared_retained_installation(self):
        self.invalid_source('examples/catalogue/existing-automation-dual-web.yaml',
            lambda value: value['apps']['homeassistant']['interfaces'].pop('transition_web_interface'),
            ComponentError, 'component.invalid')
        self.invalid_source('examples/catalogue/existing-automation-dual-web.yaml',
            lambda value: value['apps']['homeassistant'].update(lifecycle='fresh'),
            ComponentError, 'component.health-lifecycle')

    def test_split_pihole_preserves_dns_and_the_complete_existing_service(self):
        import render
        plan, _ = self.examples['examples/catalogue/local-dns-web/site.yaml']
        source, _ = component_sources.site(ROOT / 'examples/catalogue/local-dns-web/site.yaml')
        source['apps']['filtering']['profile'] = 'pihole'
        source['apps']['filtering']['interfaces'].pop('web_interface')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'site.json'
            path.write_text(json.dumps(source))
            original = compiler.resolve_plan(ROOT, path, [])
        for name in ('dns_udp_endpoint', 'dns_tcp_endpoint'):
            self.assertEqual(plan.resolved['endpoints']['app/filtering/' + name],
                             original.resolved['endpoints']['app/filtering/' + name])
        self.assertEqual(plan.resolved['endpoints']['app/filtering/web_endpoint']['address'],
                         '198.18.30.10')
        self.assertEqual(component_lower.provider_config(plan, 'resolver'),
                         component_lower.provider_config(original, 'resolver'))
        current_runtime = component_lower.runtime_config(plan, 'resolver')
        original_runtime = component_lower.runtime_config(original, 'resolver')
        current = render.compositions(current_runtime)
        previous = render.compositions(original_runtime)
        service = current['example-dns']['services']['filtering']
        self.assertEqual(service['environment'].pop('FTLCONF_webserver_port'), '198.18.30.10:80')
        self.assertEqual(current, previous)
        self.assertEqual(plan.resolved['apps']['filtering']['resolved_connections'],
                         original.resolved['apps']['filtering']['resolved_connections'])

    def test_split_pihole_requires_its_explicit_web_role(self):
        self.invalid_source('examples/catalogue/local-dns-web/site.yaml',
            lambda value: value['apps']['filtering']['interfaces'].pop('web_interface'),
            ComponentError, 'component.invalid')

    def test_music_https_probe_uses_the_declared_stream_source_and_keeps_its_assertions(self):
        import component_checks
        old, _ = self.examples['examples/catalogue/music-split.yaml']
        source, _ = component_sources.site(ROOT / 'examples/catalogue/music-split.yaml')
        source['connections']['music_public']['source_interface'] = 'stream_interface'
        source['policies']['network']['connect_music_public_incoming']['rules'][0]['source'] = '198.18.100.40/32'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'site.json'
            path.write_text(json.dumps(source))
            with patch('subprocess.run', side_effect=no_native), \
                 patch('subprocess.check_output', side_effect=no_native), \
                 patch('socket.create_connection', side_effect=no_native):
                selected = compiler.resolve_plan(ROOT, path, [])
                compiler.lower_plan(selected)
        def checks(plan):
            app = component_lower.runtime_config(plan, 'media')['applications']['music']
            return component_checks._music_assistant(app, '/opt/homelab-app/compose.yml')
        original = checks(old); actual = checks(selected)
        expected = copy.deepcopy(original)
        argv = expected[1]['argv']; argv[argv.index('--interface') + 1] = '198.18.100.40'
        self.assertEqual(actual, expected)

    def test_split_music_allows_only_selected_players_to_its_stream_socket(self):
        """Check the actual compiled policy for its intended and denied flows."""
        from component_traffic import Flow, permits
        plan, _ = self.examples['examples/catalogue/music-split.yaml']
        rules = plan.resolved['guests']['media']['rules']
        self.assertTrue(permits(rules, 'in', Flow(
            '198.18.100.50', '198.18.100.40', 'tcp', 8097), 'net1'))
        for source, target, protocol, port, interface in (
                ('198.18.20.50', '198.18.100.40', 'tcp', 8097, 'net1'),
                ('198.18.100.50', '198.18.20.40', 'tcp', 8097, 'net0'),
                ('198.18.100.50', '198.18.100.40', 'udp', 8097, 'net1'),
                ('198.18.100.50', '198.18.100.40', 'tcp', 8095, 'net1')):
            with self.subTest(source=source, target=target, protocol=protocol, port=port):
                self.assertFalse(permits(rules, 'in', Flow(source, target, protocol, port), interface))

    def test_every_real_profile_and_variant_has_a_complete_resolved_and_lowered_usage(self):
        library, _ = component_sources.library(ROOT)
        self.assertEqual(set(PROFILE_EXAMPLES), set(library['app_profiles']))
        for profile, (path, instance) in PROFILE_EXAMPLES.items():
            with self.subTest(profile=profile):
                plan, packets = self.examples[path]
                self.assertEqual(plan.resolved['apps'][instance]['profile'], profile)
                self.assertEqual(set(packets), set(plan.resolved['guests']))
                for guest, packet in packets.items():
                    self.assertEqual(packet['schema'], 'homelab-component-guest-deployment-v1')
                    self.assertEqual(packet['guest'], guest)
                    cfg = json.loads(packet['files']['site.json'])
                    self.assertTrue(cfg['deployment']['phases'])
                    self.assertIn('component-runtime.json', packet['files'])

    def test_profile_selection_fragments_match_the_linked_single_source_authority(self):
        index = (ROOT / 'examples/catalogue/README.md').read_text()
        for profile, (path, instance) in PROFILE_EXAMPLES.items():
            with self.subTest(profile=profile):
                page = (ROOT / 'docs/reference/apps' / (profile + '.md')).read_text()
                self.assertIn('(../../../' + path + ')', page)
                self.assertIn('`' + instance + '`', page)
                self.assertIn('| [' + profile + ']', index)
                found = re.findall(r'## Minimal usage\n.*?```yaml\n(.*?)```', page, re.S)
                self.assertEqual(len(found), 1)
                with tempfile.TemporaryDirectory() as tmp:
                    source = Path(tmp).resolve() / 'fragment.yaml'
                    source.write_text(found[0])
                    fragment = compiler.read(source)
                plan, _ = self.examples[path]
                app = plan.resolved['apps'][instance]
                self.assertEqual(fragment, {'apps': {instance: {
                    'profile': profile, 'guest': app['guest'], 'lifecycle': app['lifecycle']}}})
                for heading in ('First installation', 'Later deployments', 'Invalid cases'):
                    self.assertIn('## ' + heading, page)

    def test_creation_examples_keep_the_policy_and_stable_identity_on_a_later_source_revision(self):
        for profile, (path, instance) in CREATION_EXAMPLES.items():
            with self.subTest(profile=profile):
                old, _ = self.examples[path]
                app = old.resolved['apps'][instance]
                self.assertEqual(app['lifecycle'], 'fresh')
                value, _ = component_sources.site(ROOT / path)
                value['apps'][instance]['display_name'] = 'A later descriptive label'
                with tempfile.TemporaryDirectory() as tmp:
                    source = Path(tmp).resolve() / 'site.json'
                    source.write_text(json.dumps(value))
                    with patch('subprocess.run', side_effect=no_native), \
                         patch('subprocess.check_output', side_effect=no_native), \
                         patch('socket.create_connection', side_effect=no_native):
                        later = compiler.resolve_plan(ROOT, source, [])
                        compiler.lower_plan(later)
                updated = later.resolved['apps'][instance]
                self.assertEqual(updated['lifecycle'], 'fresh')
                self.assertEqual(updated['identity'], app['identity'])
                before_runtime = component_lower.runtime_config(old, app['guest'])['applications'][instance]
                after_runtime = component_lower.runtime_config(later, app['guest'])['applications'][instance]
                self.assertEqual(after_runtime['storage_paths'], before_runtime['storage_paths'])
                self.assertEqual(later.resolved['app_dependencies'], old.resolved['app_dependencies'])
        # Actual ordinary owned-update admission is the framework's lifecycle
        # integration boundary, not simulated by changing a source policy here.

    def invalid_source(self, path, change, expected, message):
        value, _ = component_sources.site(ROOT / path)
        change(value)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp).resolve() / 'site.json'
            source.write_text(json.dumps(value))
            with patch('subprocess.run', side_effect=no_native), \
                 patch('subprocess.check_output', side_effect=no_native), \
                 patch('socket.create_connection', side_effect=no_native), \
                 self.assertRaisesRegex(expected, message):
                compiler.lower_plan(compiler.resolve_plan(ROOT, source, []))

    def test_documented_current_packet_floors_refuse_without_native_effects(self):
        self.invalid_source('examples/catalogue/messaging-radio.yaml',
            lambda v: v['apps']['broker'].pop('secrets'), ComponentError, 'component.secret-required')
        self.invalid_source('examples/catalogue/music.yaml',
            lambda v: v['connections'].pop('music_public'), ComponentError, 'component.type')
        self.invalid_source('examples/catalogue/database-guis.yaml',
            lambda v: v['apps']['cloud']['properties']['connections']['postgresql-admin'].update(sslmode='require'),
            ComponentError, 'component.properties')
        def metadata_only(value):
            value['apps']['cloud']['properties']['connections'].pop('postgresql-admin')
            value['connections'].pop('postgres_administration')
            value['accounts'].pop('postgres_admin')
        self.invalid_source('examples/catalogue/database-guis.yaml', metadata_only,
            ValueError, 'Keep new owned administrator connections separate from retained metadata')

    def test_future_profile_authoring_paths_require_the_reusable_documentation_template(self):
        template = ROOT / 'docs/templates/application-profile.md'
        self.assertTrue(template.is_file())
        text = template.read_text()
        for topic in ('Purpose', 'Syntax and properties', 'Minimal and practical examples',
                      'First installation', 'Later deployments', 'Invalid cases and validation'):
            self.assertIn('## ' + topic, text)
        self.assertIn('docs/templates/application-profile.md', (ROOT / 'AGENTS.md').read_text())
        self.assertIn('(templates/application-profile.md)', (ROOT / 'docs/contributing.md').read_text())
        self.assertIn('(../templates/application-profile.md)', (ROOT / 'docs/reference/README.md').read_text())


if __name__ == '__main__':
    unittest.main()
