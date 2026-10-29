"""CI uses the same generator check as local development; it never repairs drift."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
GENERATOR = FRAMEWORK / "blueprints/workflows.py"


def generate(stack, check=False):
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--stack",
            str(stack),
            *(["--check"] if check else []),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )


class GeneratedWorkflowTests(unittest.TestCase):
    def test_checked_in_workflows_match_the_selected_catalogue_and_composition(self):
        result = generate(ROOT, check=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_detects_drift_without_writing_and_generation_repairs_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            shutil.copyfile(ROOT / "stack.json", root / "stack.json")
            for source in (ROOT / ".github/workflows").glob("*.yml"):
                shutil.copyfile(source, workflows / source.name)
            # phase.yml remains the single deliberate framework selection.
            phase = (workflows / "phase.yml").read_bytes()
            ci = (workflows / "ci.yml").read_bytes()
            path = workflows / "guest-mariadb.yml"
            path.write_bytes(path.read_bytes() + b"\n# unintended manual edit\n")
            before = {p.name: p.read_bytes() for p in workflows.iterdir()}
            result = generate(root, check=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("guest-mariadb.yml", result.stdout + result.stderr)
            self.assertEqual(
                before, {p.name: p.read_bytes() for p in workflows.iterdir()}
            )
            result = generate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(generate(root, check=True).returncode, 0)
            self.assertEqual((workflows / "phase.yml").read_bytes(), phase)
            self.assertEqual((workflows / "ci.yml").read_bytes(), ci)
