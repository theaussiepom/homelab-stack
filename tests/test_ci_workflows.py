"""Protect CI triggers, required status names and source-only security boundaries."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / ".github/workflows"
PURPOSES = {
    "validate-stack.yml": ("Validate stack", "Source contracts"),
    "review-pr-dependencies.yml": ("Review PR dependencies", "Dependency review"),
    "scan-python-security.yml": ("Scan Python security", "CodeQL (python)"),
}


def workflows():
    return {
        name: yaml.load((DIRECTORY / name).read_text(), Loader=yaml.BaseLoader)
        for name in PURPOSES
    }


class CiWorkflowTests(unittest.TestCase):
    def test_documentation_conformance_is_nonempty_and_normally_discovered(self):
        # This existing harness remains collected if a documentation module is
        # deleted or emptied. Keep control facts in their source, not here.
        required = [
            'test_component_composition.ComponentCompositionTests.test_standard_home_web_resolves_profile_role_endpoint_and_changed_guest_address',
            'test_component_composition.ComponentCompositionTests.test_explicit_custom_profiles_preserve_archive_data_authentication_and_runtime',
            'test_documentation_examples.DocumentationConformance',
            'test_documentation_examples.DocumentationConformance.test_backup_recovery_catalogue_matches_every_loaded_role_and_capture',
            'test_documentation_examples.DocumentationConformance.test_backup_preparation_and_volume_fragments_follow_presence_controls',
            'test_documentation_examples.DocumentationConformance.test_backup_operational_excerpt_matches_canonical_job_and_real_packet',
            'test_documentation_examples.DocumentationConformance.test_backup_documented_refusals_keep_exact_codes_and_context',
            'test_documentation_examples.DocumentationConformanceMechanism.test_backup_profile_pointer_cannot_be_missing_stale_or_orphaned',
            'test_documentation_examples.DocumentationConformanceMechanism.test_backup_recovery_catalogue_rejects_missing_extra_and_wrong_statements',
            'test_backup_profiles.BackupProfileTests',
            'test_documentation_examples.DocumentationConformanceMechanism',
            'test_documentation_examples.DocumentationExamples',
            'test_documentation_navigation.DocumentationNavigation',
            'test_documentation_navigation.NavigationMechanism',
            'test_documentation_personalisation.PersonalisationWalkthrough',
            'test_documentation_personalisation.PersonalisationWalkthrough.test_practice_worksheet_and_separate_home_bind_real_allocations_and_browser_access',
            'test_documentation_personalisation.PersonalisationWalkthrough.test_shared_layout_moves_selected_address_access_and_storage_without_inventing_dependencies',
        ]
        script = '''import json,sys,unittest
from pathlib import Path
directory=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(directory))
def cases(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from cases(item)
        else:yield item
for name in json.loads(sys.argv[2]):
    # Imported collaborators may prepend their own test/source directory.
    # Always resolve the next required test from the owning repository.
    sys.path[:]=[str(directory), *[part for part in sys.path if part!=str(directory)]]
    loader=unittest.TestLoader()
    named=loader.loadTestsFromName(name)
    if loader.errors or not named.countTestCases():
        raise SystemExit('DOC_COLLECTION: missing or empty '+name)
    selected=list(cases(named))
    for case in selected:
        method=getattr(case,case._testMethodName)
        if (getattr(case,'__unittest_skip__',False) or getattr(method,'__unittest_skip__',False)
                or getattr(method,'__unittest_expecting_failure__',False)):
            raise SystemExit('DOC_COLLECTION: skipped or expected failure '+case.id())
    discovered=loader.discover(str(directory),pattern=name.split('.')[0]+'.py')
    if loader.errors or not {case.id() for case in selected} <= {case.id() for case in cases(discovered)}:
        raise SystemExit('DOC_COLLECTION: not discovered '+name)
'''
        result = subprocess.run([sys.executable, '-c', script, str(ROOT / 'tests'), json.dumps(required)],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);foreign=folder/'upstream';foreign.mkdir()
            (foreign/'test_navigation.py').write_text('import unittest\nclass Wrong(unittest.TestCase):\n def test_wrong(self):pass\n')
            (folder/'test_navigation.py').write_text('import unittest\nclass Owned(unittest.TestCase):\n def test_owned(self):pass\n')
            (folder/'test_first.py').write_text('import sys,unittest\nsys.path.insert(0,'+repr(str(foreign))+')\nclass Contract(unittest.TestCase):\n def test_present(self):pass\n')
            result=subprocess.run([sys.executable,'-c',script,directory,json.dumps(['test_first.Contract','test_navigation.Owned'])],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            module = Path(directory) / 'test_fixture.py'
            for body, names in [
                ('import unittest\nclass Contract(unittest.TestCase):\n    def test_present(self): pass\n', ['test_fixture.Contract']),
                ('import unittest\nclass Contract(unittest.TestCase): pass\n', ['test_fixture.Contract']),
                ("import unittest\n@unittest.skip('disabled')\nclass Contract(unittest.TestCase):\n    def test_disabled(self): pass\n", ['test_fixture.Contract']),
                ('import unittest\nclass Contract(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_disabled(self): pass\n', ['test_fixture.Contract']),
                ('', ['test_removed.Contract']),
            ]:
                module.write_text(body)
                result = subprocess.run([sys.executable, '-c', script, directory, json.dumps(names)],
                    capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode == 0, 'test_present' in body, result.stderr)

    def test_documentation_producer_cannot_be_skipped_or_swallow_a_failure(self):
        workflow = workflows()['validate-stack.yml']
        self.assertIn(workflow['on']['pull_request'], ('', None))
        source = workflow['jobs']['source']
        self.assertNotIn('if', source)
        self.assertNotIn('continue-on-error', source)
        step = next(step for step in source['steps'] if '--suite stack --stack .' in step.get('run', ''))
        self.assertNotIn('if', step)
        self.assertNotIn('continue-on-error', step)
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'python3'
            executable.write_text('#!/bin/sh\nexit 41\n')
            executable.chmod(0o755)
            result = subprocess.run(['/bin/bash', '-e', '-o', 'pipefail', '-c', step['run']], cwd=ROOT,
                env=dict(os.environ, PATH=directory + os.pathsep + os.environ['PATH'], RUNNER_TEMP=directory),
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 41, result.stdout + result.stderr)

    def test_purposes_publish_the_original_required_checks_without_call_prefixes(self):
        self.assertFalse((DIRECTORY / "ci.yml").exists())
        checks = []
        for name, document in workflows().items():
            with self.subTest(workflow=name):
                title, required_check = PURPOSES[name]
                self.assertEqual(document["name"], title)
                self.assertEqual(len(document["jobs"]), 1)
                job = next(iter(document["jobs"].values()))
                self.assertEqual(job["name"], required_check)
                self.assertNotIn("uses", job)
                self.assertNotIn("if", job)
                self.assertTrue(job["steps"])
                self.assertTrue(all(step.get("name") for step in job["steps"]))
                checks.append(job["name"])
        self.assertEqual(set(checks), {"Source contracts", "Dependency review", "CodeQL (python)"})

    def test_pr_dependencies_have_no_main_push_run_or_skipped_placeholder_job(self):
        for name, document in workflows().items():
            with self.subTest(workflow=name):
                if name == "review-pr-dependencies.yml":
                    self.assertEqual(set(document["on"]), {"pull_request"})
                    job = document["jobs"]["dependency-review"]
                    self.assertEqual(job["steps"][0]["with"]["fail-on-severity"], "high")
                    self.assertEqual(job["steps"][0]["with"]["comment-summary-in-pr"], "never")
                else:
                    self.assertEqual(set(document["on"]), {"push", "pull_request"})
                    self.assertEqual(document["on"]["push"], {"branches": ["main"]})
                self.assertNotIn("paths", document["on"].get("push", {}))
                self.assertNotIn("paths-ignore", document["on"].get("push", {}))

    def test_separation_retains_pinned_read_only_full_source_and_coverage_checks(self):
        documents = workflows()
        for name, document in documents.items():
            with self.subTest(workflow=name):
                self.assertEqual(document["permissions"], {"contents": "read"})
                for job in document["jobs"].values():
                    self.assertNotIn("environment", job)
                    self.assertNotIn("secrets", job)
                    for step in job["steps"]:
                        self.assertNotIn("secrets.", str(step))
                        if "uses" in step:
                            self.assertRegex(step["uses"], r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
                            self.assertNotIn("upload-artifact", step["uses"])
                        if step.get("uses", "").startswith("actions/checkout@"):
                            self.assertEqual(step["with"]["persist-credentials"], "false")
        source = documents["validate-stack.yml"]["jobs"]["source"]
        self.assertNotIn("permissions", source)
        # The reconciled authored head includes current main. Preserve its
        # immutable selection, complete history and read-only credentials.
        self.assertEqual(source["steps"][0]["with"], {
            "ref": "${{ github.event.pull_request.head.sha || github.sha }}",
            "fetch-depth": "0", "persist-credentials": "false",
        })
        commands = "\n".join(step.get("run", "") for step in source["steps"])
        self.assertIn("blueprints/workflows.py --stack . --site site.example.yaml --check", commands)
        self.assertIn("blueprints/compile.py --stack . --site site.example.yaml --check", commands)
        self.assertIn("tools/check_boundaries.py --mode stack --root .", commands)
        self.assertIn("blueprints/compile.py --stack . --site examples/site.second.yaml --check", commands)
        self.assertIn("--suite stack --stack . --fail-under 100", commands)
        self.assertIn('--output "$RUNNER_TEMP/stack-coverage"', commands)
        scan = next(step for step in source["steps"] if step["name"] == "Scan source and complete history")
        self.assertEqual(scan["env"], {
            "HEAD_SHA": "${{ github.event.pull_request.head.sha || github.sha }}",
            "BASE_SHA": "${{ github.event.pull_request.base.sha || github.sha }}",
        })
        self.assertEqual(scan["run"], 'python3 .github/scripts/check_history.py --framework framework-source --scanner "$RUNNER_TEMP/homelab-source-tools/gitleaks" --head "$HEAD_SHA" --base "$BASE_SHA"')
        self.assertIn(".github/workflows/phase.yml", commands)
        self.assertIn("--require-hashes", commands)
        security = documents["scan-python-security.yml"]["jobs"]["analyze"]
        self.assertEqual(security["permissions"], {"contents": "read", "security-events": "write"})
        init = next(step for step in security["steps"] if "codeql-action/init@" in step.get("uses", ""))
        self.assertEqual(init["with"], {"languages": "python", "build-mode": "none", "queries": "security-extended"})
