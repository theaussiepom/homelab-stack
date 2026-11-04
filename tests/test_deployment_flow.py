"""Start each guest on its own prerequisites, for fresh ordering and updates."""
import importlib.util
import json
import os
from pathlib import Path
import unittest
from graphlib import TopologicalSorter

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
spec = importlib.util.spec_from_file_location('deployment_flow_compiler', FRAMEWORK/'blueprints/compile.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
EXPECTED = {
    'dns': [], 'ingress': ['dns'], 'postgresql': ['dns'], 'mariadb': ['dns'],
    'influxdb': ['dns'], 'identity': ['postgresql','ingress'],
    'db-tools': ['postgresql','mariadb','ingress'],
    'automation': ['mariadb','influxdb','mqtt'], 'bitwarden': ['ingress','mariadb'],
    'pegaprox': ['dns'], 'zigbee2mqtt': ['mqtt'], 'monitoring': ['postgresql','ingress'],
    'music': ['dns','ingress'], 'mqtt': ['dns'],
}


class DeploymentFlowTests(unittest.TestCase):
    def test_declared_first_install_order_has_no_global_or_unrelated_barrier(self):
        declared = c.manifest(ROOT)['guests']
        self.assertEqual({key:row['depends_on'] for key,row in declared.items()},EXPECTED)
        sorter=TopologicalSorter(EXPECTED)
        sorter.prepare()
        self.assertEqual(set(sorter.get_ready()),{'dns'})
        sorter.done('dns')
        first=set(sorter.get_ready())
        self.assertEqual(first,{'ingress','postgresql','mariadb','influxdb','pegaprox','mqtt'})
        # Leave ingress/identity unfinished: the Automation and Radio lanes may
        # start as soon as their own database/broker prerequisites have completed.
        sorter.done('mariadb','influxdb','mqtt')
        self.assertEqual(set(sorter.get_ready()),{'automation','zigbee2mqtt'})
        sorter.done('ingress')
        ready=set(sorter.get_ready())
        self.assertIn('music',ready)
        self.assertNotIn('db-tools',ready)
        sorter.done('postgresql')
        ready=set(sorter.get_ready())
        self.assertIn('identity',ready)
        self.assertIn('db-tools',ready)
        # CloudBeaver and Authentik can now start in the same first-install wave.
        sorter.done('db-tools')
        sorter.done('identity')

    def test_automation_selection_without_identity_ingress_keeps_runtime_unchanged(self):
        overlay=c.read(ROOT/'site.example.yaml')
        baseline=c.compile_stack(ROOT,overlay,[])
        kept={'dns','mariadb','influxdb','mqtt','automation'}
        disabled=sorted(set(baseline)-kept)
        selected=c.compile_stack(ROOT,overlay,disabled)
        self.assertEqual({key for key,row in selected.items() if row['enabled']},kept)
        self.assertEqual(selected['automation']['files'],baseline['automation']['files'])
        stack=json.loads(selected['automation']['files']['stack.json'])
        self.assertEqual(set(stack['services']),{'homeassistant','node_red'})
        for prerequisite in EXPECTED['automation']:
            with self.subTest(prerequisite=prerequisite),self.assertRaisesRegex(ValueError,'prerequisite'):
                c.compile_stack(ROOT,overlay,sorted(set(disabled)|{prerequisite}))

    def test_cloud_keeps_database_and_ingress_dependencies_without_identity(self):
        overlay=c.read(ROOT/'site.example.yaml')
        for prerequisite in EXPECTED['db-tools']:
            with self.subTest(prerequisite=prerequisite),self.assertRaisesRegex(ValueError,'prerequisite'):
                c.compile_stack(ROOT,overlay,[prerequisite])
        selected=c.compile_stack(ROOT,overlay,['identity'])
        self.assertTrue(selected['db-tools']['enabled'])
        self.assertTrue(selected['automation']['enabled'])
        self.assertTrue(selected['music']['enabled'])


if __name__ == '__main__':
    unittest.main()
