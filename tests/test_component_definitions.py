"""Library definition units, with framework app contracts mocked at their boundary.

These test authored selections and component ownership, not the framework's
validator failure matrix. Real compiler/lowerer/renderer cases live separately.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints'), str(FRAMEWORK / 'proxmox/applications')]
import component_adapters
import component_foundations
import component_properties
import component_sources
import component_types
import component_backup
# Do not let imports of the selected framework change stack discovery precedence.
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]


class ProfileDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library, cls.sources = component_sources.library(ROOT)

    def profile(self, name, adapter=None):
        value = copy.deepcopy(self.library['app_profiles'][name])
        expected = adapter or name
        self.assertEqual(value['adapter'], expected)
        owner = component_adapters.adapter(expected)
        with mock.patch.object(component_types, 'adapter', return_value=owner) as contract, \
             mock.patch.object(component_foundations, 'validate') as foundations, \
             mock.patch.object(component_properties, 'validate') as properties, \
             mock.patch.object(component_backup, 'application') as backup:
            component_types.profile(value)
        contract.assert_called_once_with(expected)
        backup.assert_called_once_with(value['backup'], value.get('storage', {}))
        selected = foundations if expected in component_foundations.OWNED else properties
        selected.assert_called_once_with(expected, value.get('properties', {}), partial=True)
        self.assertEqual(value['health']['ready']['profile'], 'adapter-ready')
        self.assertTrue(set(value.get('software', [])) <= set(self.library['software']))
        self.assertTrue(set(value.get('runtime', [])) <= set(self.library['runtime_profiles']))
        return value

    def test_homeassistant_integrations_and_mdns_are_optional(self):
        value = self.profile('homeassistant')
        self.assertEqual(set(value['connections']), {'recorder', 'metrics', 'broker'})
        self.assertTrue(all(row['required'] is False for row in value['connections'].values()))
        self.assertNotIn('homeassistant-mdns', value['runtime'])
        self.assertFalse(value['interfaces']['home']['required'])
        self.assertNotIn('cap_add', self.library['runtime_profiles']['homeassistant']['containers']['homeassistant'])
        self.assertEqual(self.library['runtime_profiles']['homeassistant-mdns']['containers']['homeassistant']['cap_add'], ['NET_ADMIN'])

    def test_public_homeassistant_selects_explicit_public_software_only(self):
        value = self.profile('homeassistant-public', 'homeassistant')
        self.assertIn('homeassistant-public-images', value['software'])
        self.assertNotIn('homeassistant-images', value['software'])
        self.assertFalse(value['storage']['startup']['required'])
        self.assertEqual(value['storage']['config']['initialize'],
                         {'type': 'directory', 'uid': 0, 'gid': 0, 'mode': '0700'})
        self.assertNotIn('initialize', self.library['app_profiles']['homeassistant']['storage']['config'])
        self.assertTrue(all(row['required'] is False for row in value['connections'].values()))

    def test_retained_node_red_owns_settings_wrapper_and_optional_api_capability(self):
        value = self.profile('node_red')
        self.assertEqual(value['authentication'], 'node-red-retained-oidc')
        self.assertTrue(value['storage']['config']['required'])
        self.assertTrue(value['storage']['settings']['read_only'])
        self.assertFalse(value['secrets']['api_token']['required'])
        self.assertFalse(value['connections']['broker']['required'])

    def test_public_node_red_has_data_without_retained_oidc_or_config_wrapper(self):
        value = self.profile('node_red-public', 'node_red')
        self.assertEqual(set(value['storage']), {'data'})
        self.assertNotIn('authentication', value)
        self.assertNotIn('secrets', value)
        self.assertIn('node_red-public-images', value['software'])
        self.assertNotIn('node_red-images', value['software'])
        self.assertEqual(value['storage']['data']['initialize'],
                         {'type': 'directory', 'uid': 1000, 'gid': 1000, 'mode': '0700'})
        self.assertTrue(all('initialize' not in row for row in self.library['app_profiles']['node_red']['storage'].values()))

    def test_bitwarden_owns_its_private_listener_and_explicit_environment_requirement(self):
        value = self.profile('bitwarden')
        self.assertEqual(value['listeners']['web']['namespace'], 'app-network')
        self.assertEqual(value['storage']['data']['target'], '/etc/bitwarden')
        self.assertTrue(value['connections']['database']['required'])
        self.assertTrue(value['secrets']['runtime_environment']['required'])
        self.assertEqual(value.get('properties', {}), {})
        self.assertEqual(self.library['software']['bitwarden-images'],
                         {'images': {'bitwarden': 'bitwarden'}})
        self.assertEqual(json.loads((ROOT / 'images.json').read_text())['bitwarden'], {
            'repository': 'ghcr.io/bitwarden/lite', 'tag': None,
            'digest': 'sha256:94484fe9382df51ad755151ea360663e922e60a32385500454dd1f38045bf6a6'})

    def test_cloudbeaver_helpers_and_database_roles_do_not_require_identity_readiness(self):
        value = self.profile('cloudbeaver')
        self.assertEqual({row['service'] for row in value['listeners'].values()}, {'cloudbeaver', 'auth_gateway'})
        self.assertEqual(value['authentication'], 'cloudbeaver-oidc')
        self.assertNotIn('identity', value['connections'])
        self.assertTrue(all(not row['required'] for row in value['connections'].values()))
        self.assertEqual(value['connections']['postgresql-admin']['accounts'], ['postgresql-admin'])
        self.assertEqual(value['connections']['mariadb-admin']['accounts'], ['mariadb-admin'])
        self.assertEqual(value['storage']['workspace']['initialize'],
                         {'type': 'directory', 'uid': 8978, 'gid': 8978, 'mode': '0700'})

    def test_managed_maria_cloudbeaver_variant_owns_one_explicit_vendor_driver_declaration(self):
        value = self.profile('cloudbeaver-mariadb-admin', 'cloudbeaver')
        self.assertTrue(value['connections']['mariadb-admin']['required'])
        self.assertEqual(value['properties']['mariadb_jdbc'], {
            'version': '3.5.11',
            'sha256': '42604178b9e57ec08ee0035079961516f086e455d0141f0b22c6eff29fb2fff4',
            'image_filename': 'mariadb-java-client-3.5.10.jar'})
        generic = self.library['app_profiles']['cloudbeaver']
        self.assertNotIn('mariadb_jdbc', generic.get('properties', {}))
        self.assertEqual(value['software'], generic['software'])
        self.assertEqual(value['runtime'], generic['runtime'])
        self.assertEqual(value['authentication'], generic['authentication'])
        self.assertEqual(value['storage'], generic['storage'])

    def test_pihole_requires_explicit_upstream_and_not_an_unbound_bundle(self):
        value = self.profile('pihole')
        self.assertEqual(value['connections']['upstream']['type'], 'dns')
        self.assertTrue(value['connections']['upstream']['required'])
        self.assertEqual({row['service'] for row in value['listeners'].values()}, {'pihole'})
        self.assertIn('guest-loopback', value['interfaces']['upstream']['accepts'])
        self.assertFalse(value['interfaces']['upstream']['required'])
        self.assertEqual(value['storage']['database'], {'target': '/ftl-db', 'read_only': False, 'required': False, 'kind': 'directory'})
        self.assertEqual(self.library['runtime_profiles']['pihole']['containers']['pihole']['memory_mib'], 256)

    def test_unbound_owns_only_itself_with_optional_fresh_config_and_two_protocols(self):
        value = self.profile('unbound')
        self.assertEqual(value['interfaces']['service']['accepts'], ['guest-loopback'])
        self.assertEqual(value['properties'], {'publish_port': 5335})
        self.assertFalse(value['storage']['config']['required'])
        self.assertEqual(value['connections'], {})
        self.assertEqual({row['protocol'] for row in value['listeners'].values()}, {'tcp', 'udp'})
        self.assertEqual({row['port'] for row in value['listeners'].values()}, {53})
        expected = {
            'dev': ('dev', False, 'directory'), 'var': ('var', False, 'directory'),
            'control_key': ('unbound_control.key', True, 'file'),
            'control_cert': ('unbound_control.pem', True, 'file'),
            'server_key': ('unbound_server.key', True, 'file'),
            'server_cert': ('unbound_server.pem', True, 'file')}
        self.assertEqual(set(value['storage']), {'config', *expected})
        for role, (name, read_only, kind) in expected.items():
            self.assertEqual(value['storage'][role], {'target': '/opt/unbound/etc/unbound/' + name,
                'read_only': read_only, 'required': False, 'kind': kind})

    def test_authentik_supporting_services_and_secret_requirements_are_owned(self):
        value = self.profile('authentik')
        self.assertEqual(component_adapters.adapter('authentik')['services'], ('server', 'worker', 'redis'))
        self.assertTrue(value['connections']['database']['required'])
        self.assertEqual(value['secrets'], {'secret_key': {'required': True},
            'postgresql_password': {'required': True}, 'smtp_password': {'required': False}})

    def test_influxdb_native_reservation_is_explicit_and_has_no_container_image(self):
        value = self.profile('influxdb')
        self.assertEqual(value['runtime'], ['native-influxdb'])
        self.assertEqual(self.library['runtime_profiles']['native-influxdb'], {'native': {'memory_mib': 1792}})
        self.assertNotIn('images', self.library['software']['influxdb'])
        self.assertEqual(value['storage']['data']['target'], '/var/lib/influxdb')

    def test_traefik_dashboard_is_internal_and_off_unless_explicitly_selected(self):
        value = self.profile('traefik')
        self.assertEqual(value['properties'], {'dashboard': False})
        self.assertEqual(value['endpoints']['dashboard'], {'internal': 'dashboard'})
        self.assertNotIn(8080, {row['port'] for row in value['listeners'].values()})
        self.assertTrue(all(row['required'] is False for row in value['secrets'].values()))

    def test_mariadb_native_package_account_has_an_explicit_admission_cost(self):
        value = self.profile('mariadb')
        self.assertEqual(value['runtime'], ['native-mariadb'])
        self.assertEqual(self.library['runtime_profiles']['native-mariadb'], {'native': {'memory_mib': 768}})
        self.assertNotIn('images', self.library['software']['mariadb'])
        self.assertNotIn('server_id', value.get('properties', {}))

    def test_zabbix_owns_web_server_and_optional_saml_requirement(self):
        value = self.profile('zabbix')
        self.assertEqual(value['authentication'], 'zabbix-saml')
        self.assertFalse(self.library['authentication_profiles']['zabbix-saml']['required'])
        self.assertFalse(value['secrets']['database_password']['required'])
        self.assertEqual(value['listeners']['web']['service'], value['listeners']['local_web']['service'])
        self.assertEqual(value['listeners']['web']['port'], value['listeners']['local_web']['port'])
        self.assertEqual(value['listeners']['local_web']['publish'], {'scope': 'guest-loopback', 'port': 8081})
        self.assertEqual(value['connections']['metrics'], {'type': 'influxdb', 'required': False})

    def test_mqtt_native_listener_is_not_a_gui_dependency_or_new_auth_manager(self):
        value = self.profile('mqtt')
        self.assertEqual({row['service'] for row in value['listeners'].values()}, {'mqtt'})
        self.assertEqual(value['connections'], {})
        self.assertEqual(value['listeners']['mqtt']['bind'], 'wildcard')
        self.assertEqual(value['listeners']['mqtt']['port'], 1883)
        self.assertNotIn('password_file', value.get('properties', {}))
        self.assertEqual(value['secrets'], {'probe': {'required': False}})

    def test_explorer_keeps_private_app_gateway_and_explicit_broker_and_outpost(self):
        value = self.profile('mqtt_explorer')
        self.assertEqual({row['service'] for row in value['listeners'].values()}, {'mqtt_explorer', 'explorer_gateway'})
        self.assertTrue(value['connections']['broker']['required'])
        self.assertEqual(value['connections']['broker']['accounts'], ['mqtt-client'])
        self.assertEqual(value['connections']['outpost'], {'type': 'http', 'required': True})
        self.assertEqual(value['storage']['data']['target'], '/app/data')
        self.assertEqual(value['storage']['data']['initialize'],
                         {'type': 'directory', 'uid': 1001, 'gid': 1001, 'mode': '0700'})

    def test_music_listener_and_health_source_use_the_same_explicit_player_role(self):
        value = self.profile('music_assistant')
        self.assertEqual({row['interface'] for row in value['listeners'].values()}, {'web'})
        self.assertEqual({row['port'] for row in value['listeners'].values()}, {8095, 8097})
        self.assertEqual(value['health']['ready']['source_interface'], 'web')
        self.assertEqual(value['storage']['data']['target'], '/data')
        self.assertNotIn('automation', value['connections'])

    def test_pegaprox_declares_rootfs_compatible_data_and_omits_unneeded_curl(self):
        value = self.profile('pegaprox')
        self.assertEqual(value['connections'], {'proxmox': {'type': 'https', 'required': False}})
        self.assertEqual({row['target'] for row in value['storage'].values()}, {'/app/config', '/app/logs'})
        self.assertNotIn('curl', value['software'])
        self.assertTrue(value['secrets']['database_key']['required'])
        self.assertEqual(self.library['runtime_profiles']['pegaprox']['requirements'], {'os_reserve_mib': 512})

    def test_postgresql_native_source_has_no_inferred_remote_grants_or_container_image(self):
        value = self.profile('postgresql')
        self.assertEqual(value['runtime'], ['native-postgresql'])
        self.assertEqual(self.library['runtime_profiles']['native-postgresql'], {'native': {'memory_mib': 1792}})
        self.assertNotIn('images', self.library['software']['postgresql'])
        self.assertNotIn('client_access', value.get('properties', {}))

    def test_zigbee_coordinator_requirement_does_not_belong_to_winet(self):
        value = self.profile('zigbee2mqtt')
        self.assertEqual(value['devices'], {'coordinator': {'type': 'serial', 'required': True}})
        self.assertTrue(value['connections']['broker']['required'])
        self.assertNotIn('winet', {row['service'] for row in value['listeners'].values()})

    def test_winet_requires_options_and_typed_broker_inverter_without_usb(self):
        value = self.profile('winet')
        self.assertEqual(value.get('devices', {}), {})
        self.assertEqual(set(value['connections']), {'broker', 'inverter'})
        self.assertTrue(all(row['required'] for row in value['connections'].values()))
        self.assertTrue(value['secrets']['options']['required'])


class SharedDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library, cls.sources = component_sources.library(ROOT)

    def test_registered_independent_adapters_public_variants_and_no_implicit_guest_graph(self):
        self.assertEqual(len(self.library['app_profiles']), 25)
        self.assertEqual({v['adapter'] for v in self.library['app_profiles'].values()}, set(component_adapters.ADAPTERS))
        self.assertFalse({'guests', 'default_enabled', 'required_site_bindings'} & set(self.library))
        self.assertEqual(set(self.library['guest_templates']), {'base', 'docker'})

    def test_image_catalogue_has_only_current_named_software_owners(self):
        images = json.loads((ROOT / 'images.json').read_text())
        referenced = {image for software in self.library['software'].values()
                      for image in software.get('images', {}).values()}
        self.assertEqual(set(images), referenced)

    def test_templates_explicit_reserve_and_common_docker_packages(self):
        for name, value in self.library['guest_templates'].items():
            with self.subTest(template=name):
                component_types.template(value)
                self.assertEqual(value['resources']['os_reserve_mib'], 256)
                self.assertTrue(value['security']['unprivileged'])
                self.assertTrue(value['security']['protection'])
                self.assertFalse(value['security']['keyctl'])
        self.assertEqual(self.library['software']['docker']['packages'], [
            'docker.io=26.1.5+dfsg1-9+deb13u1', 'docker-cli=26.1.5+dfsg1-9+deb13u1', 'docker-compose=2.26.1-4'])

    def test_public_vendor_assets_keep_exact_declared_bytes(self):
        index = json.loads((ROOT / 'stack.json').read_text())
        self.assertEqual(set(index['assets']), {'postgresql-repository-key', 'mariadb-repository-key', 'influxdb-repository-key', 'proxmox-backup-repository-key'})
        for name, value in index['assets'].items():
            with self.subTest(asset=name):
                raw = (ROOT / value['source']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), value['sha256'])
                self.assertTrue(raw.startswith(b'-----BEGIN PGP PUBLIC KEY BLOCK-----\n'))
                self.assertNotIn(b'${', raw)
        self.assertEqual(self.library['health_profiles'], {'adapter-ready': {'type': 'adapter', 'check': 'readiness'}})

    def test_monitoring_declarations_are_typed_workloads_and_only_root_feature_activates_them(self):
        self.assertEqual(self.library['monitoring_profiles'], {
            'linux-agent': {'type': 'zabbix-agent', 'profiles': ['linux']},
            'docker-agent': {'type': 'zabbix-agent', 'profiles': ['docker']},
            'postgresql-agent': {'type': 'zabbix-agent', 'profiles': ['postgresql']},
            'mariadb-agent': {'type': 'zabbix-agent', 'profiles': ['mysql']},
            'influxdb-agent': {'type': 'zabbix-agent', 'profiles': ['influxdb']}})
        for template in self.library['guest_templates'].values():
            self.assertEqual(template['monitoring'], {'profile': 'linux-agent'})
        for profile in self.library['app_profiles'].values():
            adapter = profile['adapter']
            expected = adapter + '-agent' if adapter in ('postgresql', 'mariadb', 'influxdb') else 'docker-agent'
            self.assertEqual(profile['monitoring'], {'profile': expected})

    def test_network_fragments_are_optional_definitions_not_a_site_access_default(self):
        rows = self.library['policies']['network']
        self.assertEqual(set(rows), {'mqtt_backend_ingress', 'http_backend_egress',
            'resolver_dns_udp_first', 'resolver_dns_tcp_first', 'package_repository_web_egress',
            'package_image_provider_web_egress', 'source_bound_package_image_provider_web_egress'})
        self.assertEqual(sum(len(v['rules']) for v in rows.values()), 13)
        for name, protocols in (('resolver_dns_udp_first', ['udp', 'tcp', 'udp', 'tcp']),
                                ('resolver_dns_tcp_first', ['tcp', 'udp', 'tcp', 'udp'])):
            rules = rows[name]['rules']
            self.assertEqual([row['proto'] for row in rules], protocols)
            self.assertEqual([row['destination'] for row in rules],
                [{'endpoint': 'primary_dns'}] * 2 + [{'endpoint': 'fallback_dns'}] * 2)
        self.assertEqual(rows['mqtt_backend_ingress']['rules'][0]['direction'], 'in')
        self.assertEqual(rows['http_backend_egress']['rules'][0]['direction'], 'out')
        bound = rows['source_bound_package_image_provider_web_egress']['rules'][0]
        self.assertEqual(bound['source'], {'interface': 'source'})
        self.assertEqual(bound['interface'], 'kernel')
        for template in self.library['guest_templates'].values():
            self.assertNotIn('network_policy', template)


if __name__ == '__main__':
    unittest.main()
