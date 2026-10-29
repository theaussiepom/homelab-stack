"""Both public repositories exercise their installed guard copies, without pushes."""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab"))
spec = importlib.util.spec_from_file_location(
    "stack_guard_cases", FRAMEWORK / ".githooks/test_staged_guard.py"
)
cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cases)
cases.GUARD = ROOT / ".githooks/staged_guard.py"


class StackStagedGuardTests(cases.StagedGuardTests):
    """Reuse the behavioral contract against this repository's actual executable."""


class StackPushGuardTests(unittest.TestCase):
    def test_installed_push_guard_passes_the_shared_behavioral_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-q",
                        "-p",
                        "no:cacheprovider",
                        str(FRAMEWORK / "tests/coverage/test_push_guards.py"),
                        str(FRAMEWORK / "tests/coverage/test_guard_protocols.py"),
                        "--basetemp=" + tmp + "/pytest",
                    ],
                    env=dict(os.environ, HOMELAB_TEST_GUARD_ROOT=str(ROOT)),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired as error:
                self.fail(
                    "Shared guard suite exceeded 120 seconds; captured output: "
                    + repr(error.stdout) + "; stderr: " + repr(error.stderr)
                )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class PublicPolicyTests(unittest.TestCase):
    def test_vendor_key_exceptions_bind_exact_public_key_profiles(self):
        import hashlib
        import json

        entries = json.loads((ROOT / ".githooks/reviewed-findings.json").read_text())
        self.assertEqual(
            {entry["path"] for entry in entries},
            {f"guests/{name}/profile.json" for name in ("postgresql", "mariadb", "influxdb")},
        )
        for entry in entries:
            raw = (ROOT / entry["path"]).read_bytes()
            profile = json.loads(raw)
            key = profile["files"]["vendor.asc"]
            repository = profile["config"]["app"]["repositories"][0]
            with self.subTest(path=entry["path"]):
                self.assertEqual(entry["rule"], "generic-api-key")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
                self.assertTrue(key.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----"))
                self.assertEqual(hashlib.sha256(key.encode()).hexdigest(), repository["key_sha256"])
                self.assertIn(repository["key_sha256"], raw.decode().splitlines()[entry["line"] - 1])

    def test_private_file_ignore_rules_preserve_example_exceptions(self):
        private = [".env", ".env.local", ".env.production", "site.json", "archive.p12",
                   "certificate.pfx", "runtime.db", "state.sqlite3", ".coverage", ".coverage.fixture"]
        examples = [".env.example", ".env.sample", ".env.template", "site.example.json"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".gitignore").write_bytes((ROOT / ".gitignore").read_bytes())
            result = subprocess.run(
                ["git", "-C", str(root), "-c", "core.excludesFile=/dev/null",
                 "check-ignore", "--no-index", "--stdin"],
                input="\n".join(private + examples) + "\n", capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(private))
