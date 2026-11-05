"""Maintain the real Markdown example through the selected upstream contracts."""
import copy
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent / 'homelab')).resolve()
sys.path[:0] = [str(FRAMEWORK / 'blueprints')]
import compile as compiler
import component_sources
from component_errors import ComponentError
# Upstream imports must not change stack test discovery precedence.
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT)]

NAMES = {'site.yaml', 'connections/filtering-upstream.yaml',
         'exposures/filtering-dns.yaml'}


def example_files():
    """Extract only the three named YAML fences, never arbitrary paths or code."""
    text = (ROOT / 'docs/examples/local-dns.md').read_text()
    rows = re.findall(r'^## (site\.yaml|connections/filtering-upstream\.yaml|exposures/filtering-dns\.yaml)\n\n```yaml\n(.*?)^```\s*$',
                      text, re.MULTILINE | re.DOTALL)
    if len(rows) != 3 or {name for name, _ in rows} != NAMES:
        raise AssertionError('Keep the three complete named source examples')
    return dict(rows)


def no_native(*args, **kwargs):
    raise AssertionError('Documentation integration cannot contact a target or execute a process')


class DocumentationExamples(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for name, raw in example_files().items():
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            path.write_text(raw)
        for target in ('subprocess.run', 'subprocess.check_output', 'socket.create_connection'):
            boundary = patch(target, side_effect=no_native)
            boundary.start()
            self.addCleanup(boundary.stop)

    def plan(self):
        return compiler.resolve_plan(ROOT, self.root / 'site.yaml', [])

    def test_complete_markdown_sources_match_inline_packet_and_explicit_readiness(self):
        split = self.plan()
        self.assertEqual(set(split.pins['site']), NAMES)
        packets = compiler.lower_plan(split)
        cfg = json.loads(packets['resolver']['files']['site.json'])
        self.assertEqual(cfg['deployment']['phases'],
                         ['preparation', 'recursive_dns', 'filtering'])
        self.assertEqual(split.resolved['app_dependencies']['filtering'], ['recursive_dns'])
        self.assertEqual(split.resolved['apps']['filtering']['resolved_connections']['upstream']['target']['port'], 5335)
        inline, _ = component_sources.site(self.root / 'site.yaml')
        (self.root / 'site.yaml').write_text(yaml.safe_dump(inline, sort_keys=False))
        self.assertEqual(compiler.lower_plan(self.plan()), packets)

    def test_taught_missing_endpoint_and_wrong_loopback_source_refuse_the_intended_layer(self):
        leaf = self.root / 'connections/filtering-upstream.yaml'
        raw = leaf.read_text()
        value = compiler.read(leaf)
        cases = [('missing endpoint', lambda v: v['target'].update(endpoint='missing'), 'component.invalid'),
                 ('physical loopback source', lambda v: v.update(source_interface='service'),
                  'component.connection-target-scope')]
        for name, mutate, code in cases:
            changed = copy.deepcopy(value)
            mutate(changed)
            leaf.write_text(yaml.safe_dump(changed, sort_keys=False))
            before = leaf.read_bytes()
            with self.subTest(case=name), self.assertRaises(ComponentError) as caught:
                self.plan()
            self.assertEqual(caught.exception.code, code)
            self.assertIn('connections.filtering_upstream', str(caught.exception))
            self.assertEqual(leaf.read_bytes(), before)
            leaf.write_text(raw)

    def test_tutorial_revision_is_a_quote_of_the_single_authoritative_selection(self):
        text = (ROOT / 'docs/guides/first-configuration.md').read_text()
        quoted = re.findall(r'^FRAMEWORK_REVISION=([0-9a-f]{40})$', text, re.MULTILINE)
        selected = compiler.workflow_selection(ROOT / '.github/workflows/phase.yml', 'guest-phase.yml')
        self.assertEqual(quoted, [selected['revision']])
        testing = (ROOT / 'docs/testing.md').read_text()
        self.assertIn('COVERAGE_OUTPUT="$COVERAGE_PARENT/stack-coverage"', testing)
        self.assertNotIn('--output "$COVERAGE_PARENT"', testing)

    def test_every_registered_profile_has_one_indexed_reference_page(self):
        library, _ = component_sources.library(ROOT)
        folder = ROOT / 'docs/reference/apps'
        pages = {path.stem for path in folder.glob('*.md')}
        self.assertEqual(pages, set(library['app_profiles']))
        index = (ROOT / 'docs/reference/README.md').read_text()
        for name in pages:
            with self.subTest(profile=name):
                self.assertIn('(apps/' + name + '.md)', index)
                self.assertIn('../../../apps/' + name + '.yaml', (folder / (name + '.md')).read_text())


if __name__ == '__main__':
    unittest.main()
