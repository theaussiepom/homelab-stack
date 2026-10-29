#!/usr/bin/env python3
"""Scan all reachable history using the selected framework's unchanged tree guard."""

import argparse
import importlib.util
import json
from pathlib import Path
import time

BATCH_COMMITS = 100
BATCH_SECONDS = 180


def scan(root, safety, scanner):
    head = safety.resolve(root, "HEAD")
    if safety.git(root, "rev-parse", "--is-shallow-repository").decode().strip() != "false":
        raise ValueError("Fetch complete history before scanning a shallow repository")
    revisions = safety.git(root, "rev-list", "--reverse", head).decode().splitlines()
    trees = {}
    for offset in range(0, len(revisions), BATCH_COMMITS):
        started = time.monotonic()
        for revision in revisions[offset:offset + BATCH_COMMITS]:
            if time.monotonic() - started > BATCH_SECONDS:
                raise ValueError("Source history batch exceeded its time budget")
            safety.check_identity(root, revision)
            tree = safety.git(root, "rev-parse", revision + "^{tree}").decode().strip()
            if tree not in trees:
                trees[tree] = safety.scan_tree(root, revision, scanner)
    head_tree = safety.git(root, "rev-parse", head + "^{tree}").decode().strip()
    return {
        "status": "passed",
        "commits_checked": len(revisions),
        "unique_trees_checked": len(trees),
        "head_files": trees[head_tree]["scanned_files"],
        "batches": (len(revisions) + BATCH_COMMITS - 1) // BATCH_COMMITS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--framework", type=Path, required=True)
    parser.add_argument("--scanner", type=Path, required=True)
    args = parser.parse_args()
    source = args.framework.resolve() / ".github/scripts/source_safety.py"
    spec = importlib.util.spec_from_file_location("selected_source_safety", source)
    safety = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(safety)
    print(json.dumps(scan(args.root.resolve(), safety, args.scanner.resolve())))


if __name__ == "__main__":
    main()
