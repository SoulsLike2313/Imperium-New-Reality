#!/usr/bin/env python3
"""Verify git truth: clean working tree and local HEAD == origin/master.

Capability tag: LOCAL_SCRIPT_FIRST

This is the runnable form of the rule "every PASS needs current git truth".
If there is no .git, it declares AUTHORITY_GAP instead of faking green.
Emits a receipt JSON compatible with pre_push_gate_receipt.schema.json.
"""
import argparse
import json
import os
import subprocess
import sys


def git(root, *a):
    return subprocess.run(["git", "-C", root, *a], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--remote-ref", default="origin/master")
    ap.add_argument("--report-out", default="")
    args = ap.parse_args()
    root = os.path.abspath(args.repo_root)
    receipt = {
        "schema_version": "imperium.pre_push_gate_receipt.v0_1",
        "tool": "verify_git_truth_v0_1",
        "capability_tag": "LOCAL_SCRIPT_FIRST",
        "repo_root": root,
    }
    if not os.path.isdir(os.path.join(root, ".git")):
        receipt.update({"git_present": False, "verdict": "AUTHORITY_GAP",
                        "note": "No .git: git truth cannot be proven. Do not claim PASS."})
        _emit(receipt, args.report_out)
        sys.exit(2)
    status = git(root, "status", "--porcelain=v1")
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    remote = git(root, "rev-parse", args.remote_ref)
    clean = status.stdout.strip() == ""
    remote_ok = remote.returncode == 0 and remote.stdout.strip() == head
    receipt.update({
        "git_present": True,
        "working_tree_clean": clean,
        "local_head": head,
        "remote_ref": args.remote_ref,
        "remote_head": remote.stdout.strip() if remote.returncode == 0 else None,
        "head_equals_remote": remote_ok,
        "dirty_entries": status.stdout.strip().splitlines()[:50],
        "verdict": "PASS" if (clean and remote_ok) else "BLOCK",
    })
    _emit(receipt, args.report_out)
    sys.exit(0 if receipt["verdict"] == "PASS" else 2)


def _emit(receipt, out):
    text = json.dumps(receipt, ensure_ascii=True, indent=2)
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
