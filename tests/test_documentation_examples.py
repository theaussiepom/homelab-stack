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
    """Read the three canonical files linked by the worked guide."""
    guide = (ROOT / 'docs/examples/local-dns.md').read_text()
    for name in NAMES:
        if '../../examples/catalogue/local-dns/' + name not in guide:
            raise AssertionError('Keep the complete worked-source links')
    return {name: (ROOT / 'examples/catalogue/local-dns' / name).read_text()
            for name in NAMES}


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

    def test_complete_documented_sources_match_inline_packet_and_explicit_readiness(self):
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




# Source-backed documentation conformance remains inside normal source discovery.
import component_types
import component_backup
import component_foundations
from documentation_contracts import (DocumentationError, assert_excerpt, documented_rows,
    expect_refusal, inventory, mapped_mqtt_property_inventory, mqtt_property_inventory, read_excerpt, reconcile, reconcile_recovery, registration_rows, table_cells, typed_equal, validate_definition_pointers)
from documentation_records import DEFINITIONS, MQTT_PROPERTIES, REGISTRATIONS


class DocumentationConformance(unittest.TestCase):
    def setUp(self):
        for target in ('subprocess.run', 'subprocess.check_output', 'socket.create_connection'):
            boundary = patch(target, side_effect=no_native)
            boundary.start()
            self.addCleanup(boundary.stop)
        self.library, _ = component_sources.library(ROOT)

    def test_all_registered_definitions_have_bidirectional_typed_declaration_records(self):
        self.assertEqual({path.stem for path in (ROOT / 'docs/reference/templates').glob('*.md')},
                         set(self.library['guest_templates']))
        registration = compiler.read(ROOT / 'stack.json')
        validate_definition_pointers(registration, DEFINITIONS, ROOT)
        total = 0
        for (group, name), (source, document) in DEFINITIONS.items():
            with self.subTest(declaration=f'{group}.{name}'):
                value = self.library[group][name]
                {'app_profiles': component_types.profile, 'guest_templates': component_types.template,
                 'backup_profiles': component_backup.profile}[group](value)
                total += reconcile(value, (ROOT / document).read_text(), source, document)
        self.assertGreater(total, 0)

    def test_registered_shared_declarations_have_no_missing_or_orphan_catalogue_rows(self):
        self.assertEqual(set(self.library) - {'schema', 'kind'},
                         {'app_profiles', 'guest_templates', 'policies'} |
                         {group for group in REGISTRATIONS if not group.startswith('policies.')})
        self.assertEqual(set(self.library['policies']),
                         {group.removeprefix('policies.') for group in REGISTRATIONS
                          if group.startswith('policies.')})
        accepted = {}
        for group in ('software', 'runtime_profiles', 'health_profiles',
                      'authentication_profiles', 'monitoring_profiles', 'assets', 'bundles', 'backup_profiles'):
            accepted[group] = tuple(self.library[group])
        for group, values in self.library['policies'].items():
            accepted['policies.' + group] = tuple(values)
        self.assertEqual({k: set(v) for k, v in REGISTRATIONS.items()},
                         {k: set(v) for k, v in accepted.items()})
        page = (ROOT / 'docs/reference/software-and-runtime.md').read_text()
        rows = registration_rows(page)
        for group, names in REGISTRATIONS.items():
            self.assertEqual(len(names), len(set(names)), group + ' duplicate registration pointer')
        expected = {group + '.' + name for group, names in accepted.items() for name in names}
        self.assertTrue(expected)
        self.assertEqual(len(rows), len(set(rows)))
        self.assertEqual(set(rows), expected)

    def test_optional_mqtt_properties_reconcile_actual_validator_mapping_and_documented_rows(self):
        accepted = mapped_mqtt_property_inventory(
            FRAMEWORK, MQTT_PROPERTIES, component_foundations.validate)
        page = (ROOT / 'docs/reference/apps/mqtt.md').read_text()
        section = re.search(r'^## Application properties\n(.*?)(?=^## )', page, re.M | re.S)
        self.assertIsNotNone(section)
        rows = []
        for line in section.group(1).splitlines():
            if not line.startswith('|'):
                continue
            first = table_cells(line)[0]
            if first == 'Property' or re.fullmatch(r'[-: ]+', first):
                continue
            match = re.fullmatch(r'`([^`]+)`', first)
            self.assertIsNotNone(match, 'unclassified supported MQTT property row')
            rows.append(match.group(1))
        self.assertTrue(rows)
        self.assertEqual(len(rows), len(set(rows)))
        self.assertEqual(accepted, set(MQTT_PROPERTIES))
        self.assertEqual(accepted, set(rows))
        for _, _, document, anchor in MQTT_PROPERTIES.values():
            self.assertEqual((ROOT / document).read_text().count('<a id="' + anchor + '"></a>'), 1)

    def source_plan(self, value):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory).resolve() / 'site.json'
            source.write_text(json.dumps(value))
            backup=value.get('backup')
            if isinstance(backup,dict) and 'recovery_public_key' in backup:
                public=source.parent/backup['recovery_public_key']['source']
                public.parent.mkdir(parents=True)
                public.write_bytes((ROOT/backup['recovery_public_key']['source']).read_bytes())
            plan = compiler.resolve_plan(ROOT, source, [])
            return plan, compiler.lower_plan(plan)

    def test_mqtt_complete_excerpt_endpoints_and_required_file_probe_floor(self):
        source, _ = component_sources.site(ROOT / 'examples/catalogue/messaging-radio.yaml')
        page = (ROOT / 'docs/reference/apps/mqtt.md').read_text()
        assert_excerpt(page, 'Complete broker entry', {'broker': source['apps']['broker']}, yaml.safe_load)
        profile = self.library['app_profiles']['mqtt']
        self.assertIs(profile['secrets']['probe']['required'], False)
        plan, packets = self.source_plan(source)
        broker = plan.resolved['apps']['broker']
        self.assertIn(broker['guest'], packets)
        for endpoint in ('backend', 'frontend'):
            self.assertEqual(plan.resolved['endpoints']['app/broker/' + endpoint]['port'], profile['listeners']['mqtt']['port'])
            self.assertEqual(plan.resolved['endpoints']['app/broker/' + endpoint]['address'],
                             broker['role_addresses'][endpoint])
        for change in ('missing', 'environment'):
            changed = copy.deepcopy(source)
            if change == 'missing':
                changed['apps']['broker'].pop('secrets')
            else:
                changed['secret_sources']['broker_probe'] = {'type': 'environment', 'name': 'BROKER_PROBE'}
            with self.subTest(change=change):
                expect_refusal(lambda: self.source_plan(changed), ComponentError,
                               'component.secret-required', 'apps.broker.properties')

    def test_mqtt_property_refusals_reach_the_documented_code_and_context(self):
        source, _ = component_sources.site(ROOT / 'examples/catalogue/messaging-radio.yaml')
        for properties, code in (({'password_file': '/elsewhere/passwords'}, 'component.property'),
                                 ({'port': 1884}, 'component.fields')):
            changed = copy.deepcopy(source)
            changed['apps']['broker']['properties'] = properties
            with self.subTest(properties=properties):
                expect_refusal(lambda: self.source_plan(changed), ComponentError, code,
                               'apps.broker.properties')

    def test_docker_omission_partial_override_and_exact_refusals(self):
        source, _ = component_sources.site(ROOT / 'site.example.yaml')
        guest = source['guests']['resolver']
        guest['template'] = 'docker'
        for field in ('resources', 'startup', 'security'):
            guest.pop(field, None)
        template = self.library['guest_templates']['docker']
        inherited, _ = self.source_plan(source)
        for field in ('resources', 'startup', 'security'):
            self.assertEqual(inherited.resolved['guests']['resolver'][field], template[field])
        page = (ROOT / 'docs/reference/templates/docker.md').read_text()
        fragment = read_excerpt(page, 'Partial override', yaml.safe_load)
        changed = copy.deepcopy(source)
        changed['guests']['resolver'].update(fragment)
        resolved, _ = self.source_plan(changed)
        actual = resolved.resolved['guests']['resolver']
        expected = dict(template['resources'], **fragment['resources'])
        self.assertEqual(actual['resources'], expected)
        self.assertEqual(actual['startup'], template['startup'])
        self.assertEqual(actual['security'], template['security'])
        for field, value, code in (('resources', {'memory_mib': 255}, 'component.integer'),
                                   ('security', {'protection': False}, 'component.invalid')):
            changed = copy.deepcopy(source)
            changed['guests']['resolver'][field] = value
            with self.subTest(field=field):
                expect_refusal(lambda: self.source_plan(changed), ComponentError, code, 'guests.resolver')


    def test_backup_recovery_catalogue_matches_every_loaded_role_and_capture(self):
        page = (ROOT / 'docs/reference/backup-coverage.md').read_text()
        count = reconcile_recovery(self.library['app_profiles'], page)
        self.assertEqual(count, sum(len(p.get('storage', {}))
                                    for p in self.library['app_profiles'].values()))

    def test_backup_preparation_and_volume_fragments_follow_presence_controls(self):
        page = (ROOT / 'docs/backup.md').read_text()
        selection = read_excerpt(page, 'Select client preparation', yaml.safe_load)
        self.assertEqual(selection, {'backup': None})
        source, _ = component_sources.site(ROOT / 'site.example.yaml')
        original, _ = self.source_plan(source)
        self.assertNotIn('backup', original.resolved['guests']['resolver'])
        volume = read_excerpt(page, 'Protect managed volumes explicitly', yaml.safe_load)
        inventories = []
        for value in (selection['backup'], {}, {'profile': 'pbs-client'}):
            changed = copy.deepcopy(source)
            changed['backup'] = value
            shared, _ = self.source_plan(changed)
            self.assertNotIn('backup', shared.resolved['guests']['resolver'])
            changed['guests']['resolver']['backup'] = None
            changed['guests']['resolver'].update(copy.deepcopy(volume))
            plan, packets = self.source_plan(changed)
            cfg = json.loads(packets['resolver']['files']['site.json'])
            self.assertEqual(cfg['deployment']['phases'][-1], 'pbs-agent')
            self.assertTrue(cfg['guest']['volumes']['application']['backup'])
            self.assertFalse(cfg['guest']['volumes']['cache']['backup'])
            self.assertNotIn('job', cfg['app']['backup'])
            self.assertNotIn('backup-group.json', packets['resolver']['files'])
            inventories.append(plan.resolved['guests']['resolver']['backup'])
        self.assertTrue(all(value == inventories[0] for value in inventories))

    def test_backup_operational_excerpt_matches_canonical_job_and_real_packet(self):
        source, _ = component_sources.site(ROOT / 'site.backup.example.yaml')
        page = (ROOT / 'docs/backup.md').read_text()
        assert_excerpt(page, 'Operational job example', {'backup': source['backup']}, yaml.safe_load)
        self.assertIn('../site.backup.example.yaml', page)
        self.assertIn('../examples/backup/guests/resolver.yaml', page)
        plan, packets = self.source_plan(source)
        cfg = json.loads(packets['resolver']['files']['site.json'])
        job = cfg['app']['backup']['job']
        self.assertEqual(job['schedule'], source['backup']['job']['schedule'])
        self.assertIn('backup-group.json', packets['resolver']['files'])
        self.assertFalse(cfg['guest']['volumes']['backup-stage']['backup'])
        self.assertEqual(job['staging']['path'], source['guests']['resolver']['volumes']['backup-stage']['path'])
        self.assertEqual(set(plan.resolved['guests']), set(source['backup']['job']['clients']))

    def test_backup_documented_refusals_keep_exact_codes_and_context(self):
        source, _ = component_sources.site(ROOT / 'site.example.yaml')
        page = (ROOT / 'docs/backup.md').read_text()
        for value, code in ((True, 'component.fields'), (False, 'component.fields'),
                            ({'profile': 'missing'}, 'component.backup-profile-selection')):
            changed = copy.deepcopy(source)
            changed['backup'] = value
            with self.subTest(selection=value):
                self.assertIn('`' + code + '`', page)
                expect_refusal(lambda: self.source_plan(changed), ComponentError, code, ())
        changed = copy.deepcopy(source)
        changed['backup'] = None
        changed['guests']['resolver'].update(read_excerpt(page, 'Protect managed volumes explicitly', yaml.safe_load))
        changed['guests']['resolver']['volumes']['application']['backup'] = True
        expect_refusal(lambda: self.source_plan(changed), ComponentError,
                       'component.backup-presence', 'guests.resolver.volumes.application')
        operational, _ = component_sources.site(ROOT / 'site.backup.example.yaml')
        operational['guests']['resolver']['volumes']['backup-stage']['backup'] = None
        expect_refusal(lambda: self.source_plan(operational), ComponentError,
                       'component.backup-staging-volume', ())


class DocumentationConformanceMechanism(unittest.TestCase):
    SOURCE = {'startup': {'boot_order': 50, 'started': True}}
    PAGE = '''## Declaration records

| Declaration path | Selected value |
| --- | --- |
| <a id="declaration-startup"></a>`startup` | `object` |
| <a id="declaration-startup-boot-order"></a>`startup.boot_order` | `50` |
| <a id="declaration-startup-started"></a>`startup.started` | `true` |
'''

    def check(self, source=None, page=None):
        return reconcile(self.SOURCE if source is None else source,
                         self.PAGE if page is None else page, 'fixture.yaml', 'fixture.md')

    def test_missing_stale_new_orphan_and_duplicate_declaration_rows_fail(self):
        self.assertEqual(self.check(), 3)
        new_source = copy.deepcopy(self.SOURCE)
        new_source['startup']['new_accepted_field'] = True
        orphan = '| <a id="declaration-phantom"></a>`phantom` | `false` |\n'
        row = self.PAGE.splitlines()[-1] + '\n'
        removed_source = copy.deepcopy(self.SOURCE)
        removed_source['startup'].pop('started')
        cases = [dict(source=new_source), dict(source=removed_source),
                 dict(page=self.PAGE + orphan), dict(page=self.PAGE.replace(row, '')),
                 dict(page=self.PAGE + row),
                 dict(page=self.PAGE.replace('declaration-startup-started', 'declaration-startup'))]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(DocumentationError):
                self.check(**case)

    def test_definition_pointer_missing_stale_source_document_and_registration_fail(self):
        registration = {'app_profiles': {'fixture': {'source': 'apps/fixture.yaml'}},
                        'guest_templates': {}, 'backup_profiles': {}}
        definitions = {('app_profiles', 'fixture'): ('apps/fixture.yaml', 'docs/fixture.md')}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for locator in definitions[('app_profiles', 'fixture')]:
                path = root / locator
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture')
            validate_definition_pointers(registration, definitions, root)
            for changed in ({},
                            {('app_profiles', 'removed'): ('apps/fixture.yaml', 'docs/fixture.md')},
                            {('app_profiles', 'fixture'): ('apps/missing.yaml', 'docs/fixture.md')},
                            {('app_profiles', 'fixture'): ('apps/fixture.yaml', 'docs/missing.md')}):
                with self.subTest(mapping=changed), self.assertRaises(DocumentationError):
                    validate_definition_pointers(registration, changed, root)
            added = copy.deepcopy(registration)
            added['app_profiles']['new'] = {'source': 'apps/fixture.yaml'}
            with self.assertRaisesRegex(DocumentationError, 'DOC_INVENTORY'):
                validate_definition_pointers(added, definitions, root)

    def test_source_and_document_drift_and_strict_boolean_number_string_comparison(self):
        changed = copy.deepcopy(self.SOURCE)
        changed['startup']['boot_order'] = 51
        for case in (dict(source=changed), dict(page=self.PAGE.replace('`50`', '`20`')),
                     dict(page=self.PAGE.replace('`50`', '`"50"`')),
                     dict(page=self.PAGE.replace('`true`', '`1`'))):
            with self.subTest(case=case), self.assertRaisesRegex(DocumentationError, 'DOC_FACT_DRIFT'):
                self.check(**case)
        self.assertFalse(typed_equal({'x': [True]}, {'x': [1]}))

    def test_empty_and_unclassified_inventory_and_ambiguous_value_fail_closed(self):
        for case in (dict(source={}), dict(page='## Declaration records\n'),
                     dict(source={'unexpected.key': 1}),
                     dict(page=self.PAGE.replace('`50`', 'fifty')),
                     dict(page=self.PAGE + self.PAGE)):
            with self.subTest(case=case), self.assertRaises(DocumentationError):
                self.check(**case)
        self.assertEqual(table_cells('| `a|b` | escaped\\|pipe |'), ['`a|b`', 'escaped|pipe'])

    def test_shared_registration_rows_cannot_hide_missing_anchors_or_orphan_rows(self):
        page = '| Selection | Effect |\n| --- | --- |\n| <a id="registration-software-example"></a>`software.example` | selected |\n'
        self.assertEqual(registration_rows(page), {'software.example'})
        for changed in (page + '| `software.orphan` | added |\n',
                        page + page.splitlines()[-1] + '\n',
                        '| Selection | Effect |\n| --- | --- |\n'):
            with self.subTest(changed=changed), self.assertRaises(DocumentationError):
                registration_rows(changed)

    def test_validator_inventory_detects_new_fields_and_refuses_unclassified_shapes(self):
        source = "def validate(adapter, value):\n    if adapter == 'mqtt':\n        closed(value, (), ('password_file',))\n"
        self.assertEqual(mqtt_property_inventory(source), {'password_file'})
        added = source.replace("('password_file',)", "('password_file', 'new_control')")
        self.assertNotEqual(mqtt_property_inventory(added), set(MQTT_PROPERTIES))
        for changed in (source.replace("('password_file',)", 'dynamic_fields'),
                        source.replace("('password_file',)", '()'),
                        source.replace("closed(value", "closed(value['nested']")):
            with self.subTest(changed=changed), self.assertRaises(DocumentationError):
                mqtt_property_inventory(changed)

    def test_conditional_closed_declaration_cannot_hide_an_accepted_new_branch(self):
        source = ("def validate(adapter, value):\n"
                  "    if adapter == 'mqtt':\n"
                  "        if 'new_control' not in value:\n"
                  "            closed(value, (), ('password_file',))\n")
        namespace = {'closed': component_sources.closed}
        exec(compile(source, '<conditional-mqtt-fixture>', 'exec'), namespace)
        # The fixture uses the actual closed-object validator, but bypasses it
        # for this newly accepted branch. Extraction must refuse that shape.
        self.assertIsNone(namespace['validate']('mqtt', {'new_control': 1}))
        with self.assertRaisesRegex(DocumentationError, 'DOC_UNCLASSIFIED'):
            mqtt_property_inventory(source)

    def test_stale_mqtt_source_file_and_owner_pointers_fail_against_selected_validator(self):
        self.assertEqual(mapped_mqtt_property_inventory(
            FRAMEWORK, MQTT_PROPERTIES, component_foundations.validate), set(MQTT_PROPERTIES))
        for index, replacement in ((0, 'missing.py'), (1, 'removed')):
            changed = dict(MQTT_PROPERTIES)
            record = list(changed['password_file'])
            record[index] = replacement
            changed['password_file'] = tuple(record)
            with self.subTest(pointer=index), self.assertRaisesRegex(DocumentationError, 'DOC_STALE_SOURCE'):
                mapped_mqtt_property_inventory(FRAMEWORK, changed, component_foundations.validate)

    def test_refusal_requires_the_exact_structured_path(self):
        def refusal(path):
            def action():
                raise ComponentError('component.invalid', path)
            return action
        expect_refusal(refusal(('guests', 'resolver')), ComponentError,
                       'component.invalid', 'guests.resolver')
        for wrong in (('guests', 'resolver_extra'), ('guests', 'resolver', 'resources')):
            with self.subTest(path=wrong), self.assertRaisesRegex(DocumentationError, 'DOC_WRONG_REFUSAL'):
                expect_refusal(refusal(wrong), ComponentError, 'component.invalid', 'guests.resolver')

    def test_excerpt_and_expected_refusal_checks_cannot_pass_on_stale_or_wrong_results(self):
        page = '## Example\n\n```yaml\nx: 1\n```\n'
        assert_excerpt(page, 'Example', {'x': 1}, yaml.safe_load)
        for ambiguous in (page + '\n```yaml\nx: 2\n```\n', page + page):
            with self.subTest(page=ambiguous), self.assertRaisesRegex(DocumentationError, 'DOC_AMBIGUOUS'):
                assert_excerpt(ambiguous, 'Example', {'x': 1}, yaml.safe_load)
            with self.assertRaisesRegex(DocumentationError, 'DOC_AMBIGUOUS'):
                read_excerpt(ambiguous.replace('## Example', '## Partial override'),
                             'Partial override', yaml.safe_load)
        with self.assertRaisesRegex(DocumentationError, 'DOC_STALE_EXCERPT'):
            assert_excerpt(page, 'Example', {'x': 2}, yaml.safe_load)
        with self.assertRaisesRegex(DocumentationError, 'DOC_UNEXPECTED_SUCCESS'):
            expect_refusal(lambda: None, ComponentError, 'component.invalid', 'apps.broker')
        def wrong():
            raise ComponentError('component.fields')
        with self.assertRaisesRegex(DocumentationError, 'DOC_WRONG_REFUSAL'):
            expect_refusal(wrong, ComponentError, 'component.invalid', 'apps.broker')


    def test_backup_profile_pointer_cannot_be_missing_stale_or_orphaned(self):
        registration = compiler.read(ROOT / 'stack.json')
        key = ('backup_profiles', 'pbs-client')
        for replacement in (None, ('backup/missing.yaml', DEFINITIONS[key][1]),
                            (DEFINITIONS[key][0], 'docs/reference/missing.md')):
            changed = dict(DEFINITIONS)
            if replacement is None:
                changed.pop(key)
            else:
                changed[key] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(DocumentationError):
                validate_definition_pointers(registration, changed, ROOT)
        removed = copy.deepcopy(registration)
        removed['backup_profiles'].pop('pbs-client')
        with self.assertRaisesRegex(DocumentationError, 'DOC_INVENTORY'):
            validate_definition_pointers(removed, DEFINITIONS, ROOT)

    def test_backup_recovery_catalogue_rejects_missing_extra_and_wrong_statements(self):
        profiles = {
            'fixture': {'storage': {'data': {'target': '/data'}, 'logs': {'target': '/logs'}},
                        'backup': {'include': {'data': {'category': 'state', 'capture': 'application-export'}},
                                   'exclude': {'logs': 'transient'}}},
            'empty': {'storage': {}, 'backup': {'include': {}, 'exclude': {}}}}
        page = ('## Exact profile storage dispositions\n\n### fixture\n\n'
                '| Role / app target | Disposition | Capture requirement |\n| --- | --- | --- |\n'
                '| `data` — `/data` | state | application-export |\n'
                '| `logs` — `/logs` | Excluded: transient | None |\n\n'
                '### empty\n\nNo declared storage roles.\n')
        self.assertEqual(reconcile_recovery(profiles, page), 2)
        row = '| `logs` — `/logs` | Excluded: transient | None |\n'
        cases = [page.replace('/data', '/wrong'), page.replace('application-export', 'files'),
                 page.replace('Excluded: transient', 'Excluded: rebuildable'),
                 page.replace(row, ''), page.replace(row, row + row),
                 page.replace('### empty', '### unknown'), page + '\n### empty\nNo declared storage roles.\n',
                 page.replace('No declared storage roles.', ''),
                 page.replace('| state | application-export |', '| state | application-export | extra |'),
                 page.replace('| Role / app target | Disposition | Capture requirement |', '|'),
                 page.replace('| Role / app target | Disposition | Capture requirement |',
                              '| Role / app target | Disposition | Capture requirement | extra |'),
                 '## Exact profile storage dispositions\n']
        for changed in cases:
            with self.subTest(changed=changed), self.assertRaises(DocumentationError):
                reconcile_recovery(profiles, changed)
        with self.assertRaises(DocumentationError):
            reconcile_recovery({}, page)


if __name__ == '__main__':
    unittest.main()
