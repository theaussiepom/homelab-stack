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

    def pr_checkout(self, directory, *, private_merge=False, forged_ancestor=False,
                    diverged_target=False, private_target=False, forged_target=False,
                    forged_author=False):
        """Build authored commits plus a platform-style merge without changing this checkout."""
        repository = Path(directory) / "pull-request"
        repository.mkdir()

        def git(*args, data=None, platform_identity=False, invalid_committer=False,
                reserved_author=False):
            environment = dict(self.environment)
            if platform_identity:
                environment["GIT_AUTHOR_EMAIL"] = safety.OWN_EMAIL
            if invalid_committer:
                environment["GIT_COMMITTER_EMAIL"] = safety.OWN_EMAIL
            if reserved_author:
                environment["GIT_AUTHOR_NAME"] = safety.OWN_NAME
            return subprocess.check_output(
                ["git", "-C", str(repository), *args], input=data, text=True,
                env=environment,
            ).strip()

        git("init", "-q")
        blob = git("hash-object", "-w", "--stdin", data="Public source fixture\n")
        authored_tree = git("mktree", data=f"100644 blob {blob}\tfixture.txt\n")
        ancestor = git("commit-tree", authored_tree, data="Authored ancestor\n",
                       invalid_committer=forged_ancestor, reserved_author=forged_author)
        authored = git("commit-tree", authored_tree, "-p", ancestor, data="Authored head\n")
        target = ancestor
        if diverged_target:
            target_tree = authored_tree
            if private_target:
                target_tree = git("mktree", data=(
                    f"100644 blob {blob}\t.env\n100644 blob {blob}\tfixture.txt\n"
                ))
            target = git("commit-tree", target_tree, "-p", ancestor,
                         data="Target-only ancestor\n", invalid_committer=forged_target)
            target = git("commit-tree", authored_tree, "-p", target, data="Clean target head\n")
        leaf = ".env" if private_merge else "merge-only.txt"
        merged_tree = git("mktree", data=(
            f"100644 blob {blob}\tfixture.txt\n100644 blob {blob}\t{leaf}\n"
        ))
        merge = git("commit-tree", merged_tree, "-p", target, "-p", authored,
                    data="Platform merge\n", platform_identity=True)
        git("update-ref", "HEAD", merge)
        return repository, authored, merge

    def pr_scan(self, repository, *arguments):
        scanner = os.environ.get("GITLEAKS_BIN") or subprocess.check_output(
            ["git", "-C", str(ROOT), "config", "--get", "hooks.gitleaksPath"], text=True,
        ).strip()
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(repository),
             "--framework", str(FRAMEWORK), "--scanner", scanner, *arguments],
            capture_output=True, text=True, timeout=60,
        )

    def test_pr_head_accepts_author_display_label_and_scans_the_distinct_merged_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            repository, authored, merge = self.pr_checkout(directory)
            before = self.pr_scan(repository)
            self.assertEqual(before.returncode, 0, before.stderr)
            self.assertEqual(json.loads(before.stdout)["commits_checked"], 3)
            safety.check_identity(repository, merge)
            after = self.pr_scan(repository, "--head", authored)
            self.assertEqual(after.returncode, 0, after.stderr)
            self.assertEqual(json.loads(after.stdout), {
                "status": "passed", "commits_checked": 2, "unique_trees_checked": 2,
                "head_files": 2, "batches": 1,
            })

    def test_pr_head_keeps_merged_tree_private_path_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            repository, authored, _ = self.pr_checkout(directory, private_merge=True)
            result = self.pr_scan(repository, "--head", authored)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private_file_path", result.stderr)
        self.assertNotIn('"status": "passed"', result.stdout)

    def test_pr_head_keeps_authored_ancestor_identity_and_invalid_ref_refusals(self):
        with tempfile.TemporaryDirectory() as directory:
            repository, authored, _ = self.pr_checkout(directory, forged_ancestor=True)
            for head, reason in ((authored, "maintainer_identity_mismatch"),
                                 ("refs/pull/25/head", "invalid_revision")):
                with self.subTest(reason=reason):
                    result = self.pr_scan(repository, "--head", head)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(reason, result.stderr)
                    self.assertNotIn('"status": "passed"', result.stdout)

    def test_pr_head_keeps_reserved_author_handle_wrong_email_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            repository, authored, _ = self.pr_checkout(directory, forged_author=True)
            result = self.pr_scan(repository, "--head", authored)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("maintainer_identity_mismatch", result.stderr)
        self.assertNotIn('"status": "passed"', result.stdout)

    def test_branch_union_covers_clean_divergence_and_deduplicates_push_history(self):
        with tempfile.TemporaryDirectory() as directory:
            repository, authored, merge = self.pr_checkout(directory, diverged_target=True)
            target = subprocess.check_output(
                ["git", "-C", str(repository), "rev-parse", merge + "^1"], text=True,
            ).strip()
            for base, expected in ((target, 4), (authored, 2)):
                with self.subTest(base_is_head=base == authored):
                    result = self.pr_scan(repository, "--head", authored, "--base", base)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout), {
                        "status": "passed", "commits_checked": expected, "unique_trees_checked": 2,
                        "head_files": 2, "batches": 1,
                    })
            subprocess.run(
                ["git", "-C", str(repository), "update-ref", "HEAD", authored], check=True,
            )
            push = self.pr_scan(repository, "--head", authored, "--base", authored)
            self.assertEqual(push.returncode, 0, push.stderr)
            self.assertEqual(json.loads(push.stdout), {
                "status": "passed", "commits_checked": 2, "unique_trees_checked": 1,
                "head_files": 1, "batches": 1,
            })
            invalid = self.pr_scan(repository, "--head", authored, "--base", "refs/heads/main")
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("invalid_revision", invalid.stderr)
            self.assertNotIn('"status": "passed"', invalid.stdout)

    def test_branch_union_refuses_removed_private_path_and_forged_target_ancestor(self):
        for options, reason in (({"private_target": True}, "private_file_path"),
                                ({"forged_target": True}, "maintainer_identity_mismatch")):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as directory:
                repository, authored, merge = self.pr_checkout(
                    directory, diverged_target=True, **options,
                )
                target = subprocess.check_output(
                    ["git", "-C", str(repository), "rev-parse", merge + "^1"], text=True,
                ).strip()
                self.assertNotIn(".env", subprocess.check_output(
                    ["git", "-C", str(repository), "ls-tree", "--name-only", target], text=True,
                ).splitlines())
                result = self.pr_scan(repository, "--head", authored, "--base", target)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(reason, result.stderr)
                self.assertNotIn('"status": "passed"', result.stdout)
