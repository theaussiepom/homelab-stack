"""Reusable allocation contracts compile against genuinely distinct consumers."""
import copy
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
spec = importlib.util.spec_from_file_location('site_bindings_compiler', FRAMEWORK/'blueprints/compile.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class SiteBindingTests(unittest.TestCase):
    def test_every_required_allocation_is_explicit_and_examples_are_separate(self):
        manifest = c.manifest(ROOT)
        self.assertEqual(manifest['values'], {})
        declarations = manifest['required_site_bindings']
        for path in (ROOT/'site.example.yaml', ROOT/'examples/site.second.yaml'):
            site = c.read(path)
            self.assertEqual(set(site['values']), set(declarations))
            for key, kind in declarations.items():
                self.assertTrue(c.binding_value(site['values'][key], kind), key)
            self.assertEqual(site['accepted'], {})

    def test_two_distinct_sites_drive_identity_network_storage_and_runtime_bindings(self):
        sites = [c.merge(c.read(ROOT/path), {'zabbix': None})
                 for path in ('site.example.yaml', 'examples/site.second.yaml')]
        packets = [c.compile_stack(ROOT, site, []) for site in sites]
        self.assertTrue(all(len(selected) == 14 for selected in packets))
        self.assertEqual(set(packets[0]), set(packets[1]))
        for role in packets[0]:
            configs = [json.loads(selected[role]['files']['site.json']) for selected in packets]
            for cfg, site in zip(configs, sites):
                values = site['values']
                self.assertEqual(cfg['guest']['vmid'], values['vmids.'+role])
                self.assertEqual(cfg['guest']['hostname'], values['hostnames.'+role])
                self.assertEqual(cfg['site']['node'], values['site.node'])
                self.assertEqual(cfg['guest']['storage_id'], values['storage.guest'])
                self.assertTrue(all(n['bridge'] in {v for k,v in values.items() if k.startswith('bridges.')}
                                    for n in cfg['guest']['interfaces']))
            self.assertNotEqual(configs[0]['guest']['vmid'], configs[1]['guest']['vmid'])
            self.assertNotEqual(configs[0]['guest']['interfaces'], configs[1]['guest']['interfaces'])
        for selected in packets:
            music = json.loads(selected['music']['files']['site.json'])
            nic = music['guest']['interfaces'][2]
            prefix = ipaddress.ip_interface(nic['ipv4']).network.prefixlen
            self.assertIn(prefix, (24,25))
            self.assertEqual(music['app']['frontend_routing']['address'], nic['ipv4'])
        for selected, site in zip(packets, sites):
            ingress = json.loads(selected['ingress']['files']['stack.json'])
            self.assertEqual(ingress['routing']['routes']['nas']['url'],
                             'http://'+site['values']['addresses.nas']+':'+site['values']['ports.nas_web'])
            self.assertEqual(ingress['routing']['middlewares']['music-clients']['ipAllowList']['sourceRange'],
                             site['values']['networks.music_clients'])

    def test_missing_or_wrong_type_binding_refuses_in_the_actual_composition(self):
        baseline = c.read(ROOT/'site.example.yaml')
        for key, invalid in [('vmids.music', True), ('vlans.home', '100'),
                             ('networks.music_clients', '198.18.0.0/24'),
                             ('ssh.public_keys', []), ('hostnames.music', 207),
                             ('identity.db_tools_jwks_url', None)]:
            for omit in (True,False):
                changed = copy.deepcopy(baseline)
                if omit:
                    changed['values'].pop(key)
                else:
                    changed['values'][key] = invalid
                with self.subTest(key=key, omit=omit), self.assertRaisesRegex(ValueError,'declared site binding type'):
                    c.compile_stack(ROOT, changed, [])

    def test_synthetic_consumers_compile_but_cannot_be_admitted_for_deployment(self):
        for path in ('site.example.yaml','examples/site.second.yaml'):
            site = c.read(ROOT/path)
            self.assertTrue(c.compile_stack(ROOT,site,[]))
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'known synthetic site binding'):
                c.compile_stack(ROOT,site,[],admit=True)

    def test_stack_ci_uses_the_single_selected_framework_boundary_checker(self):
        result = subprocess.run([sys.executable,str(FRAMEWORK/'tools/check_boundaries.py'),
                                 '--mode','stack','--root',str(ROOT)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse((ROOT/'tools/check_boundaries.py').exists())


if __name__ == '__main__':
    unittest.main()
