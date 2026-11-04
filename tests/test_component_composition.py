"""Focused real source/lowerer/renderer integrations, never native/CD acceptance."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints'), str(FRAMEWORK / 'proxmox/applications')]
import authored_config
import component_lower
import component_plan
import render
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]


class ComponentCompositionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name).resolve() / 'site.json'

    def plan(self, value):
        self.source.write_text(json.dumps(value))
        return component_plan.resolve(ROOT, self.source)

    def compose(self, value, guest='resolver'):
        return render.compositions(component_lower.runtime_config(self.plan(value), guest))

    def test_main_starter_selects_only_one_unbound_and_no_historical_evidence(self):
        plan = component_plan.resolve(ROOT, ROOT / 'site.example.yaml')
        self.assertEqual(set(plan.resolved['guests']), {'resolver'})
        self.assertEqual(set(plan.resolved['apps']), {'recursive_dns'})
        self.assertEqual(plan.resolved['apps']['recursive_dns']['adapter'], 'unbound')
        cfg = component_lower.runtime_config(plan, 'resolver')
        documents = render.compositions(cfg)
        self.assertEqual(len(documents), 1)
        services = next(iter(documents.values()))['services']
        self.assertEqual(len(services), 1)
        service = next(iter(services.values()))
        self.assertEqual(service['ports'], ['127.0.0.1:5335:53/tcp', '127.0.0.1:5335:53/udp'])
        self.assertEqual(service['volumes'], [])
        self.assertEqual(service['pull_policy'], 'missing')
        self.assertNotIn('user', service)
        self.assertNotIn('network_mode', service)

    def test_repeated_profile_has_distinct_runtime_and_publication_with_cosmetic_labels(self):
        source = authored_config.read(ROOT / 'site.example.yaml')
        source['apps']['backup'] = copy.deepcopy(source['apps']['recursive_dns'])
        source['apps']['backup']['properties'] = {'publish_port': 5336}
        plan = self.plan(source)
        first, second = plan.resolved['apps']['recursive_dns'], plan.resolved['apps']['backup']
        self.assertNotEqual(first['identity']['runtime_id'], second['identity']['runtime_id'])
        self.assertNotEqual(first['project_name'] if 'project_name' in first else first['identity']['project'],
                            second['project_name'] if 'project_name' in second else second['identity']['project'])
        documents = self.compose(source)
        ports = sorted(tuple(row['ports']) for doc in documents.values() for row in doc['services'].values())
        self.assertEqual(ports, [('127.0.0.1:5335:53/tcp', '127.0.0.1:5335:53/udp'),
                                 ('127.0.0.1:5336:53/tcp', '127.0.0.1:5336:53/udp')])
        source['apps']['backup']['display_name'] = 'A cosmetic backup label'
        self.assertEqual(self.compose(source), documents)
        source['apps']['backup']['properties'] = {'publish_port': 5335}
        with self.assertRaises(ValueError): self.plan(source)

    def test_alternate_layout_renders_repeated_resolvers_and_homeassistant_without_integrations(self):
        plan = component_plan.resolve(ROOT, ROOT / 'examples/site.second.yaml')
        self.assertEqual(set(plan.resolved['guests']), {'resolver-east', 'resolver-west', 'home-app'})
        self.assertEqual(len(plan.resolved['apps']), 4)
        self.assertEqual(plan.resolved['apps']['home']['resolved_connections'], {})
        self.assertEqual(plan.resolved['app_dependencies']['home'], [])
        self.assertEqual(plan.resolved['guest_dependencies']['home-app'], [])
        self.assertNotIn('node_red', {app['adapter'] for app in plan.resolved['apps'].values()})
        services = {}
        for guest in plan.resolved['guests']:
            documents = render.compositions(component_lower.runtime_config(plan, guest))
            services[guest] = [row for doc in documents.values() for row in doc['services'].values()]
        self.assertEqual({guest: len(rows) for guest, rows in services.items()},
                         {'resolver-east': 2, 'resolver-west': 1, 'home-app': 1})
        home = services['home-app'][0]
        self.assertEqual(home['network_mode'], 'host')
        self.assertNotIn('cap_add', home)
        self.assertNotIn('entrypoint', home)
        self.assertNotIn('extra_hosts', home)
        self.assertEqual(home['volumes'], ['/srv/example/apps/homeassistant:/config'])
        self.assertEqual(home['pull_policy'], 'missing')

    def pihole(self):
        source = authored_config.read(ROOT / 'site.example.yaml')
        source['contexts']['lab']['timezone'] = 'Etc/UTC'
        guest = source['guests']['resolver']
        guest.update(lifecycle='retained', compose_projects={'shared': {'name': 'homelab-dns', 'file': 'compose.yml'}},
                     root_paths={'app-data': {'path': '/srv/homelab/data'}})
        source['apps'] = {'pihole': {'profile': 'pihole', 'guest': 'resolver', 'lifecycle': 'retained',
            'identity': {'phase': 'pihole', 'runtime_id': 'pihole', 'project': 'shared',
                         'services': {'pihole': 'pihole'}, 'networks': {}},
            'interfaces': {'service': {'interface': 'primary'}, 'upstream': {'interface': 'primary'}},
            'storage': {'config': {'root_path': 'app-data', 'subpath': 'pihole'}}}}
        source['connections'] = {'upstream': {'consumer': {'app': 'pihole', 'connection': 'upstream'},
            'target': {'external': 'resolver'}, 'source_interface': 'upstream'}}
        return source

    def test_pihole_only_uses_an_explicit_external_upstream_and_missing_binding_refuses(self):
        source = self.pihole()
        document = next(iter(self.compose(source).values()))
        self.assertEqual(set(document['services']), {'pihole'})
        self.assertEqual(document['services']['pihole']['environment']['FTLCONF_dns_upstreams'], '192.0.2.53#53')
        source['connections'] = {}
        with self.assertRaises(ValueError): self.plan(source)

    def test_retained_dns_optional_roles_preserve_modes_and_fresh_unbound_refuses_binds(self):
        source = self.pihole()
        source['apps']['pihole']['storage']['database'] = {'root_path': 'app-data', 'subpath': 'pihole/database'}
        source['apps']['unbound'] = {'profile': 'unbound', 'guest': 'resolver', 'lifecycle': 'retained',
            'identity': {'phase': 'unbound', 'runtime_id': 'unbound', 'project': 'shared',
                'services': {'unbound': 'unbound'}, 'networks': {'default': 'default'}},
            'interfaces': {'service': {'scope': 'guest-loopback'},
                           'private': {'scope': 'app-network', 'network': 'default'}},
            'storage': {'config': {'root_path': 'app-data', 'subpath': 'unbound'}}}
        selected = {'dev': ('dev', 'rw'), 'var': ('var', 'rw'),
                    'control_key': ('unbound_control.key', 'ro'),
                    'control_cert': ('unbound_control.pem', 'ro'),
                    'server_key': ('unbound_server.key', 'ro'),
                    'server_cert': ('unbound_server.pem', 'ro')}
        for role, (name, mode) in selected.items():
            source['apps']['unbound']['storage'][role] = {'root_path': 'app-data', 'subpath': 'unbound/' + name}
        document = next(iter(self.compose(source).values()))
        self.assertIn('/srv/homelab/data/pihole/database:/ftl-db:rw', document['services']['pihole']['volumes'])
        for name, mode in selected.values():
            self.assertIn('/srv/homelab/data/unbound/' + name + ':/opt/unbound/etc/unbound/' + name + ':' + mode,
                          document['services']['unbound']['volumes'])
        fresh = authored_config.read(ROOT / 'site.example.yaml')
        fresh['guests']['resolver']['root_paths'] = {'state': {'path': '/srv/example/unbound'}}
        fresh['apps']['recursive_dns']['storage'] = {'dev': {'root_path': 'state', 'subpath': 'dev'}}
        with self.assertRaises(ValueError): self.compose(fresh)

    def test_independent_pihole_and_unbound_share_project_and_preserve_actual_baseline(self):
        source = self.pihole()
        source['apps']['pihole']['interfaces']['upstream'] = {'scope': 'guest-loopback'}
        source['apps']['unbound'] = {'profile': 'unbound', 'guest': 'resolver', 'lifecycle': 'retained',
            'identity': {'phase': 'unbound', 'runtime_id': 'unbound', 'project': 'shared',
                'services': {'unbound': 'unbound'}, 'networks': {'default': 'default'}},
            'interfaces': {'service': {'scope': 'guest-loopback'},
                           'private': {'scope': 'app-network', 'network': 'default'}},
            'storage': {'config': {'root_path': 'app-data', 'subpath': 'unbound'}}}
        source['connections']['upstream'].update(target={'app': 'unbound', 'endpoint': 'dns_udp'}, readiness='start')
        document = next(iter(self.compose(source).values()))
        expected = json.loads((ROOT / 'tests/fixtures/dns-compose-baseline.json').read_text())
        self.assertEqual(document, expected)
        import component_runtime
        artifacts = component_runtime.artifacts(component_lower.runtime_config(self.plan(source), 'resolver'))
        self.assertIn('compose.yml', artifacts)
        manifest = json.loads(artifacts['component-projects.json'])
        self.assertEqual(manifest['homelab-dns']['file'], 'compose.yml')


if __name__ == '__main__':
    unittest.main()
