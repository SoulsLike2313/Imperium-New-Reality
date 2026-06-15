#!/usr/bin/env python3
"""Remove committed build artifacts from source (Rust target/, node_modules, caches).

Capability tag: LOCAL_SCRIPT_FIRST
Safe by default: --dry-run unless --apply. Prints reclaimed megabytes.
"""
import argparse
import os
import shutil

ARTIFACT_DIRS = {"target", "node_modules", "__pycache__", ".pytest_cache"}


def dir_size(path):
    total = 0
    for r, _d, files in os.walk(path):
        for fn in files:
            try:
                total += os.path.getsize(os.path.join(r, fn))
            except OSError:
                pass
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.repo_root)
    targets, reclaimed = [], 0
    for dirpath, dirnames, _files in os.walk(root):
        if "/.git" in dirpath.replace(os.sep, "/"):
            continue
        for d in list(dirnames):
            if d in ARTIFACT_DIRS:
                full = os.path.join(dirpath, d)
                sz = dir_size(full)
                reclaimed += sz
                targets.append((os.path.relpath(full, root).replace(os.sep, "/"), sz))
                dirnames.remove(d)
                if args.apply:
                    shutil.rmtree(full, ignore_errors=True)
    mode = "APPLIED" if args.apply else "DRY_RUN"
    print("[%s] artifact_dirs=%d reclaimed_megabytes=%.1f"
          % (mode, len(targets), reclaimed / 1048576))
    for rel, sz in targets:
        print("  %8.1f MB  %s" % (sz / 1048576, rel))
    if not args.apply and targets:
        print("\nNext: re-run with --apply, then add 'target/' to .gitignore.")


if __name__ == "__main__":
    main()
