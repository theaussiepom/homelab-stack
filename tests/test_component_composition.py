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
import component_lower
import component_plan
import component_sources
from component_errors import ComponentError
import render
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]


class ComponentCompositionTests(unittest.TestCase):
    def test_complete_cloudflare_example_and_scalar_workflow_binding(self):
        import workflows
        import re, yaml
        value = component_sources.site(ROOT / 'examples/catalogue/edge-management.yaml')[0]
        page=(ROOT/'docs/examples/cloudflare-ingress.md').read_text()
        fragment=yaml.safe_load(re.findall(r'<!-- example: cloudflare-policy -->\n```yaml\n(.*?)```',page,re.S)[0])
        value['apps']['edge']['secrets'].update(fragment['apps']['edge']['secrets'])
        value['policies']['middlewares'].update(fragment['policies']['middlewares'])
        # RFC1918 addresses are test-only prerequisites, never public site allocations.
        value['policies']['middlewares']['trusted_clients']={'type':'ip-allow-list','ranges':['10.222.0.0/16']}
        value['policies']['middlewares']['headers']={'type':'default-headers'}
        value['secret_sources']['edge_origin_token']={'type':'file','path':'/run/example/retained-origin-token'}
        value['domains']={'manager':'manager.example.invalid'}
        value['policies']['tls']={'public':{'type':'acme','resolver':'letsencrypt'}}
        value['exposures']={'manager':{'type':'http','endpoint':{'app':'manager','endpoint':'web'},'domain':'manager',
            'ingress':{'app':'edge','endpoint':'https'},'tls':'public','middlewares':['cloudflare_public','headers']}}
        value['policies']['network']['proxy_backend']={'rules':[{'direction':'out','proto':'tcp',
            'destination':{'endpoint':'backend'},'port':{'endpoint':'backend'},'comment':'Selected proxy backend'}]}
        value['policies']['network']['proxy_client']={'rules':[{'direction':'in','proto':'tcp','source':{'endpoint':'proxy'},
            'destination':{'endpoint':'backend'},'port':{'endpoint':'backend'},'comment':'Selected reverse proxy'}]}
        value['guests']['edge']['network_policy'].append({'policy':'proxy_backend','endpoints':{'backend':{'app':'manager','endpoint':'web'}}})
        value['guests']['manager']['network_policy'].append({'policy':'proxy_client','endpoints':{
            'backend':{'app':'manager','endpoint':'web'},'proxy':{'app':'edge','endpoint':'https'}}})
        plan = self.plan(value)
        edge = plan.resolved['apps']['edge']
        self.assertTrue(edge['settings']['cloudflare'])
        self.assertEqual(edge['secret_bindings']['cloudflare_origin_token']['path'], '/run/example/retained-origin-token')
        routes = plan.resolved['routes']['edge']
        self.assertEqual(routes['manager']['middlewares'], ['cloudflare_public', 'headers'])
        runtime = component_lower.runtime_config(plan, 'edge')['applications']['edge']
        self.assertTrue({'cloudflare-origin-token', 'cloudflare.go', 'cloudflare-go.mod', 'cloudflare-LICENSE', 'cloudflare-manifest.yml'} <= set(runtime['runtime_files']['files']))
        value['secret_sources']['edge_origin_token'] = {'type': 'environment', 'name': 'ORIGIN_TOKEN', 'workflow_secret': 'ORIGIN_EDGE'}
        self.plan(value)
        models = workflows.models(ROOT, site_source=self.source)
        steps = models['guest-edge.yml']['jobs']['deploy']['steps']
        selected = [row for row in steps if row.get('with', {}).get('phase') == 'edge']
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['with']['traefik_cloudflare_origin_token'], '${{ secrets.ORIGIN_EDGE }}')
        self.assertTrue(models['deploy.yml']['on']['workflow_call']['secrets']['ORIGIN_EDGE']['required'])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name).resolve() / 'site.json'

    def plan(self, value):
        self.source.write_text(json.dumps(value))
        return component_plan.resolve(ROOT, self.source)

    def compose(self, value, guest='resolver'):
        return render.compositions(component_lower.runtime_config(self.plan(value), guest))

    def starter(self):
        return component_sources.site(ROOT / 'site.example.yaml')[0]

    def test_pegaprox_api_binding_checks_egress_without_configuring_cluster_or_scheduling(self):
        value = component_sources.site(ROOT / 'examples/catalogue/edge-management.yaml')[0]
        selected = self.plan(value)
        absent = copy.deepcopy(value)
        absent['connections'].pop('manager_provider')
        omitted = self.plan(absent)
        self.assertEqual(selected.resolved['apps']['manager']['resolved_connections']['proxmox']['target']['port'], 8006)
        self.assertEqual(omitted.resolved['apps']['manager']['resolved_connections'], {})
        self.assertEqual(selected.resolved['guest_dependencies'], omitted.resolved['guest_dependencies'])
        self.assertEqual(render.compositions(component_lower.runtime_config(selected, 'manager')),
                         render.compositions(component_lower.runtime_config(omitted, 'manager')))
        for change in ('missing-rule', 'wrong-api-port'):
            with self.subTest(change=change):
                broken = copy.deepcopy(value)
                if change == 'missing-rule':
                    broken['guests']['manager']['network_policy'] = [
                        row for row in broken['guests']['manager']['network_policy']
                        if row['policy'] != 'provider_api']
                else:
                    broken['policies']['network']['provider_api']['rules'][0]['port'] = '8443'
                with self.assertRaisesRegex(ComponentError, 'component.traffic-egress'):
                    self.plan(broken)

    def test_typed_example_sources_and_inline_bodies_resolve_to_the_same_composition(self):
        for name in ('site.example.yaml', 'examples/site.second.yaml'):
            with self.subTest(site=name):
                path = ROOT / name
                plan = component_plan.resolve(ROOT, path)
                inline, sources = component_sources.site(path)
                other = self.plan(inline)
                self.assertEqual(plan.resolved, other.resolved)
                self.assertEqual(plan.pins['site'], sources.pins)
                self.assertNotEqual(plan.pins['site'], other.pins['site'])
                self.assertEqual(len(sources.pins), 1 + len(inline['guests']) + len(inline['apps']))
                for guest in inline['guests']:
                    self.assertEqual(render.compositions(component_lower.runtime_config(plan, guest)),
                                     render.compositions(component_lower.runtime_config(other, guest)))

    def test_shared_address_group_replaces_only_the_repeated_literal_destinations(self):
        grouped = self.starter()
        literal = copy.deepcopy(grouped)
        del literal['address_groups']
        for name in ('downloads', 'recursive_dns'):
            for row in literal['policies']['network'][name]['rules']:
                self.assertEqual(row['destination'], {'address_group': 'internet'})
                row['destination'] = '0.0.0.0/0'
        for selected in literal['guests']['resolver']['network_policy']:
            if selected['policy'] in ('downloads', 'recursive_dns'):
                self.assertEqual(selected.pop('address_groups'), {'internet': 'internet'})
        grouped_plan, literal_plan = self.plan(grouped), self.plan(literal)
        resolved = copy.deepcopy(grouped_plan.resolved)
        self.assertEqual(resolved.pop('address_groups'), {'internet': ['0.0.0.0/0']})
        for selected in resolved['guests']['resolver']['network_policy']:
            if selected['policy'] in ('downloads', 'recursive_dns'):
                self.assertEqual(selected.pop('address_groups'), {'internet': 'internet'})
        self.assertEqual(resolved, literal_plan.resolved)
        self.assertEqual(self.compose(grouped), self.compose(literal))

    def test_group_composition_preserves_explicit_duplicates_and_requires_the_selected_binding(self):
        source = self.starter()
        source['address_groups']['test_targets'] = {
            'members': [{'network': 'services'}, '192.0.2.53', {'network': 'services'}]}
        source['address_groups']['internet'] = {'members': [{'address_group': 'test_targets'}]}
        plan = self.plan(source)
        rows = plan.resolved['guests']['resolver']['rules']
        downloads = [row for row in rows if row['comment'] == 'Package and image downloads']
        self.assertEqual([row['destination'] for row in downloads],
                         ['198.18.20.0/24', '192.0.2.53', '198.18.20.0/24'])
        self.assertEqual(plan.resolved['guest_dependencies']['resolver'], [])
        del source['guests']['resolver']['network_policy'][1]['address_groups']
        with self.assertRaises(ValueError):
            self.plan(source)

    def test_main_starter_selects_only_one_independent_unbound(self):
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

    def test_unbound_loopback_binding_succeeds_and_physical_nic_binding_refuses(self):
        source = self.starter()
        app = self.plan(source).resolved['apps']['recursive_dns']
        self.assertEqual(app['listeners']['dns_tcp']['publication_address'], '127.0.0.1')
        source['apps']['recursive_dns']['interfaces']['service'] = {'interface': 'primary'}
        with self.assertRaises(ValueError): self.plan(source)

    def test_repeated_profile_has_distinct_runtime_and_publication_with_cosmetic_labels(self):
        source = self.starter()
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
        source = self.starter()
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
        fresh = self.starter()
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
