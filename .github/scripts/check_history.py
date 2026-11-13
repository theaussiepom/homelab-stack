#!/usr/bin/env python3
"""Scan both branch histories and the checkout using the selected framework's guard."""

import argparse
import importlib.util
import json
from pathlib import Path
import time

BATCH_COMMITS = 100
BATCH_SECONDS = 180


def scan(root, safety, scanner, head="HEAD", base=None):
    head = safety.resolve(root, head)
    if safety.git(root, "rev-parse", "--is-shallow-repository").decode().strip() != "false":
        raise ValueError("Fetch complete history before scanning a shallow repository")
    revisions = ["rev-list", "--reverse", head]
    if base:
        revisions.append(safety.resolve(root, base))
    revisions = safety.git(root, *revisions).decode().splitlines()
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
    checkout = safety.resolve(root, "HEAD")
    head_tree = safety.git(root, "rev-parse", checkout + "^{tree}").decode().strip()
    if head_tree not in trees:
        trees[head_tree] = safety.scan_tree(root, checkout, scanner)
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
    parser.add_argument("--head", default="HEAD", help="Authored history head; the checkout tree is also scanned")
    parser.add_argument("--base", help="Target history head; all reachable commits on both sides are scanned")
    args = parser.parse_args()
    source = args.framework.resolve() / ".github/scripts/source_safety.py"
    spec = importlib.util.spec_from_file_location("selected_source_safety", source)
    safety = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(safety)
    print(json.dumps(scan(args.root.resolve(), safety, args.scanner.resolve(), args.head, args.base)))


if __name__ == "__main__":
    main()
