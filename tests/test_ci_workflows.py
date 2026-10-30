"""Protect CI triggers, required status names and source-only security boundaries."""

from pathlib import Path
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
        self.assertEqual(source["steps"][0]["with"]["fetch-depth"], "0")
        commands = "\n".join(step.get("run", "") for step in source["steps"])
        self.assertIn("blueprints/workflows.py --stack . --check", commands)
        self.assertIn("blueprints/compile.py --stack . --site site.example.json --check", commands)
        self.assertIn("--suite stack --stack . --fail-under 100", commands)
        self.assertIn('--output "$RUNNER_TEMP/stack-coverage"', commands)
        self.assertIn('.github/scripts/check_history.py --framework framework-source --scanner "$RUNNER_TEMP/homelab-source-tools/gitleaks"', commands)
        self.assertIn(".github/workflows/phase.yml", commands)
        self.assertIn("--require-hashes", commands)
        security = documents["scan-python-security.yml"]["jobs"]["analyze"]
        self.assertEqual(security["permissions"], {"contents": "read", "security-events": "write"})
        init = next(step for step in security["steps"] if "codeql-action/init@" in step.get("uses", ""))
        self.assertEqual(init["with"], {"languages": "python", "build-mode": "none", "queries": "security-extended"})
