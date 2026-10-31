"""The empty root marker adds one guest and the existing workload templates."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
spec = importlib.util.spec_from_file_location('zabbix_stack_compiler', FRAMEWORK/'blueprints/compile.py')
compiler = importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)


class MonitoringFeatureTests(unittest.TestCase):
    def overlay(self):
        return compiler.read(ROOT/'site.example.json')

    def packets(self, marker=True, disabled=None):
        overlay = self.overlay()
        if marker:overlay['zabbix']=None
        return compiler.compile_stack(ROOT,overlay,disabled)

    def test_root_presence_creates_exactly_one_dedicated_guest(self):
        off=self.packets(False);on=self.packets()
        self.assertEqual(len(off),11)
        self.assertEqual(set(on)-set(off),{'monitoring'})
        cfg=json.loads(on['monitoring']['files']['site.json'])
        self.assertEqual(cfg['guest']['hostname'],'zabbix')
        self.assertEqual(cfg['app']['kind'],'monitoring')
        self.assertEqual(cfg['routes']['zabbix']['host'],'zabbix.example.invalid')
        self.assertEqual(cfg['routes']['zabbix']['middlewares'],['security-headers','management-clients'])
        self.assertNotIn('monitoring',cfg['app']['monitoring']['proxmox']['hostname'])

    def test_profiles_are_derived_and_source_contains_no_generated_credentials(self):
        packets=self.packets()
        for name,packet in packets.items():
            cfg=json.loads(packet['files']['site.json']);profiles=cfg['app']['monitoring']['profiles']
            self.assertIn('linux',profiles)
            self.assertEqual('docker' in profiles,'docker' in cfg['deployment']['capabilities'])
            if name in {'postgresql','mariadb','influxdb'}:
                self.assertIn('mysql' if name=='mariadb' else name,profiles)
            self.assertNotIn('monitoring-agent.json',packet['files'])
            self.assertNotIn('monitoring-server.json',packet['files'])
        storage=json.loads(packets['monitoring']['files']['stack.json'])['monitoring']
        self.assertEqual(storage['postgresql_user'],'zabbix')
        self.assertEqual(storage['postgresql_database'],'zabbix')

    def test_empty_value_only_and_default_guest_identity_collisions_refuse(self):
        for value in [True,False,{},[],0]:
            overlay=self.overlay();overlay['zabbix']=value
            with self.subTest(value=value),self.assertRaises(ValueError):compiler.compile_stack(ROOT,overlay)
        overlay=self.overlay();overlay['zabbix']=None
        overlay['guests']['monitoring']={'config':{'guest':{'vmid':208},'app':{'vmid':208}}}
        with self.assertRaises(ValueError):compiler.compile_stack(ROOT,overlay)

    def test_disabled_leafs_keep_existing_dependency_rules(self):
        packets=self.packets(disabled=['db-tools'])
        self.assertFalse(packets['db-tools']['enabled'])
        self.assertTrue(packets['monitoring']['enabled'])
        members=json.loads(packets['monitoring']['files']['site.json'])['app']['monitoring']['members']
        self.assertNotIn('db-tools',{m['guest'] for m in members})
        with self.assertRaises(ValueError):self.packets(disabled=['postgresql'])
        self.assertEqual(len(self.packets(False,['monitoring'])),11)
        self.assertFalse(self.packets(True,['monitoring'])['monitoring']['enabled'])

    def test_generated_selection_reads_presence_and_never_runs_an_absent_feature(self):
        import yaml
        deploy=yaml.safe_load((ROOT/'.github/workflows/deploy.yml').read_text())
        self.assertIn("needs.selection.outputs.zabbix == 'true'",deploy['jobs']['monitoring']['if'])
        self.assertEqual(deploy['jobs']['monitoring']['needs'],['selection','postgresql','ingress'])
        self.assertNotIn('monitoring',deploy['jobs']['postgresql']['needs'])
        step=next(s for s in deploy['jobs']['selection']['steps'] if s.get('id')=='selection')
        for active in [False,True]:
            with tempfile.TemporaryDirectory() as td:
                root=Path(td);overlay=self.overlay()
                if active:overlay['zabbix']=None
                (root/'site.json').write_text(json.dumps(overlay))
                out=root/'outputs'
                run=subprocess.run(['sh','-eu','-c',step['run']],cwd=root,
                    env=dict(os.environ,DISABLED='[]',DEPENDENCIES=step['env']['DEPENDENCIES'],GITHUB_OUTPUT=str(out)),capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr)
                self.assertEqual(out.read_text(),'zabbix='+str(active).lower()+'\n')

    def test_monitoring_accounts_have_explicit_loopback_and_exact_remote_storage_rules(self):
        hba=self.packets()['postgresql']['files']['pg_hba.conf']
        prefix=hba.splitlines()[:5]
        self.assertEqual(prefix,['# Root Zabbix: dedicated storage and local statistics only',
            'host postgres zbx_monitor 127.0.0.1/32 scram-sha-256',
            'host zabbix zabbix 127.0.0.1/32 scram-sha-256',
            'hostssl zabbix zabbix 198.18.31.36/32 scram-sha-256',
            'hostnossl zabbix zabbix 198.18.31.36/32 reject'])
        self.assertTrue(hba.endswith(self.packets(False)['postgresql']['files']['pg_hba.conf']))
