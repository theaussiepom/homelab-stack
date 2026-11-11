"""Execute the maintained newcomer choices with the library-selected compiler."""
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints')]
import compile as compiler
from component_errors import ComponentError
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]
from documentation_contracts import expect_refusal, read_excerpt, table_cells


def no_native(*args, **kwargs):
    raise AssertionError('The newcomer walkthrough must remain offline')


class PersonalisationWalkthrough(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.site = self.work / 'personal-site'
        # Equivalent to the guide's whole-directory copy: no leaf points back
        # into the public checkout, and optional leaves travel with the site.
        shutil.copytree(ROOT / 'examples/personalisation', self.site)
        self.page = (ROOT / 'docs/guides/design-your-homelab.md').read_text()
        for target in ('subprocess.run', 'subprocess.check_output', 'socket.create_connection'):
            boundary = patch(target, side_effect=no_native)
            boundary.start()
            self.addCleanup(boundary.stop)

    def read(self, name):
        return yaml.safe_load((self.site / name).read_text())

    def write(self, name, value):
        (self.site / name).write_text(yaml.safe_dump(value, sort_keys=False))

    def excerpt(self, heading):
        # The existing strict reader accepts second-level sections. Promote
        # subsection headings only in this read view; retain its ambiguity guard.
        return read_excerpt(self.page.replace('\n### ', '\n## '), heading, yaml.safe_load)

    def plan(self):
        return compiler.resolve_plan(ROOT, self.site / 'site.yaml', [])

    def cli(self, *arguments):
        stream = io.StringIO()
        with patch.object(sys, 'argv', ['compile.py', '--stack', str(ROOT),
                '--site', str(self.site / 'site.yaml'), *arguments]), redirect_stdout(stream):
            compiler.main()
        return stream.getvalue()

    def inspect(self, packet):
        scripts = re.findall(r'<<\'PYCODE\'\n(.*?)^PYCODE$', self.page, re.M | re.S)
        self.assertEqual(len(scripts), 1, 'Keep one unambiguous documented packet inspector')
        output = io.StringIO()
        with patch.object(sys, 'argv', ['inspect', str(packet)]), redirect_stdout(output):
            exec(compile(scripts[0], '<documented-packet-inspector>', 'exec'), {})
        return output.getvalue()

    def personalise(self):
        section = self.page.split('## 5. Put your choices into the source\n', 1)[1].split('\n### ', 1)[0]
        rows = [table_cells(line) for line in section.splitlines()
                if line.startswith('| `')]
        self.assertTrue(rows, 'Execute the actual practice worksheet, not a parallel fixture')
        for filename, dotted, replacement in rows:
            filename, dotted = filename.strip('`'), dotted.strip('`')
            value = self.read(filename)
            target = value
            keys = dotted.split('.')
            for key in keys[:-1]:
                target = target[key]
            self.assertIn(keys[-1], target, 'Worksheet must point at an existing source field')
            target[keys[-1]] = yaml.safe_load(replacement.strip('`'))
            self.write(filename, value)

    def add_home(self, *, practice=False):
        site = self.read('site.yaml')
        site.update(self.excerpt('Separate-guest selections'))
        site['policies']['network'].update(self.excerpt('Browser policy'))
        if practice:
            site['policies']['network']['home_browser']['rules'][0]['source'] = '198.19.30.50'
        self.write('site.yaml', site)
        guest = self.read('guests/home-app.yaml')
        guest['network_policy'].extend(self.excerpt('Browser policy binding'))
        if practice:
            guest['identity'].update(vmid=811, hostname='practice-home')
            guest['interfaces']['primary']['mac'] = '02:00:00:30:00:11'
            guest['interfaces']['primary']['address']['value'] = '198.19.30.11'
            guest['template_file_id'] = 'practice:vztmpl/debian.tar.zst'
        self.write('guests/home-app.yaml', guest)

    def share_home(self):
        site = self.read('site.yaml')
        del site['guests']['home-app']
        self.write('site.yaml', site)
        home = self.read('apps/home.yaml')
        home['guest'] = 'resolver'
        self.write('apps/home.yaml', home)
        guest = self.read('guests/resolver.yaml')
        guest.update(self.excerpt('Shared-guest additions'))
        guest['network_policy'].extend(self.excerpt('Browser policy binding'))
        self.write('guests/resolver.yaml', guest)

    def assert_browser(self, config, address, source='198.19.30.50'):
        rules = [row for row in config['guest']['rules']
                 if row['comment'] == 'Home Assistant from selected browser']
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0], {'direction': 'in', 'proto': 'tcp', 'source': source,
                                  'destination': address + '/32', 'port': '8123', 'interface': 'net0',
                                  'comment': 'Home Assistant from selected browser'})

    def test_complete_copy_runs_documented_compile_packet_and_inspection(self):
        original = {path.relative_to(self.site): path.read_bytes() for path in self.site.rglob('*.yaml')}
        quoted = re.findall(r'^FRAMEWORK_REVISION=([0-9a-f]{40})$', self.page, re.M)
        selected = compiler.workflow_selection(ROOT / '.github/workflows/phase.yml', 'guest-phase.yml')
        self.assertEqual(quoted, [selected['revision']])
        self.assertIn('cp -R "$STACK/examples/personalisation/." "$SITE_ROOT/"', self.page)
        for path in original:
            self.assertIn('../../examples/personalisation/' + str(path), self.page)
        plan = self.plan()
        self.assertEqual(set(plan.pins['site']), {'site.yaml', 'guests/resolver.yaml', 'apps/recursive_dns.yaml'})
        self.assertEqual(self.cli('--check').strip(),
                         'All component guests compile offline; no credentials or targets accessed.')
        output = self.work / 'resolver.json'
        self.cli('--guest', 'resolver', '--output', str(output))
        packet = json.loads(output.read_text())
        self.assertEqual(packet, compiler.lower_plan(plan)['resolver'])
        text = self.inspect(output)
        self.assertIn("'vmid': 610", text)
        self.assertIn('198.18.20.10', text)
        self.assertIn('127.0.0.1', text)
        self.assertIn('5335', text)
        self.assertIn('Data: {}', text)
        before = output.read_bytes()
        with self.assertRaises(FileExistsError):
            self.cli('--guest', 'resolver', '--output', str(output))
        self.assertEqual(output.read_bytes(), before)
        self.assertEqual({path.relative_to(self.site): path.read_bytes() for path in self.site.rglob('*.yaml')}, original)

    def test_practice_worksheet_and_separate_home_bind_real_allocations_and_browser_access(self):
        self.personalise()
        self.add_home(practice=True)
        plan = self.plan()
        packets = compiler.lower_plan(plan)
        self.assertEqual(set(packets), {'resolver', 'home-app'})
        self.assertEqual(set(plan.pins['site']), {'site.yaml', 'guests/resolver.yaml',
            'apps/recursive_dns.yaml', 'guests/home-app.yaml', 'apps/home.yaml'})
        resolver = json.loads(packets['resolver']['files']['site.json'])
        self.assertEqual(resolver['site']['node'], 'practice-node')
        self.assertEqual(resolver['guest']['vmid'], 810)
        self.assertEqual(resolver['guest']['hostname'], 'practice-resolver')
        self.assertEqual(resolver['guest']['storage_id'], 'practice-pool')
        self.assertEqual(resolver['app']['address'], '198.19.30.10')
        home = json.loads(packets['home-app']['files']['site.json'])
        self.assertEqual(home['guest']['vmid'], 811)
        self.assertEqual(home['deployment']['phases'], ['preparation', 'home'])
        self.assert_browser(home, '198.19.30.11')
        self.assertFalse(any(row['comment'] == 'Home Assistant from selected browser'
                             for row in resolver['guest']['rules']))
        app = plan.resolved['apps']['home']
        self.assertEqual(app['profile'], 'homeassistant')
        self.assertEqual(app['role_addresses']['web'], '198.19.30.11')
        self.assertEqual(app['resolved_connections'], {})
        self.assertEqual(plan.resolved['app_dependencies']['home'], [])
        output = self.work / 'home-app.json'
        self.cli('--guest', 'home-app', '--output', str(output))
        text = self.inspect(output)
        self.assertIn("Role addresses: {'web': '198.19.30.11'}", text)
        self.assertIn('/srv/example/apps/homeassistant', text)
        self.assertIn('Home Assistant from selected browser', text)
        self.assertIn('8123', text)

    def test_shared_layout_moves_selected_address_access_and_storage_without_inventing_dependencies(self):
        self.personalise()
        self.add_home(practice=True)
        self.share_home()
        plan = self.plan()
        packets = compiler.lower_plan(plan)
        self.assertEqual(set(packets), {'resolver'})
        self.assertNotIn('guests/home-app.yaml', plan.pins['site'])
        config = json.loads(packets['resolver']['files']['site.json'])
        runtime = json.loads(packets['resolver']['files']['component-runtime.json'])
        self.assertEqual(set(runtime['applications']), {'recursive_dns', 'home'})
        self.assertEqual(config['guest']['memory_mib'], 3072)
        self.assertEqual(config['guest']['volumes']['apps'], {'path': '/srv/example/apps', 'size_gib': 4})
        self.assert_browser(config, '198.19.30.10')
        self.assertEqual(runtime['applications']['home']['role_addresses']['web'], '198.19.30.10')
        self.assertEqual(plan.resolved['app_dependencies'], {'recursive_dns': [], 'home': []})
        for listener in runtime['applications']['recursive_dns']['listeners'].values():
            self.assertEqual(listener['publication_address'], '127.0.0.1')
            self.assertEqual(listener['publish']['port'], 5335)

    def test_taught_guest_rename_updates_all_consumers_and_home_can_be_selected_alone(self):
        self.add_home()
        self.share_home()
        source = self.read('site.yaml')
        source['guests']['dns-box'] = source['guests'].pop('resolver')
        self.write('site.yaml', source)
        for filename in ('apps/recursive_dns.yaml', 'apps/home.yaml'):
            app = self.read(filename)
            app['guest'] = 'dns-box'
            self.write(filename, app)
        self.assertEqual(set(compiler.lower_plan(self.plan())), {'dns-box'})
        source['apps'].pop('recursive_dns')
        self.write('site.yaml', source)
        plan = self.plan()
        self.assertEqual(set(plan.resolved['apps']), {'home'})
        self.assertEqual(set(compiler.lower_plan(plan)), {'dns-box'})

    def test_documented_refusals_reach_exact_compiler_layers_without_mutating_source(self):
        self.add_home()
        fixtures = {path.relative_to(self.site): path.read_bytes() for path in self.site.rglob('*.yaml')}
        cases = [
            ('guests/resolver.yaml', ('interfaces', 'primary', 'address', 'value'),
             '198.19.30.10', 'component.invalid', ()),
            ('apps/recursive_dns.yaml', ('interfaces', 'service'),
             {'interface': 'primary'}, 'component.invalid', ()),
            ('guests/home-app.yaml', ('resources', 'memory_mib'),
             1024, 'component.memory-budget', ()),
            ('apps/home.yaml', ('storage', 'config', 'subpath'),
             '', 'component.storage-initialization-volume', ()),
            ('site.yaml', ('guests', 'resolver', 'source'),
             'guests/missing.yaml', 'component.source', ('guests', 'resolver')),
        ]
        for filename, keys, replacement, code, path in cases:
            with self.subTest(code=code, filename=filename):
                for name, raw in fixtures.items():
                    (self.site / name).write_bytes(raw)
                value = self.read(filename)
                target = value
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = copy.deepcopy(replacement)
                self.write(filename, value)
                before = (self.site / filename).read_bytes()
                expect_refusal(lambda: compiler.lower_plan(self.plan()), ComponentError, code, path)
                self.assertEqual((self.site / filename).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
