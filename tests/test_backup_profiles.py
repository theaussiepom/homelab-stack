"""Library choices and focused PBS composition; type failures belong upstream."""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK/'blueprints'), str(FRAMEWORK/'proxmox/applications')]
import component_plan
import component_packet
import component_sources
import component_workflows


class BackupProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.library, cls.sources = component_sources.library(ROOT)

    def test_client_package_repository_and_key_are_one_authoritative_definition(self):
        self.assertEqual(self.library['backup_profiles']['pbs-client']['software'], ['pbs-client'])
        definition = self.library['software']['pbs-client']
        self.assertEqual(definition['packages'], ['proxmox-backup-client=4.2.8-1'])
        repository = definition['repositories'][0]
        self.assertNotIn('trusted=yes', repository['source'])
        self.assertIn('Signed-By: /usr/share/keyrings/pbs-client.asc', repository['source'])
        key = self.library['assets'][repository['key_asset']]
        self.assertEqual(hashlib.sha256(key['text'].encode()).hexdigest(), key['sha256'])
        self.assertIn('BEGIN PGP PUBLIC KEY BLOCK', key['text'])

    def test_every_current_profile_and_variant_has_an_explicit_storage_disposition(self):
        for name, profile in self.library['app_profiles'].items():
            with self.subTest(profile=name):
                rules = profile['backup']
                self.assertEqual(set(rules['include']) | set(rules['exclude']), set(profile.get('storage', {})))
                self.assertFalse(set(rules['include']) & set(rules['exclude']))
                document = ROOT/'docs/reference/apps'/f'{name}.md'
                self.assertIn('backup-coverage.md#'+name, document.read_text())

    def test_database_guests_keep_configuration_and_separate_native_export_requirements(self):
        for adapter, path in [('postgresql', '/etc/postgresql'), ('mariadb', '/etc/mysql'),
                              ('influxdb', '/etc/influxdb')]:
            profile = self.library['app_profiles'][adapter]['backup']
            self.assertEqual(profile['include']['data'], {'category': 'database', 'capture': 'database-export'})
            self.assertNotIn('configuration', profile)
            import component_native
            self.assertEqual(component_native.configuration_root(adapter), path)

    def test_critical_state_is_not_misclassified_as_logs_or_rebuildable_cache(self):
        expected = {'bitwarden': 'data', 'node_red': 'data', 'homeassistant': 'config',
                    'authentik': 'redis', 'mqtt': 'data', 'zigbee2mqtt': 'data',
                    'music_assistant': 'data', 'pegaprox': 'config', 'traefik': 'certs',
                    'cloudbeaver': 'workspace', 'mqtt_explorer': 'data'}
        for name, role in expected.items():
            with self.subTest(profile=name):
                self.assertEqual(self.library['app_profiles'][name]['backup']['include'][role],
                                 {'category': 'state', 'capture': 'application-export'})
        self.assertEqual(self.library['app_profiles']['pihole']['backup']['exclude']['database'], 'transient')
        self.assertEqual(self.library['app_profiles']['bitwarden']['backup']['exclude']['logs'], 'transient')

    def test_complete_operational_example_keeps_dag_and_binds_job_network_and_staging(self):
        original = component_plan.resolve(ROOT, ROOT/'site.example.yaml')
        prepared = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml')
        self.assertEqual(original.resolved['guest_dependencies'], prepared.resolved['guest_dependencies'])
        self.assertEqual(original.resolved['app_dependencies'], prepared.resolved['app_dependencies'])
        for guest in prepared.resolved['enabled']:
            self.assertNotIn('backup', original.resolved['guests'][guest])
            row = prepared.resolved['guests'][guest]
            self.assertIn('proxmox-backup-client=4.2.8-1', row['software_selection']['packages'])
            original_rules = original.resolved['guests'][guest]['rules']
            added = [rule for rule in row['rules'] if rule not in original_rules]
            self.assertEqual(len(added), 1)
            self.assertIn('8007', json.dumps(added[0]))
            self.assertTrue(all(rule in row['rules'] for rule in original_rules))
            packet = component_packet.lower_guest(prepared, guest)
            cfg = json.loads(packet['files']['site.json'])
            self.assertEqual(cfg['deployment']['phases'][-1], 'pbs-agent')
            self.assertEqual(component_workflows.model(prepared)['guests'][guest]['phases'][-1]['name'], 'PBS agent')
            job = cfg['app']['backup']['job']
            self.assertEqual(job['destination']['backup_id'], 'guest-610')
            self.assertEqual(job['schedule']['calendar'], '02:00')
            self.assertFalse(cfg['guest']['volumes']['backup-stage']['backup'])
            self.assertEqual(job['staging']['path'], cfg['guest']['volumes']['backup-stage']['path'])
            self.assertIn('backup-group.json', packet['files'])
            self.assertEqual(set(job['group']), {'name', 'member'})
            import backup_agent
            backup_agent.configuration(cfg)
        disabled = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml', disabled=list(prepared.resolved['guests']))
        self.assertEqual(disabled.resolved['enabled'], [])
        self.assertTrue(all('backup' in row for row in disabled.resolved['guests'].values()))


if __name__ == '__main__': unittest.main()
