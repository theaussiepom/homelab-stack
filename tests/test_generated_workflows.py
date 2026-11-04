"""Actual explicit compositions generate checked-in, fail-stop guest workflows."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints'), str(FRAMEWORK / 'proxmox/applications')]
import compile as compiler
import component_workflows
from component_input_secrets import PREFIX, SLOTS
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]
GENERATOR = FRAMEWORK / 'blueprints/workflows.py'
COMMON = {'APPLICATION_SSH_KEY', 'PROXMOX_APP_TOKEN'}


def generate(stack, check=False, *, site=None):
    return subprocess.run([sys.executable, str(GENERATOR), '--stack', str(stack),
                           '--site', str(site or stack / 'site.example.yaml'),
                           *(['--check'] if check else [])],
                          capture_output=True, text=True, timeout=30)


def load(path):
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)


def copy_library(target):
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.work', '__pycache__'))


class GeneratedWorkflowTests(unittest.TestCase):
    def test_checked_in_workflows_match_the_explicit_starter_and_published_pin(self):
        result = generate(ROOT, check=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        phase = load(ROOT / '.github/workflows/phase.yml')['jobs']['run']['uses']
        self.assertRegex(phase, r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/\.github/workflows/guest-phase\.yml@[0-9a-f]{40}$')

    def test_check_detects_guest_and_phase_drift_without_writing_and_repairs_it(self):
        for changed in ('guest-resolver.yml', 'phase.yml'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve() / 'stack'; copy_library(root)
                workflows = root / '.github/workflows'
                phase = (workflows / 'phase.yml').read_bytes()
                ci_names = ('validate-stack.yml', 'review-pr-dependencies.yml', 'scan-python-security.yml')
                ci = {name: (workflows / name).read_bytes() for name in ci_names}
                path = workflows / changed
                if changed == 'phase.yml':
                    document = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
                    del document['on']['workflow_call']['secrets']['APPLICATION_SSH_KEY']
                    del document['jobs']['run']['secrets']['APPLICATION_SSH_KEY']
                    path.write_text(yaml.safe_dump(document, sort_keys=False))
                else:
                    path.write_bytes(path.read_bytes() + b'\n# unintended manual edit\n')
                before = {p.name: p.read_bytes() for p in workflows.iterdir()}
                result = generate(root, check=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(changed, result.stdout + result.stderr)
                self.assertEqual(before, {p.name: p.read_bytes() for p in workflows.iterdir()})
                result = generate(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(generate(root, check=True).returncode, 0)
                self.assertEqual((workflows / 'phase.yml').read_bytes(), phase)
                self.assertEqual({name: (workflows / name).read_bytes() for name in ci_names}, ci)

    def test_one_guest_job_matches_actual_packet_phases_in_both_distinct_layouts(self):
        for site, guests, phases in (('site.example.yaml', 1, 3), ('examples/site.second.yaml', 3, 10)):
            with self.subTest(site=site), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve() / 'stack'; copy_library(root)
                # A deliberate alternate layout retires only the previous generated guest paths.
                for path in (root / '.github/workflows').glob('guest-*.yml'): path.unlink()
                result = generate(root, site=root / site)
                self.assertEqual(result.returncode, 0, result.stderr)
                plan = compiler.resolve_plan(root, root / site)
                graph = component_workflows.model(plan); packets = compiler.lower_plan(plan)
                deploy = load(root / '.github/workflows/deploy.yml')
                self.assertEqual(len(graph['guests']), guests)
                self.assertEqual(set(deploy['jobs']), {'selection', *graph['guests']})
                self.assertEqual(sum(len(row['phases']) for row in graph['guests'].values()), phases)
                pin = load(root / '.github/workflows/phase.yml')['jobs']['run']['uses']
                repository, revision = pin.split('/.github/workflows/guest-phase.yml@')
                for guest, metadata in graph['guests'].items():
                    workflow = load(root / '.github/workflows' / ('guest-' + guest + '.yml'))
                    self.assertEqual(list(workflow['jobs']), ['deploy'])
                    job = workflow['jobs']['deploy']; caller = deploy['jobs'][guest]
                    self.assertEqual(workflow['name'], metadata['name']); self.assertEqual(job['name'], metadata['name'])
                    self.assertEqual(job['name'], caller['name'])
                    self.assertEqual(caller['needs'], metadata['needs'])
                    self.assertEqual(job['if'], caller['if'])
                    self.assertIn("github.event.repository.private == true", job['if'])
                    self.assertIn("github.ref == 'refs/heads/main'", job['if'])
                    self.assertEqual(int(job['timeout-minutes']), 45 * len(metadata['phases']))
                    self.assertEqual(job['env'], {'HOMELAB_DEPLOYMENT_WORKFLOW': '${{ github.workflow_ref }}'})
                    self.assertEqual(job['steps'][0], {'name': 'Setup', 'uses': repository + '/.github/actions/guest-setup@' + revision,
                                                     'timeout-minutes': '45'})
                    cfg = json.loads(packets[guest]['files']['site.json'])
                    self.assertEqual(['infrastructure', *cfg['deployment']['phases']],
                                     [row['id'] for row in metadata['phases']])
                    for step, phase in zip(job['steps'][1:], metadata['phases'], strict=True):
                        self.assertEqual(step['name'], phase['name'])
                        self.assertEqual(step['uses'], repository + '/.github/actions/guest-phase@' + revision)
                        self.assertEqual(step['with']['phase'], phase['id'])
                        self.assertEqual(step['with']['guest'], guest)
                        self.assertEqual(step['with']['disabled'], '${{ inputs.disabled }}')
                        self.assertEqual(step['timeout-minutes'], '45')
                        self.assertNotIn('continue-on-error', step); self.assertNotIn('if', step)
                        self.assertNotIn('env', step)

    def test_finite_scalar_slots_stay_only_in_the_final_shared_deploy_process(self):
        phase = load(ROOT / '.github/workflows/phase.yml')
        framework = load(FRAMEWORK / '.github/workflows/guest-phase.yml')
        slots = {slot for roles in SLOTS.values() for slot in roles.values()}
        expected = {**{name: {'required': 'true'} for name in COMMON},
                    **{name: {'required': 'false'} for name in slots}}
        for document in (phase, framework):
            self.assertEqual(document['on']['workflow_call']['secrets'], expected)
            self.assertEqual(document['permissions'], {'contents': 'read'})
        self.assertEqual(phase['jobs']['run']['secrets'],
                         {name: '${{ secrets.' + name + ' }}' for name in expected})
        shared = load(FRAMEWORK / '.github/actions/guest-phase/action.yml')
        steps = shared['runs']['steps']
        self.assertEqual([row['name'] for row in steps], ['Check readiness', 'Check inputs', 'Load credentials', 'Deploy'])
        self.assertEqual(set(steps[1]['env']), {'GUEST', 'PHASE', 'DISABLED'})
        self.assertEqual(set(steps[2]['env']), {'GUEST', 'PHASE', *COMMON})
        self.assertEqual(set(steps[3]['env']), {'GUEST', 'PHASE', *[PREFIX + slot.upper() for slot in slots]})
        for slot in slots:
            self.assertEqual(steps[3]['env'][PREFIX + slot.upper()], '${{ inputs.' + slot + ' }}')
        self.assertNotIn('secrets.', json.dumps(shared))
        setup = load(FRAMEWORK / '.github/actions/guest-setup/action.yml')['runs']['steps']
        self.assertEqual(len(setup), 7); self.assertEqual(setup[-1]['name'], 'Prepare config')
        self.assertNotIn('secrets.', json.dumps(setup)); self.assertFalse(any('env' in row for row in setup))
        deploy = load(ROOT / '.github/workflows/deploy.yml')
        self.assertNotIn('secrets', deploy['jobs']['selection'])
        for guest in compiler.resolve_plan(ROOT, ROOT / 'site.example.yaml').resolved['guests']:
            workflow = load(ROOT / '.github/workflows' / ('guest-' + guest + '.yml'))
            self.assertEqual(set(workflow['on']['workflow_call']['secrets']), COMMON)
            for step in workflow['jobs']['deploy']['steps'][1:]:
                self.assertEqual(set(step['with']), {'guest', 'phase', 'disabled', *COMMON})
                for name in COMMON: self.assertEqual(step['with'][name], '${{ secrets.' + name + ' }}')

    def test_actual_secret_free_selector_validates_disabled_and_rejects_source_drift(self):
        deploy = yaml.safe_load((ROOT / '.github/workflows/deploy.yml').read_text())
        selection = deploy['jobs']['selection']; steps = selection['steps']
        self.assertEqual(selection['timeout-minutes'], 2)
        self.assertIn('private == true', selection['if']); self.assertNotIn('secrets', selection)
        step = next(row for row in steps if row.get('id') == 'selection')
        prepared = next(row for row in steps if row.get('name') == 'Prepare config')
        self.assertLess(steps.index(prepared), steps.index(step))
        self.assertIn('framework-source/requirements.lock.txt', prepared['run'])
        self.assertIn('--require-hashes --no-deps', prepared['run'])
        self.assertNotIn('secrets.', json.dumps(steps))
        expected = json.loads(step['env']['EXPECTED_MODEL'])
        self.assertEqual(expected['guest_order'], ['resolver'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); copy_library(root / 'stack-source')
            (root / 'framework-source').symlink_to(FRAMEWORK, target_is_directory=True)
            shutil.copyfile(ROOT / 'site.example.yaml', root / 'site.yaml')
            def execute(disabled):
                return subprocess.run(['sh', '-eu', '-c', step['run']], cwd=root,
                    env=dict(os.environ, DISABLED=disabled, EXPECTED_MODEL=step['env']['EXPECTED_MODEL'],
                             GITHUB_OUTPUT=os.devnull, HOMELAB_CONFIG_PYTHON=sys.executable),
                    capture_output=True, text=True, timeout=20)
            for disabled, accepted in (('', True), ('[]', True), ('["resolver"]', True),
                    ('["unknown"]', False), ('["resolver","resolver"]', False), ('[1]', False),
                    ('{}', False), ('null', False), ('invalid-json', False)):
                with self.subTest(disabled=disabled):
                    result = execute(disabled)
                    self.assertEqual(result.returncode == 0, accepted, result.stderr)
            value = yaml.safe_load((root / 'site.yaml').read_text())
            value['apps']['recursive_dns']['display_name'] = 'Changed component label'
            (root / 'site.yaml').write_text(yaml.safe_dump(value, sort_keys=False))
            result = execute('[]')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Regenerate', result.stderr)
