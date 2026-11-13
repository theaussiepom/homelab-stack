"""Library choices and focused PBS composition; type failures belong upstream."""
import hashlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import yaml
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK/'blueprints'), str(FRAMEWORK/'proxmox/applications')]
import component_plan
import component_packet
import component_sources
import component_workflows
from documentation_contracts import read_excerpt


class BackupProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.library, cls.sources = component_sources.library(ROOT)

    def setUp(self):
        for target in ('subprocess.run', 'subprocess.check_output', 'socket.create_connection'):
            boundary = patch(target, side_effect=AssertionError('Backup source tests cannot execute processes or contact targets'))
            boundary.start()
            self.addCleanup(boundary.stop)

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
            destination = row['backup']['job']['destination']
            self.assertEqual(added[0]['direction'], 'out')
            self.assertEqual(added[0]['proto'], 'tcp')
            self.assertEqual(added[0]['destination'], destination['server'] + '/32')
            self.assertEqual(added[0]['port'], str(destination['port']))
            self.assertTrue(all(rule in row['rules'] for rule in original_rules))
            packet = component_packet.lower_guest(prepared, guest)
            cfg = json.loads(packet['files']['site.json'])
            self.assertEqual(cfg['deployment']['phases'][-1], 'pbs-agent')
            self.assertEqual(component_workflows.model(prepared)['guests'][guest]['phases'][-1]['name'], 'Backup')
            job = cfg['app']['backup']['job']
            self.assertEqual(job['destination']['backup_id'], 'guest-610')
            self.assertEqual(job['schedule']['calendar'], '02:00')
            self.assertFalse(cfg['guest']['volumes']['backup-stage']['backup'])
            self.assertEqual(job['staging']['path'], cfg['guest']['volumes']['backup-stage']['path'])
            self.assertIn('backup-group.json', packet['files'])
            self.assertIn('backup-management.json', packet['files'])
            graph=component_workflows.model(prepared)
            self.assertEqual(graph['backup']['needs'],['selection'])
            self.assertIn('_backup',graph['guests'][guest]['needs'])
            self.assertEqual(graph['guests'][guest]['phases'][-1]['inputs'],
                {'PBS_API_TOKEN':{'environment':'PBS_API_TOKEN','workflow_secret':'PBS_API_TOKEN'}})
            self.assertTrue(all('PBS_API_TOKEN' not in phase['inputs'] for phase in graph['guests'][guest]['phases'][:-1]))
            self.assertEqual(set(job['group']), {'name', 'member'})
            import backup_agent
            backup_agent.configuration(cfg)
        disabled = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml', disabled=list(prepared.resolved['guests']))
        self.assertEqual(disabled.resolved['enabled'], [])
        self.assertTrue(all('backup' in row for row in disabled.resolved['guests'].values()))

    def test_database_consumers_compile_as_one_complete_backup_group(self):
        source = yaml.safe_load((ROOT/'examples/catalogue/new-database-guis.yaml').read_text())
        backup = yaml.safe_load((ROOT/'site.backup.example.yaml').read_text())['backup']
        job = backup['job']
        source['secret_sources']['pbs-management'] = {'type':'environment','name':'PBS_API_TOKEN'}
        source['external_endpoints']['pbs'] = {'protocol':'https','address':'192.0.2.50','port':8007}
        for guest_id, guest in source['guests'].items():
            guest['backup'] = None
            for volume in guest.get('volumes', {}).values():volume['backup'] = None
            volumes = guest.setdefault('volumes', {})
            volumes['backup-stage'] = {'storage':guest['root_storage'],'slot':max([v['slot'] for v in volumes.values()],default=-1)+1,
                'path':'/srv/backup-stage','size_gib':1}
        source['backup'] = None
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary).resolve()/'site.yaml';path.write_text(yaml.safe_dump(source))
            public=path.parent/backup['recovery_public_key']['source']
            public.parent.mkdir(parents=True)
            public.write_bytes((ROOT/backup['recovery_public_key']['source']).read_bytes())
            planned=component_plan.resolve(ROOT,path)
            inventories=[g['backup'] for g in planned.resolved['guests'].values()]
            job['capture'] = {'pause':[name for inv in inventories for name,app in inv['applications'].items()
                if any(row.get('capture')=='application-export' for row in app['storage'].values())],
                'database_lock':[name for name,app in planned.resolved['apps'].items() if app['adapter']=='mariadb'],
                'influx_tokens':{}}
            source['backup']=backup;path.write_text(yaml.safe_dump(source))
            from component_errors import ComponentError
            with self.assertRaisesRegex(ComponentError,'backup-database-producer'):
                component_plan.resolve(ROOT,path)
            # The optional remote browse connection has no root-group producer.
            # Keep the two genuinely managed administration links for this set.
            source['connections'].pop('browse')
            source['apps']['cloud']['properties']['connections'].pop('postgresql')
            path.write_text(yaml.safe_dump(source))
            operational=component_plan.resolve(ROOT,path)
            packets=component_packet.lower_plan(operational)
            self.assertEqual(set(packets),set(source['guests']))
            associations=[row for guest in operational.resolved['guests'].values()
                for app in guest['backup']['applications'].values() for row in app['databases']]
            expected={'postgresql':'postgres_database','mariadb':'database'}
            self.assertEqual({row['type']:row['target']['app'] for row in associations},expected)
            self.assertTrue(all('address' in row['target'] for row in associations))
            packet_associations=[]
            for packet in packets.values():
                import backup_agent
                cfg=json.loads(packet['files']['site.json']);backup_agent.configuration(cfg)
                packet_associations.extend(row for app in cfg['app']['backup']['applications'].values()
                    for row in app['databases'])
            self.assertEqual({row['type']:row['target']['app'] for row in packet_associations},expected)

    def test_documented_client_capacity_override_changes_only_effective_job_limits(self):
        """Bind documented capacity overrides and inheritance without changing job identities."""
        source, _ = component_sources.site(ROOT/'site.backup.example.yaml')
        original = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml')
        baseline = component_packet.lower_guest(original, 'resolver')
        baseline_job = json.loads(baseline['files']['site.json'])['app']['backup']['job']
        self.assertEqual(baseline_job['limits'], source['backup']['job']['limits'])
        override = read_excerpt((ROOT/'docs/backup.md').read_text(),
                                'Size clients independently', yaml.safe_load)
        self.assertEqual(set(override), {'backup'})
        self.assertNotIn('clients', source['backup']['job'])
        for inherit_files in (False, True):
            changed = copy.deepcopy(source)
            changed['guests']['resolver']['backup'] = copy.deepcopy(override['backup'])
            if inherit_files:
                changed['guests']['resolver']['backup']['limits'].pop('max_files')
            with self.subTest(inherit_files=inherit_files), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                path = root/'site.yaml'
                path.write_text(yaml.safe_dump(changed, sort_keys=False))
                public = root/changed['backup']['recovery_public_key']['source']
                public.parent.mkdir(parents=True)
                public.write_bytes((ROOT/changed['backup']['recovery_public_key']['source']).read_bytes())
                planned = component_plan.resolve(ROOT, path)
                packet = component_packet.lower_guest(planned, 'resolver')
                job = json.loads(packet['files']['site.json'])['app']['backup']['job']
                expected = {**source['backup']['job']['limits'],
                            **changed['guests']['resolver']['backup']['limits']}
                self.assertEqual(job['limits'], expected)
                self.assertNotEqual(job['limits'], baseline_job['limits'])
                self.assertEqual({**job, 'limits': baseline_job['limits']}, baseline_job)
                self.assertEqual(component_workflows.model(planned), component_workflows.model(original))
                self.assertGreaterEqual(job['staging']['size_bytes'], 4*expected['max_bytes'])

    def test_shared_bindings_keep_enrollment_explicit_including_disabled_members(self):
        """Root defaults do not enroll another guest or discard a disabled member."""
        source, _ = component_sources.site(ROOT/'site.backup.example.yaml')
        other = copy.deepcopy(source['guests']['resolver'])
        other.pop('backup')
        other.pop('volumes')
        other['identity'] = {'vmid': 611, 'hostname': 'example-unenrolled'}
        other['interfaces']['primary']['mac'] = '02:00:00:20:00:11'
        other['interfaces']['primary']['address']['value'] = '198.18.20.11'
        source['guests']['unenrolled'] = other
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = root/'site.yaml'
            path.write_text(yaml.safe_dump(source, sort_keys=False))
            public = root/source['backup']['recovery_public_key']['source']
            public.parent.mkdir(parents=True)
            public.write_bytes((ROOT/source['backup']['recovery_public_key']['source']).read_bytes())
            plan = component_plan.resolve(ROOT, path, disabled=['resolver'])
        self.assertNotIn('backup', plan.resolved['guests']['unenrolled'])
        self.assertFalse(any(row.startswith('proxmox-backup-client=')
                             for row in plan.resolved['guests']['unenrolled']['software_selection']['packages']))
        member = plan.resolved['guests']['resolver']['backup']['job']
        self.assertEqual(member['destination']['backup_id'], 'guest-610')
        self.assertEqual(set(plan.resolved['backup']['group']['group']['members']), {'guest-610'})
        self.assertNotIn('clients', source['backup']['job'])

    def test_explicit_guest_bindings_preserve_the_same_complete_packets_and_identity(self):
        """Spelling inherited values on the guest does not change its effective contract."""
        source, _ = component_sources.site(ROOT/'site.backup.example.yaml')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = root/'site.yaml'
            path.write_text(yaml.safe_dump(source, sort_keys=False))
            public = root/source['backup']['recovery_public_key']['source']
            public.parent.mkdir(parents=True)
            public.write_bytes((ROOT/source['backup']['recovery_public_key']['source']).read_bytes())
            inherited = component_plan.resolve(ROOT, path)
            identity = inherited.resolved['guests']['resolver']['backup']['job']['destination']['backup_id']
            source['guests']['resolver']['backup'] = {
                **source['backup']['defaults'], 'backup_id': identity}
            path.write_text(yaml.safe_dump(source, sort_keys=False))
            explicit = component_plan.resolve(ROOT, path)
            self.assertEqual(explicit.resolved, inherited.resolved)
            self.assertEqual(component_packet.lower_plan(explicit), component_packet.lower_plan(inherited))
            self.assertEqual(component_workflows.model(explicit), component_workflows.model(inherited))

    def test_operational_example_keeps_runtime_storage_qualification_separate_from_compilation(self):
        """Bind the example's storage ID to the shared runtime floor without a target call."""
        source, _ = component_sources.site(ROOT/'site.backup.example.yaml')
        plan = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml')
        cfg = json.loads(component_packet.lower_guest(plan, 'resolver')['files']['site.json'])
        storage_id = cfg['guest']['storage_id']
        self.assertEqual(storage_id, source['storage'][source['guests']['resolver']['root_storage']]['pool'])
        self.assertEqual(cfg['app']['backup']['job']['staging']['path'],
                         source['guests']['resolver']['volumes']['backup-stage']['path'])
        guide = (ROOT/'docs/backup.md').read_text()
        self.assertIn('non-shared `zfspool`', guide)
        self.assertIn('configure.md#prepare-storage-for-an-already-managed-guest', guide)
        import backup_staging
        qualified = {'storage': storage_id, 'type': 'zfspool', 'shared': 0, 'pool': 'example-zfs/data'}
        self.assertEqual(backup_staging.storage([qualified], storage_id),
                         ('example-zfs/data', '/example-zfs/data'))
        with self.assertRaisesRegex(ValueError, 'Bind an isolated declared ZFS pool'):
            backup_staging.storage([{**qualified, 'type': 'lvmthin'}], storage_id)

    def test_scheduler_guide_matches_the_selected_account_owned_installation(self):
        """Keep the prerequisite and installed-path explanation bound to the real builder."""
        plan = component_plan.resolve(ROOT, ROOT/'site.backup.example.yaml')
        packet = component_packet.lower_guest(plan, 'resolver')
        schedule = json.loads(packet['files']['backup-group.json'])
        import backup_controller
        state = min(row['state_root'] for row in schedule['group']['members'].values())
        directory = state+'/backup-controller/framework/'+'a'*64+'/proxmox/applications'
        rendered = backup_controller.units(schedule, directory, 1000, '/home/example-cd')
        guide = (ROOT/'docs/backup.md').read_text()
        self.assertIn('configure.md#prepare-the-controllers-persistent-user-manager', guide)
        self.assertIn('operations.md#find-the-schedule-and-completion-records', guide)
        self.assertIn('`NoNewPrivileges`', guide)
        self.assertIn('does not use local `sudo`', guide)
        self.assertIn('root/system-scope namesake is refused', guide)
        self.assertIn('Preparing the user manager alone does not convert that schedule', guide)
        self.assertIn('Keep its working source pins and backup protection until that handover is available', guide)
        self.assertIn('also applies to managed enrollment', guide)
        self.assertIn("a process with the CD account's UID can alter its own alarm", guide)
        for suffix in ('service', 'timer'):
            path = rendered['unit_directory'].removeprefix('/home/example-cd/')
            path += '/'+rendered['name']+'.'+suffix
            self.assertIn(path.replace(schedule['group']['name'], '<job-name>'), guide)
        self.assertIn(rendered['base'].replace(state, '<state_root>')+'/schedules/', guide)
        self.assertIn(directory.removesuffix('/applications').replace(state, '<state_root>').replace('a'*64, '<source-hash>')+'/', guide)
        self.assertIn('account-owned, not root-immutable', guide)


if __name__ == '__main__': unittest.main()
