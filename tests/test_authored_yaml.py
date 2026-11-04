"""Authored YAML and legacy JSON compile to the same deployment packets."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
sys.path.insert(0, str(FRAMEWORK/'blueprints'))
spec = importlib.util.spec_from_file_location('yaml_stack_compiler', FRAMEWORK/'blueprints/compile.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
import workflows
# Upstream imports add their test directory; keep stack discovery first.
sys.path.insert(0, str(ROOT/'tests'))


class AuthoredYamlTests(unittest.TestCase):
    def test_authored_profiles_use_yaml_with_typed_fields_and_exact_text_values(self):
        for guest in c.manifest(ROOT)['guests']:
            path = c.profile_path(ROOT, guest)
            profile = c.read(path)
            with self.subTest(guest=guest):
                self.assertEqual(path.suffix, '.yaml')
                self.assertIs(type(profile['config']['guest']['started']), bool)
                self.assertIs(type(profile['config']['guest']['memory_mib']), int)
                self.assertIs(type(profile['config']['guest']['vmid']), str)
                self.assertTrue(all(type(value) is str for value in profile['files'].values()))
                if 'vendor.asc' in profile['files']:
                    self.assertTrue(profile['files']['vendor.asc'].endswith('\n'))
                    self.assertIn('  vendor.asc: |\n', path.read_text())

    def test_both_site_formats_preserve_all_packets_runtime_bytes_and_workflow_models(self):
        examples = ('site.example.yaml', 'examples/site.second.yaml')
        with tempfile.TemporaryDirectory() as directory:
            legacy = Path(directory).resolve()/'stack'
            shutil.copytree(ROOT, legacy, ignore=shutil.ignore_patterns('.git', '.work', '__pycache__'))
            authored = [*(ROOT/'guests').glob('*/profile.yaml'), *(ROOT/name for name in examples)]
            self.assertEqual(len(authored), 16)
            for source in authored:
                path = legacy/source.relative_to(ROOT)
                path.with_suffix('.json').write_text(json.dumps(c.read(source))+'\n')
                path.unlink()
            for example in examples:
                yaml_site = c.read(ROOT/example)
                json_site = c.read((legacy/example).with_suffix('.json'))
                for monitored in (False, True):
                    for disabled in ([], ['music']):
                        with self.subTest(example=example, monitored=monitored, disabled=disabled):
                            left = c.merge(yaml_site, {'zabbix': None}) if monitored else yaml_site
                            right = c.merge(json_site, {'zabbix': None}) if monitored else json_site
                            actual = c.compile_stack(ROOT, left, disabled)
                            previous = c.compile_stack(legacy, right, disabled)
                            self.assertEqual(c.encoded(actual), c.encoded(previous))
                            self.assertEqual(len(actual), 14 if monitored else 13)
                            self.assertEqual(sum(len(row['files']) for row in actual.values()), 40 if monitored else 38)
            self.assertEqual(workflows.models(ROOT, monitored=True), workflows.models(legacy, monitored=True))


if __name__ == '__main__':
    unittest.main()
