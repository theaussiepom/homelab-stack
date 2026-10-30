"""Both public repositories exercise their installed guard copies, without pushes."""

import importlib.util
import json
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


    def test_push_cli_rejects_oversized_input_before_accepting_a_valid_prefix(self):
        """A complete 64-KiB deletion prefix cannot hide unchecked suffix refs."""
        zero = "0" * 40
        remote = "a" * 40
        padding = 128 - len(f"(delete) {zero} refs/heads/0000 {remote}\n")
        prefix = "".join(
            f"(delete) {zero} refs/heads/{index:04d}{'x' * padding} {remote}\n"
            for index in range(512)
        )
        self.assertEqual(len(prefix.encode("utf-8")), 65536)
        suffix = f"refs/heads/unsigned {'1' * 40} refs/heads/unsigned {zero}\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "git-calls"
            executable = root / "git"
            executable.write_text(
                "#!" + sys.executable + "\n"
                "import os,sys\n"
                "with open(os.environ['HOMELAB_TEST_GIT_CALLS'],'a') as calls: calls.write('call\\n')\n"
                "values={'user.name':'fixture','user.email':'123+fixture@users.noreply.github.com'}\n"
                "if len(sys.argv)!=3 or sys.argv[1]!='config': raise SystemExit(2)\n"
                "print(values[sys.argv[2]])\n"
            )
            executable.chmod(0o700)
            environment = dict(
                os.environ, PATH=str(root) + os.pathsep + os.environ["PATH"],
                HOMELAB_TEST_GIT_CALLS=str(marker),
            )
            for payload, accepted in [
                (prefix, True),
                (prefix + suffix, False),
                (prefix.replace("x", "é"), False),
            ]:
                with self.subTest(bytes=len(payload.encode("utf-8")), accepted=accepted):
                    marker.unlink(missing_ok=True)
                    result = subprocess.run(
                        [sys.executable, str(ROOT / ".githooks/push_guard.py"), "origin"],
                        input=payload, capture_output=True, text=True,
                        env=environment, timeout=15,
                    )
                    if accepted:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(json.loads(result.stdout)["commits_checked"], 0)
                        self.assertTrue(marker.is_file())
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertEqual(json.loads(result.stderr)["reason"], "push_update_input_too_large")
                        self.assertFalse(marker.exists())


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
