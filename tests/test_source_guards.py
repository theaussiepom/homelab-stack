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
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
