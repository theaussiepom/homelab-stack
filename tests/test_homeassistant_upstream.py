"""Official-image conversion preserves the retained listener and startup contract."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ['HOMELAB_FRAMEWORK']).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints'), str(FRAMEWORK / 'proxmox/applications')]
import compile as compiler
import component_checks
import component_lower
import component_sources
import render
from component_errors import ComponentError


class OfficialHomeAssistant(unittest.TestCase):
    def resolve(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'site.json'
            path.write_text(json.dumps(source))
            with patch('subprocess.run', side_effect=AssertionError('No native operations')), \
                 patch('socket.create_connection', side_effect=AssertionError('No target contact')):
                plan = compiler.resolve_plan(ROOT, path, [])
                compiler.lower_plan(plan)
        return plan

    def source(self):
        return component_sources.site(ROOT / 'examples/catalogue/existing-homeassistant-upstream.yaml')[0]

    def test_conversion_changes_only_image_and_pull_policy_in_compose(self):
        source = self.source()
        source['connections'].pop('ha_controller')
        source['apps']['homeassistant']['interfaces'].pop('management_interface')
        official = self.resolve(source)
        source['apps']['homeassistant']['profile'] = 'homeassistant-bound'
        archived = self.resolve(source)
        self.assertEqual(component_lower.provider_config(official, 'homeassistant'),
                         component_lower.provider_config(archived, 'homeassistant'))
        current = component_lower.runtime_config(official, 'homeassistant')
        previous = component_lower.runtime_config(archived, 'homeassistant')
        new_app, old_app = (cfg['applications']['homeassistant'] for cfg in (current, previous))
        self.assertEqual(new_app['storage_paths'], old_app['storage_paths'])
        self.assertEqual(new_app['listeners'], old_app['listeners'])
        self.assertEqual(component_checks._homeassistant(new_app, None),
                         component_checks._homeassistant(old_app, None))
        new_compose, old_compose = (render.compositions(cfg) for cfg in (current, previous))
        self.assertEqual(set(new_compose), set(old_compose))
        for filename in new_compose:
            new, old = (c[filename] for c in (new_compose, old_compose))
            new_service = new['services']['homeassistant_homeassistant']
            old_service = old['services']['homeassistant_homeassistant']
            image = json.loads((ROOT / 'images.json').read_text())['homeassistant_upstream']
            self.assertRegex(image['tag'], r'^\d{4}\.\d+\.\d+$')
            self.assertEqual(new_service.pop('image'), image['repository'] + ':' + image['tag'] + '@' + image['digest'])
            self.assertTrue(old_service.pop('image').startswith('sha256:'))
            self.assertEqual(new_service.pop('pull_policy'), 'missing')
            self.assertEqual(old_service.pop('pull_policy'), 'never')
            self.assertEqual(new, old)
            self.assertEqual(new_service['entrypoint'], ['/bin/sh', '-c', '/startup/mdns-route.sh && exec /init'])
            self.assertEqual(new_service['cap_add'], ['NET_ADMIN'])
            self.assertEqual(new_service['environment']['HOMELAB_HA_IPV4'], '198.18.20.20')
            self.assertIn('/srv/example/homeassistant/homeassistant/startup:/startup:ro', new_service['volumes'])

    def test_controller_connection_keeps_hostname_scoped_to_home_assistant(self):
        source = self.source()
        with_controller = self.resolve(source)
        source['connections'].pop('ha_controller')
        without_controller = self.resolve(source)
        self.assertEqual(component_lower.provider_config(with_controller, 'homeassistant'),
                         component_lower.provider_config(without_controller, 'homeassistant'))
        actual, prior = (
            render.compositions(component_lower.runtime_config(plan, 'homeassistant'))
            for plan in (with_controller, without_controller)
        )
        self.assertEqual(len(actual), 1)
        service = next(iter(actual.values()))['services']['homeassistant_homeassistant']
        self.assertEqual(service.pop('extra_hosts'),
                         {'controller.example.invalid': '198.18.20.3'})
        self.assertEqual(actual, prior)

    def test_unused_archive_binding_must_be_removed(self):
        source = self.source()
        source['images']['homeassistant'] = {
            'archive': '/var/lib/example/old-homeassistant.tar',
            'archive_sha256': 'a' * 64, 'local_id': 'sha256:' + 'b' * 64}
        with self.assertRaisesRegex(ComponentError, 'component.image-binding-unused'):
            self.resolve(source)

    def test_no_initializer_or_implicit_network_capability(self):
        library, _ = component_sources.library(ROOT)
        official = copy.deepcopy(library['app_profiles']['homeassistant-upstream-bound'])
        archived = copy.deepcopy(library['app_profiles']['homeassistant-bound'])
        official.pop('display_name'); archived.pop('display_name')
        official['software'].remove('homeassistant-upstream-images')
        archived['software'].remove('homeassistant-custom-images')
        self.assertEqual(official['interfaces'].pop('management_interface'),
                         {'required': False, 'accepts': ['guest-interface']})
        self.assertEqual(official['connections'].pop('controller'),
                         {'type': 'https', 'required': False})
        self.assertEqual(official, archived)
        source = self.source()
        app = source['apps']['homeassistant']
        app.pop('properties'); app.pop('runtime'); app['storage'].pop('startup')
        plan = self.resolve(source)
        config = component_lower.runtime_config(plan, 'homeassistant')
        compose = next(iter(render.compositions(config).values()))
        service = compose['services']['homeassistant_homeassistant']
        self.assertNotIn('entrypoint', service)
        self.assertNotIn('cap_add', service)


if __name__ == '__main__':
    unittest.main()
