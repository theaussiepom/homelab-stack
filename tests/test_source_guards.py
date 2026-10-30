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


    def test_push_cli_bounds_raw_bytes_before_decoding_or_accepting_a_prefix(self):
        """Raw-byte bounds precede newline handling, UTF-8 decoding and Git calls."""
        zero = "0" * 40
        remote = "a" * 40
        padding = 128 - len(f"(delete) {zero} refs/heads/0000 {remote}\n")
        prefix = "".join(
            f"(delete) {zero} refs/heads/{index:04d}{'x' * padding} {remote}\n"
            for index in range(512)
        )
        self.assertEqual(len(prefix.encode("utf-8")), 65536)
        suffix = f"refs/heads/unsigned {'1' * 40} refs/heads/unsigned {zero}\n"
        raw = prefix.encode("utf-8")
        crlf_oversize = raw.replace(b"\n", b"\r\n")
        crlf_exact = b"".join(raw.splitlines(keepends=True)[:508]).replace(b"\n", b"\r\n")
        crlf_exact = crlf_exact.replace(b"refs/heads/0507", b"refs/heads/0507xxxx", 1)
        self.assertEqual(len(crlf_exact), 65536)
        self.assertGreater(len(crlf_oversize), 65536)
        invalid_utf8 = f"(delete) {zero} refs/heads/".encode() + b"\xff " + remote.encode() + b"\n"
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
                HOMELAB_TEST_GIT_CALLS=str(marker), PYTHONIOENCODING="latin-1",
            )
            scenarios = [
                (b"", "origin", None, True),
                (raw, "origin", None, True),
                (crlf_exact, "origin", None, True),
                (raw + suffix.encode(), "origin", "push_update_input_too_large", False),
                (prefix.replace("x", "é").encode(), "origin", "push_update_input_too_large", False),
                (crlf_oversize, "origin", "push_update_input_too_large", False),
                (invalid_utf8, "origin", "UnicodeDecodeError", False),
                (b"", "invalid/remote", "push_to_a_configured_named_remote", False),
            ]
            for translated in (False, True):
                for payload, remote_name, reason, calls_expected in scenarios:
                    with self.subTest(bytes=len(payload), remote=remote_name, reason=reason, translated=translated):
                        marker.unlink(missing_ok=True)
                        command = [sys.executable, str(ROOT / ".githooks/push_guard.py"), remote_name]
                        if translated:
                            # A real byte pipe through a standard TextIOWrapper
                            # configured for universal newline translation.
                            bootstrap = (
                                "import runpy,sys; sys.stdin.reconfigure(newline=None); "
                                "script=sys.argv[1]; sys.argv=sys.argv[1:]; "
                                "runpy.run_path(script,run_name='__main__')"
                            )
                            command = [sys.executable, "-c", bootstrap, *command[1:]]
                        result = subprocess.run(
                            command,
                            input=payload, capture_output=True,
                            env=environment, timeout=15,
                        )
                        if reason is None:
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertEqual(json.loads(result.stdout)["commits_checked"], 0)
                        else:
                            self.assertNotEqual(result.returncode, 0, result.stdout)
                            self.assertEqual(json.loads(result.stderr)["reason"], reason)
                        self.assertEqual(marker.exists(), calls_expected)


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
