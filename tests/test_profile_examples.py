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
    @classmethod
    def setUpClass(cls):
        cls.examples = compile_examples()

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
