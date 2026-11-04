"""Compile declared admin capabilities without contacting brokers or databases."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
spec = importlib.util.spec_from_file_location('managed_administration_compiler', FRAMEWORK / 'blueprints/compile.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0, str(FRAMEWORK / 'proxmox/applications'))
import render
import service_bindings
import connections
import cloudbeaver


class ManagedAdministrationTests(unittest.TestCase):
    def packets(self, site='site.example.json', disabled=None):
        return c.compile_stack(ROOT, c.read(ROOT / site), disabled or [])

    def test_explorer_has_only_the_authenticated_gateway_listener(self):
        for path in ('site.example.json', 'examples/site.second.json'):
            with self.subTest(site=path):
                site = c.read(ROOT / path)
                packet = self.packets(path)['mqtt']
                cfg = json.loads(packet['files']['site.json'])
                stack = json.loads(packet['files']['stack.json'])
                compose = render.compose(stack)
                self.assertEqual(set(compose['services']), {'mqtt', 'mqtt_explorer', 'explorer_gateway'})
                explorer = compose['services']['mqtt_explorer']
                gateway = compose['services']['explorer_gateway']
                self.assertNotIn('ports', explorer)
                self.assertNotEqual(explorer.get('network_mode'), 'host')
                self.assertEqual(explorer['user'], '1001:1001')
                self.assertEqual(explorer['cap_drop'], ['ALL'])
                self.assertTrue(explorer['read_only'])
                self.assertEqual(explorer['environment']['MQTT_EXPLORER_SKIP_AUTH'], 'true')
                self.assertFalse(any('API_KEY' in key or 'AUTO_CONNECT' in key for key in explorer['environment']))
                self.assertEqual(explorer['volumes'][0]['source'], '/srv/homelab/data/mqtt-explorer')
                self.assertEqual(gateway['ports'], [site['values']['addresses.mqtt_backend'] + ':80:4180'])
                self.assertEqual(gateway['user'], '65532:65532')
                self.assertEqual(gateway['image'], c.read(ROOT / 'images.json')['traefik']['repository'] + '@' + c.read(ROOT / 'images.json')['traefik']['digest'])
                self.assertEqual(sum(service['memory_mib'] for service in stack['services'].values()), 640)
                self.assertEqual(stack['guest_memory_mib'], 1024)
                self.assertEqual(cfg['routes']['mqtt-explorer']['host'], site['values']['domains.mqtt_explorer'])
                self.assertEqual(cfg['routes']['mqtt-explorer']['middlewares'], ['security-headers'])

    def test_saved_broker_connection_is_distinct_from_the_existing_probe(self):
        for path in ('site.example.json', 'examples/site.second.json'):
            site = c.read(ROOT / path)
            packet = self.packets(path)['mqtt']
            cfg = json.loads(packet['files']['site.json'])
            stack = json.loads(packet['files']['stack.json'])
            selected = stack['mqtt_explorer']['broker_connection']
            self.assertEqual(selected['hostname'], site['values']['hostnames.mqtt_broker'])
            self.assertEqual(selected['port'], 1883)
            self.assertEqual(selected['username'], site['values']['accounts.mqtt_explorer'])
            self.assertEqual(selected['credential_id'], site['values']['credentials.mqtt_explorer'])
            self.assertEqual(Path(selected['credential_file']).name, 'managed-' + selected['credential_id'] + '.json')
            self.assertNotEqual(selected['credential_file'], stack['mqtt']['credential_file'])
            self.assertEqual(selected['password_file'], site['values']['paths.mqtt_password_file'])
            self.assertEqual(selected['access'], 'read-write-all')
            self.assertEqual(cfg['app']['service_connections']['mqtt_explorer'], {'service': 'mqtt.mqtt', 'address': 'backend'})
            configurations = {name: json.loads(row['files']['site.json']) for name, row in self.packets(path).items()}
            self.assertFalse(any(edge.source == edge.target == 'mqtt' for edge in service_bindings.connections_for(configurations)))

    def test_optional_gui_does_not_change_the_retained_broker_compose(self):
        packet = self.packets()['mqtt']
        stack = json.loads(packet['files']['stack.json'])
        legacy = copy.deepcopy(stack)
        legacy.pop('mqtt_explorer')
        for name in ('mqtt_explorer', 'explorer_gateway'):
            legacy['services'].pop(name)
        self.assertEqual(render.compose(stack)['services']['mqtt'], render.compose(legacy)['services']['mqtt'])

    def test_explorer_broker_alias_follows_the_selected_endpoint_not_the_gui_listener(self):
        for path in ('site.example.json', 'examples/site.second.json'):
            with self.subTest(site=path):
                site = c.read(ROOT / path)
                packet = self.packets(path)['mqtt']
                cfg = json.loads(packet['files']['site.json'])
                stack = json.loads(packet['files']['stack.json'])
                compose = render.compose(stack)
                binding = cfg['app']['service_connections']['mqtt_explorer']
                publication = cfg['app']['published_services'][binding['service'].split('.')[1]]
                address = publication['addresses'][binding['address']]
                hostname = stack['mqtt_explorer']['broker_connection']['hostname']
                self.assertNotEqual(address, publication['addresses'][publication['dns_address']])
                self.assertEqual(stack['mqtt_explorer']['broker_address'], address)
                self.assertEqual(compose['services']['mqtt_explorer']['extra_hosts'], {hostname: address})
                self.assertNotIn('extra_hosts', compose['services']['explorer_gateway'])

                # Select another assigned address without moving the GUI listener,
                # the broker, its public DNS record or its saved native profile.
                alternative = site['values']['addresses.mqtt_management']
                self.assertNotIn(alternative, (address, publication['addresses'][publication['dns_address']]))
                changed = c.merge(site, {'guests': {'mqtt': {'config': {'app': {
                    'published_services': {'mqtt': {'addresses': {'explorer-local': alternative}}},
                    'service_connections': {'mqtt_explorer': {'address': 'explorer-local'}},
                }}}}})
                next_packet = c.compile_stack(ROOT, changed, [])['mqtt']
                next_stack = json.loads(next_packet['files']['stack.json'])
                next_compose = render.compose(next_stack)
                self.assertNotEqual(alternative, next_stack['mqtt_explorer']['bind_address'])
                self.assertEqual(next_stack['mqtt_explorer']['broker_address'], alternative)
                expected = copy.deepcopy(compose)
                expected['services']['mqtt_explorer']['extra_hosts'] = {hostname: alternative}
                self.assertEqual(next_compose, expected)
                slot = '/var/lib/homelab-inputs/ordinary/mqtt/'
                before = json.dumps(stack['mqtt_explorer']['broker_connection']).replace(slot + packet['identity'], '${inputs}')
                after = json.dumps(next_stack['mqtt_explorer']['broker_connection']).replace(slot + next_packet['identity'], '${inputs}')
                self.assertEqual(json.loads(after), json.loads(before))

    def test_local_explorer_health_does_not_wait_for_identity_or_ingress(self):
        selected = self.packets(disabled=['identity', 'db-tools', 'ingress', 'bitwarden', 'music', 'monitoring'])
        mqtt = json.loads(selected['mqtt']['files']['site.json'])
        self.assertTrue(selected['mqtt']['enabled'])
        self.assertEqual(c.manifest(ROOT)['guests']['mqtt']['depends_on'], ['dns'])
        self.assertEqual(list(mqtt['app']['service_health_checks']), ['mqtt', 'mqtt_explorer'])
        self.assertEqual(mqtt['app']['service_health_checks']['mqtt'][0]['argv'][-1], 'mqtt-broker')
        checks = mqtt['app']['service_health_checks']['mqtt_explorer']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['argv'], ['python3', '/usr/local/bin/homelab-mqtt-explorer.py', 'health', '--config', '/opt/homelab-app/runtime/mqtt-explorer-public.json'])
        self.assertEqual(checks[0]['expect'], '"mqtt_explorer": "passed"')
        self.assertFalse(any('https://' in argument or '9000' in argument for check in checks for argument in check['argv']))

    def test_dedicated_admin_connections_keep_original_metadata_and_consumer_identity(self):
        for path in ('site.example.json', 'examples/site.second.json'):
            site = c.read(ROOT / path)
            packets = self.packets(path)
            cloud = json.loads(packets['db-tools']['files']['stack.json'])['cloudbeaver']
            self.assertEqual(set(cloud['connections']), {'postgresql', 'mariadb'})
            self.assertEqual(cloud['connections']['postgresql']['sslmode'], 'prefer')
            self.assertEqual(set(cloud['managed_connections']), {'postgresql-admin', 'mariadb-admin'})
            for engine in ('postgresql', 'mariadb'):
                profile = c.read(ROOT / 'guests' / engine / 'profile.json')
                raw = profile['config']['app']['database_administrators']['cloudbeaver-' + engine + '-admin']
                self.assertEqual(raw['source_guest'], 'db-tools')
                self.assertEqual(raw['access'], 'server-administration')
                self.assertEqual(raw['transport'], 'tls')
                self.assertEqual(raw['username'], '${accounts.' + engine + '_admin}')
                self.assertEqual(raw['credential_file'], '${inputs}/managed-${credentials.' + engine + '_admin}.json')
                selected = cloud['managed_connections'][engine + '-admin']
                self.assertEqual(selected['account_id'], 'cloudbeaver-' + engine + '-admin')
                self.assertEqual(selected['driver'], engine)
                self.assertEqual(selected['database'], 'postgres' if engine == 'postgresql' else '')
                self.assertNotIn('password', selected)
                cfg = json.loads(packets[engine]['files']['site.json'])
                self.assertIsNone(profile['stack'])
                self.assertEqual(cfg['guest']['vmid'], site['values']['vmids.' + engine])
                self.assertEqual(cfg['guest']['interfaces'][1]['ipv4'].split('/')[0], site['values']['addresses.' + engine + '_backend'])

    def test_new_credential_and_hostname_bindings_are_explicit_and_site_specific(self):
        keys = {'domains.mqtt_explorer', 'accounts.mqtt_explorer', 'accounts.postgresql_admin', 'accounts.mariadb_admin', 'credentials.mqtt_explorer', 'credentials.postgresql_admin', 'credentials.mariadb_admin', 'paths.mqtt_password_file'}
        declarations = c.manifest(ROOT)['required_site_bindings']
        a, b = [c.read(ROOT / path) for path in ('site.example.json', 'examples/site.second.json')]
        for key in keys:
            self.assertEqual(declarations[key], 'string')
            self.assertNotEqual(a['values'][key], b['values'][key])
            missing = copy.deepcopy(a)
            missing['values'].pop(key)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'declared site binding type'):
                c.compile_stack(ROOT, missing, [])

    def test_managed_mariadb_uses_one_pinned_read_only_jdbc_artifact(self):
        declared = c.read(ROOT / 'guests/db-tools/profile.json')['stack']['cloudbeaver']['mariadb_jdbc']
        self.assertEqual(declared, {
            'version': '3.5.11',
            'sha256': '42604178b9e57ec08ee0035079961516f086e455d0141f0b22c6eff29fb2fff4',
            'image_filename': 'mariadb-java-client-3.5.10.jar',
        })
        for path in ('site.example.json', 'examples/site.second.json'):
            with self.subTest(site=path):
                stack = json.loads(self.packets(path)['db-tools']['files']['stack.json'])
                self.assertEqual(stack['cloudbeaver']['mariadb_jdbc'], declared)
                artifact = cloudbeaver.jdbc(stack['cloudbeaver'])
                self.assertEqual(artifact['url'], 'https://repo.maven.apache.org/maven2/org/mariadb/jdbc/mariadb-java-client/3.5.11/mariadb-java-client-3.5.11.jar')
                server = render.compose(stack)['services']['cloudbeaver']
                mounts = [row for row in server['volumes'] if row['target'].startswith('/opt/cloudbeaver/drivers/')]
                self.assertEqual(mounts, [{
                    'type': 'bind',
                    'source': '/opt/homelab-app/runtime/mariadb-java-client-3.5.11.jar',
                    'target': '/opt/cloudbeaver/drivers/mariadb/mariadb-java-client-3.5.10.jar',
                    'read_only': True, 'bind': {'create_host_path': False},
                }])
                self.assertEqual(server['healthcheck']['test'][-3:], [declared['version'], declared['sha256'], declared['image_filename']])
                self.assertEqual(server['healthcheck']['test'][-4], '--postgresql')
                maria_only = copy.deepcopy(stack)
                maria_only['cloudbeaver']['managed_connections'].pop('postgresql-admin')
                self.assertNotIn('--postgresql', render.compose(maria_only)['services']['cloudbeaver']['healthcheck']['test'])
                self.assertEqual(server['image'], 'dbeaver/cloudbeaver:26.2.3@sha256:a537c60a7ca98d8d791c11c01172c1354e8dedfe222d04a54795ceeb32f12bbc')

    def test_managed_mariadb_refuses_missing_or_unbounded_jdbc_declarations(self):
        stack = json.loads(self.packets()['db-tools']['files']['stack.json'])
        changed = copy.deepcopy(stack)
        changed['cloudbeaver'].pop('mariadb_jdbc')
        with self.assertRaisesRegex(ValueError, 'fixed MariaDB JDBC artifact'):
            render.compose(changed)
        for key, value in [('version', '3.5.10'), ('sha256', 'unverified'),
                           ('image_filename', '../mariadb.jar'),
                           ('image_filename', 'other-driver.jar'),
                           ('url', 'https://alternate.example.invalid/driver.jar')]:
            changed = copy.deepcopy(stack)
            changed['cloudbeaver']['mariadb_jdbc'][key] = value
            with self.subTest(field=key, value=value), self.assertRaisesRegex(ValueError, 'fixed vendor JDBC artifact'):
                render.compose(changed)

    def test_jdbc_override_is_absent_without_a_managed_mariadb_connection(self):
        original = json.loads(self.packets()['db-tools']['files']['stack.json'])
        for managed in ({}, {'postgresql-admin': original['cloudbeaver']['managed_connections']['postgresql-admin']}):
            stack = copy.deepcopy(original)
            if managed:
                stack['cloudbeaver']['managed_connections'] = managed
            else:
                stack['cloudbeaver'].pop('managed_connections')
            with self.subTest(managed=list(managed)), self.assertRaisesRegex(ValueError, 'fixed MariaDB JDBC artifact'):
                render.compose(stack)
            stack['cloudbeaver'].pop('mariadb_jdbc')
            self.assertIsNone(cloudbeaver.jdbc(stack['cloudbeaver']))
            server = render.compose(stack)['services']['cloudbeaver']
            self.assertFalse(any(row['target'].startswith('/opt/cloudbeaver/drivers/') for row in server['volumes']))
            self.assertEqual('--postgresql' in server['healthcheck']['test'], bool(managed))
            if managed:
                self.assertEqual(server['healthcheck']['test'][-1], '--postgresql')

    def test_admin_owners_and_postgresql_hba_follow_existing_interfaces(self):
        for path in ('site.example.json', 'examples/site.second.json'):
            site = c.read(ROOT / path)
            packets = self.packets(path)
            cloud = json.loads(packets['db-tools']['files']['stack.json'])['cloudbeaver']
            for engine, source_key in [('postgresql', 'addresses.pgadmin_postgresql'), ('mariadb', 'addresses.db_tools_mariadb')]:
                cfg = json.loads(packets[engine]['files']['site.json'])
                account = cfg['app']['database_administrators']['cloudbeaver-' + engine + '-admin']
                owner = {'node': site['values']['site.node'], 'engine': engine, 'database_vmid': site['values']['vmids.' + engine], 'source_vmid': site['values']['vmids.db-tools'], 'server_address': site['values']['addresses.' + engine + '_backend'], 'source_address': site['values'][source_key], 'username': site['values']['accounts.' + engine + '_admin'], 'purpose': 'database-administration'}
                self.assertEqual(account['owner'], owner)
                selected = cloud['managed_connections'][engine + '-admin']
                self.assertEqual(selected['owner'], owner)
                self.assertEqual(selected['host'], owner['server_address'])
                self.assertEqual(selected['username'], account['username'])
                self.assertEqual(selected['credential_id'], account['credential_id'])
                self.assertEqual(Path(selected['credential_file']).name, Path(account['credential_file']).name)
                self.assertEqual(selected['transport'], 'tls')
            hba = packets['postgresql']['files']['pg_hba.conf']
            original = c.read(ROOT / 'guests/postgresql/profile.json')['files']['pg_hba.conf']
            for key, value in site['values'].items():
                if isinstance(value, str):
                    original = original.replace('${' + key + '}', value)
            user = site['values']['accounts.postgresql_admin']
            source = site['values']['addresses.pgadmin_postgresql']
            prefix = '# homelab managed administrator accounts\n' + f'hostssl all,replication {user} {source}/32 scram-sha-256\nlocal all,replication {user} reject\nhost all,replication {user} 0.0.0.0/0 reject\nhost all,replication {user} ::/0 reject\n'
            self.assertEqual(hba, prefix + original)

    def test_new_routes_require_the_exact_existing_backend_connection(self):
        for role, direction, port in [('mqtt', 'in', '80'), ('ingress', 'out', '80')]:
            site = c.read(ROOT / 'site.example.json')
            packets = c.compile_stack(ROOT, site, [])
            cfg = json.loads(packets[role]['files']['site.json'])
            rules = cfg['guest']['rules']
            flow = connections.Connection('ingress', 'mqtt', site['values']['addresses.ingress_backend'], site['values']['addresses.mqtt_backend'], 'tcp', int(port))
            narrow = {'direction': direction, 'proto': 'tcp', 'port': port, 'source': flow.source_address + '/32', 'destination': flow.target_address + '/32', 'interface': 'net1', 'comment': 'Traefik to the authenticated MQTT Explorer gateway'}
            self.assertIn(narrow, rules)
            # Existing package-download egress also admits TCP80. Remove every
            # actually matching allowance in this negative fixture, rather than
            # assuming the newly declared narrow rule is its sole permission.
            denied = [row for row in rules if not connections.permits([row], direction, flow, 'net1')]
            self.assertFalse(connections.permits(denied, direction, flow, 'net1'))
            site['guests'][role] = {'config': {'guest': {'rules': denied}}}
            with self.subTest(role=role), self.assertRaisesRegex(ValueError, role + ' ' + direction + ' firewall'):
                c.compile_stack(ROOT, site, [])

    def test_disabled_db_tools_remains_a_valid_leaf_with_declared_admin_source_closure(self):
        packets = self.packets(disabled=['db-tools'])
        self.assertFalse(packets['db-tools']['enabled'])
        self.assertTrue(packets['postgresql']['enabled'])
        self.assertTrue(packets['mariadb']['enabled'])
        self.assertTrue(packets['mqtt']['enabled'])
        self.assertEqual(len(packets), 13)
        monitoring_site = c.read(ROOT / 'site.example.json')
        monitoring_site['zabbix'] = None
        self.assertEqual(len(c.compile_stack(ROOT, monitoring_site, ['db-tools'])), 14)


if __name__ == '__main__':
    unittest.main()
