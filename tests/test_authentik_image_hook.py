"""Exercise the source planner and the real compiler's profile ownership boundary."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK/'blueprints'), str(FRAMEWORK/'proxmox/applications')]
import component_lower
import component_packet
import component_plan
from authentik_releases import REPOSITORY

SCRIPT = ROOT/'apps/authentik/plan.py'
spec = importlib.util.spec_from_file_location('authentik_source_plan', SCRIPT)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


class HookTests(unittest.TestCase):
    def test_retained_storage_is_checked_in_the_phase_that_owns_it(self):
        site = yaml.safe_load((ROOT/'examples/catalogue/identity-monitoring.yaml').read_text())
        guest = site['guests']['identity']
        storage = site['apps']['identity']['storage']
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve()/'site.yaml'
            for binding in ('root_path', 'volume'):
                with self.subTest(binding=binding):
                    if binding == 'volume':
                        root = guest.pop('root_paths')['data']['path']
                        guest['volumes'] = {'data': {'storage': 'local', 'slot': 0, 'size_gib': 8, 'path': root}}
                        for row in storage.values():
                            row['volume'] = row.pop('root_path')
                    source.write_text(yaml.safe_dump(site))
                    plan = component_plan.resolve(ROOT, source)
                    packet = component_packet.lower_guest(plan, 'identity')
                    runtime = json.loads(packet['files']['component-runtime.json'])
                    paths = runtime['applications']['identity']['storage_paths']
                    self.assertEqual(set(paths), {'data', 'media', 'certs', 'templates'})
                    prepared = json.loads(packet['files']['site.json'])['app']['required_paths']
                    self.assertEqual({row['path'] for row in prepared},
                                     {row['source'] for role, row in paths.items()
                                      if binding == 'root_path' or role != 'data'})

    def test_default_and_cross_profile_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            stack = Path(directory).resolve()/'stack'
            shutil.copytree(ROOT, stack, ignore=shutil.ignore_patterns('.git','node_modules','__pycache__','.work'))
            source = stack/'site.example.yaml'
            def compile():
                return component_plan.resolve(stack, source)
            plan = compile()
            app = next(iter(plan.resolved['apps'].values()))
            runtime = component_lower.runtime_config(plan,app['guest'])
            self.assertEqual(runtime['applications'][app['id']]['image_update'],'standard')
            auth = stack/'apps/authentik.yaml'
            other = stack/'apps/unbound.yaml'
            original = auth.read_text()
            for change in [original.replace('image_update: release-series\n',''),
                           original.replace('release-series','standard')]:
                auth.write_text(change)
                with self.assertRaisesRegex(ValueError,'image-update'):
                    compile()
            auth.write_text(original)
            other.write_text(other.read_text()+'\nimage_update: release-series\n')
            with self.assertRaisesRegex(ValueError,'image-update'):
                compile()
            other.write_text((ROOT/'apps/unbound.yaml').read_text())
            (stack/'apps/authentik/image-update.yaml').unlink()
            with self.assertRaises(ValueError):
                compile()

    def test_source_lookup_and_registry_evidence(self):
        with patch.object(planner.subprocess,'check_output',return_value='other\nversion/2027.2.1\n') as lookup:
            self.assertEqual(planner.published('goauthentik/authentik'),['2027.2.1'])
            self.assertIn('--paginate',lookup.call_args.args[0])
        def response(raw, headers=None):
            stream = io.BytesIO(raw)
            stream.headers = headers or {}
            return stream
        for os_name, correct, success in [('linux',True,True),('windows',True,False),('linux',False,False)]:
            raw=json.dumps({'manifests':[{'platform':{'os':os_name,'architecture':'amd64'}}]}).encode()
            digest='sha256:'+hashlib.sha256(raw).hexdigest()
            with patch.object(planner.urllib.request,'urlopen',side_effect=[
                    response(b'{"token":"test"}'),response(raw,{'Docker-Content-Digest':digest if correct else ''})]):
                resolve=planner.registry(REPOSITORY)
                if success:
                    self.assertEqual(resolve('2027.2.1'),digest)
                else:
                    with self.assertRaises(ValueError):
                        resolve('2027.2.1')

    def test_plan_and_verify_cli(self):
        digest='sha256:'+'a'*64
        source=REPOSITORY+':2026.8.6@'+digest
        target=REPOSITORY+':2027.1.2@'+digest
        chain=[source,target]
        with tempfile.TemporaryDirectory() as directory:
            app=Path(directory)/'app.yaml'
            def invoke(args):
                with patch.object(sys,'argv',[str(SCRIPT),*args]), redirect_stdout(io.StringIO()) as output:
                    planner.main()
                    return json.loads(output.getvalue())
            catalogue = Path(directory) / 'images.json'
            catalogue.write_text(json.dumps({'authentik': {'repository': REPOSITORY, 'tag': '2027.1.2',
                                                           'digest': digest}}))
            with patch.object(planner, 'CATALOGUE', catalogue), \
                 patch.object(planner,'published',return_value=['2026.8.6','2027.1.1','2027.1.2','2027.1.3','2027.3.1']), \
                 patch.object(planner,'registry',return_value=lambda _:digest):
                self.assertEqual(invoke([source]),chain)
                with self.assertRaises(SystemExit), patch.object(sys,'stderr',new_callable=io.StringIO):
                    invoke([])
                for profile,pins,valid in [('authentik',chain,True),('other',chain,False),
                                           ('authentik',[source,target.replace('.2@','.1@')],False)]:
                    app.write_text(yaml.safe_dump({'profile':profile,'properties':{'upgrade_path':pins}}))
                    if valid:
                        self.assertEqual(invoke(['--check-app',str(app)]),chain)
                    else:
                        with self.assertRaises(ValueError):
                            invoke(['--check-app',str(app)])
        with patch.object(sys,'argv',[str(SCRIPT),'--help']), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            runpy.run_path(str(SCRIPT),run_name='__main__')
