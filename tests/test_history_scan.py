"""Full-history scanning stays complete past 200 commits and fails closed."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get("HOMELAB_FRAMEWORK", ROOT.parent / "homelab")).resolve()
SCRIPT = ROOT / ".github/scripts/check_history.py"
spec = importlib.util.spec_from_file_location("stack_history", SCRIPT)
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)
spec = importlib.util.spec_from_file_location(
    "stack_history_safety", FRAMEWORK / ".github/scripts/source_safety.py"
)
safety = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety)


class FullHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.scratch.name)
        cls.environment = dict(
            os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )
        cls.git("init", "-q")
        empty = cls.git("mktree", data="").strip()
        blob = cls.git("hash-object", "-w", "--stdin", data="Offline public source fixture\n").strip()
        populated = cls.git("mktree", data=f"100644 blob {blob}\tfixture.txt\n").strip()
        parent = None
        for index in range(202):
            parent = cls.git(
                "commit-tree", empty, *(["-p", parent] if parent else []),
                data=f"Synthetic main history {index}\n",
            ).strip()
        side = cls.git("commit-tree", populated, data="Independent fixture root\n").strip()
        side = cls.git("commit-tree", populated, "-p", side, data="Fixture side branch\n").strip()
        head = cls.git("commit-tree", populated, "-p", parent, "-p", side, data="Fixture merge\n").strip()
        cls.git("update-ref", "HEAD", head)
        cls.revisions = cls.git("rev-list", "--reverse", "HEAD").splitlines()

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    @classmethod
    def git(cls, *args, data=None):
        return subprocess.check_output(
            ["git", "-C", str(cls.repo), *args], input=data, text=True,
            env=cls.environment,
        )

    def test_batches_check_every_reachable_identity_and_unique_tree(self):
        checked = []
        trees = []

        def identity(root, revision):
            safety.check_identity(root, revision)
            checked.append(revision)

        def tree(root, revision, scanner):
            trees.append(self.git("rev-parse", revision + "^{tree}").strip())
            return {"scanned_files": 1}

        selected = SimpleNamespace(
            resolve=safety.resolve, git=safety.git, check_identity=identity, scan_tree=tree,
        )
        result = history.scan(self.repo, selected, Path("unused-fixture-scanner"))
        self.assertEqual(len(self.revisions), 205)
        self.assertEqual(checked, self.revisions)
        self.assertEqual(len(trees), len(set(trees)))
        self.assertEqual(result["commits_checked"], 205)
        self.assertEqual(result["unique_trees_checked"], 2)
        self.assertEqual(result["batches"], 3)

    def test_cli_uses_the_selected_real_guard_and_scanner_past_the_old_limit(self):
        scanner = os.environ.get("GITLEAKS_BIN") or subprocess.check_output(
            ["git", "-C", str(ROOT), "config", "--get", "hooks.gitleaksPath"], text=True,
        ).strip()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.repo),
             "--framework", str(FRAMEWORK), "--scanner", scanner],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            "status": "passed", "commits_checked": 205, "unique_trees_checked": 2,
            "head_files": 1, "batches": 3,
        })

    def test_time_limit_and_guard_failures_stop_before_reporting_success(self):
        selected = SimpleNamespace(
            resolve=Mock(return_value="head"),
            git=Mock(side_effect=[b"false\n", b"head\n", b"tree\n"]),
            check_identity=Mock(), scan_tree=Mock(),
        )
        with patch.object(history.time, "monotonic", side_effect=[0, 181]):
            with self.assertRaisesRegex(ValueError, "time budget"):
                history.scan(self.repo, selected, Path("unused-fixture-scanner"))
        selected.check_identity.assert_not_called()
        selected.scan_tree.assert_not_called()
        for failing_stage in ("check_identity", "scan_tree"):
            selected.git = Mock(side_effect=[b"false\n", b"head\n", b"tree\n"])
            selected.check_identity = Mock()
            selected.scan_tree = Mock()
            getattr(selected, failing_stage).side_effect = RuntimeError("fixture guard refusal")
            with self.subTest(stage=failing_stage):
                with self.assertRaisesRegex(RuntimeError, "guard refusal"):
                    history.scan(self.repo, selected, Path("unused-fixture-scanner"))

    def test_cli_refuses_an_actual_shallow_clone_before_any_success_report(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "shallow"
            subprocess.run(
                ["git", "clone", "-q", "--depth=1", self.repo.as_uri(), str(clone)],
                check=True, capture_output=True,
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(clone),
                 "--framework", str(FRAMEWORK), "--scanner", "unused-fixture-scanner"],
                capture_output=True, text=True, timeout=15,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Fetch complete history", result.stderr)
        self.assertNotIn('"status": "passed"', result.stdout)
