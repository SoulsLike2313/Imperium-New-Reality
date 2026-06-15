#!/usr/bin/env python3
"""IMPERIUM Hygiene & Honesty Gate v0.1 (script-first, stdlib only).

This is the executable heart of the clean-and-honest system. It scans a repo
root and reports physical-hygiene and honesty violations that the Organs must
not ignore. It is the runnable form of the doctrine "No fake green. Claims
require receipts."

Capability tag: LOCAL_SCRIPT_FIRST

Verdict model (mirrors INQUISITION PASS/WARN/BLOCK):
  exit 0 -> PASS
  exit 1 -> PASS_WITH_WARNINGS
  exit 2 -> BLOCK

BLOCK conditions (default policy):
  - committed build artifacts in source (target/, *.rlib, *.rmeta, *.pdb, *.dll, *.exe, *.lib)
  - committed .zip outside the declared fixture allowlist
  - truly malformed JSON outside the declared fixture allowlist
  - real-looking secret material outside detector allowlist

WARN conditions:
  - UTF-8 BOM in *.json / *.md
  - CRLF line endings in text files
  - empty (0-byte) non-.gitkeep files
"""
import argparse
import json
import os
import re
import sys

BUILD_DIR_NAMES = {"target", "node_modules", "__pycache__", ".pytest_cache"}
BUILD_ARTIFACT_EXT = {".rlib", ".rmeta", ".pdb", ".dll", ".exe", ".lib", ".pyc", ".pyo"}
TEXT_EXT = {".md", ".json", ".jsonl", ".py", ".txt", ".toml", ".js", ".ts", ".tsx",
            ".css", ".tcss", ".html", ".svg", ".yml", ".yaml"}
SECRET_PATTERNS = [
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{10,}"),
]
BOM = b"\xef\xbb\xbf"
DEFAULT_FIXTURE_MARKERS = ("FIXTURE", "FIXTURES", "fixture", "fixtures")
DEFAULT_SECRET_ALLOWLIST = ("QUESTIONABLE_OR_QUARANTINE", "validate_organ_dialogue_demo")


def is_allowlisted(path, markers):
    return any(m in path for m in markers)


def scan(repo_root, fixture_markers, secret_allowlist, max_samples):
    report = {
        "build_artifact_files": [], "build_artifact_bytes": 0,
        "committed_zip": [], "bom_files": [], "crlf_files": [],
        "truly_malformed_json": [], "bom_only_json": [],
        "empty_files": [], "secret_like": [],
    }
    for dirpath, dirnames, filenames in os.walk(repo_root):
        if "/.git" in dirpath.replace(os.sep, "/"):
            continue
        rel_dir = os.path.relpath(dirpath, repo_root).replace(os.sep, "/")
        # build directories: count everything inside
        base = os.path.basename(dirpath)
        if base in BUILD_DIR_NAMES:
            for root2, _d, files2 in os.walk(dirpath):
                for fn in files2:
                    fp = os.path.join(root2, fn)
                    try:
                        report["build_artifact_bytes"] += os.path.getsize(fp)
                    except OSError:
                        pass
                    rel = os.path.relpath(fp, repo_root).replace(os.sep, "/")
                    report["build_artifact_files"].append(rel)
            dirnames[:] = []
            continue
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            rel = (rel_dir + "/" + fn) if rel_dir != "." else fn
            ext = os.path.splitext(fn)[1].lower()
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            if ext in BUILD_ARTIFACT_EXT:
                report["build_artifact_files"].append(rel)
                report["build_artifact_bytes"] += size
                continue
            if ext == ".zip":
                if not is_allowlisted(rel, fixture_markers):
                    report["committed_zip"].append(rel)
                continue
            if size == 0 and fn != ".gitkeep":
                report["empty_files"].append(rel)
            # read small head for text checks
            try:
                with open(fp, "rb") as fh:
                    head = fh.read(65536)
            except OSError:
                continue
            if ext in (".json", ".md") and head.startswith(BOM):
                report["bom_files"].append(rel)
            if ext in TEXT_EXT and b"\r" in head:
                report["crlf_files"].append(rel)
            if ext == ".json":
                try:
                    with open(fp, "r", encoding="utf-8-sig") as jf:
                        json.load(jf)
                    if head.startswith(BOM):
                        report["bom_only_json"].append(rel)
                except (ValueError, OSError):
                    if not is_allowlisted(rel, fixture_markers):
                        report["truly_malformed_json"].append(rel)
            if ext in TEXT_EXT and not is_allowlisted(rel, secret_allowlist):
                for pat in SECRET_PATTERNS:
                    if pat.search(head):
                        report["secret_like"].append(rel)
                        break
    # summarize
    counts = {k: (len(v) if isinstance(v, list) else v) for k, v in report.items()}
    counts["build_artifact_megabytes"] = round(report["build_artifact_bytes"] / 1048576, 1)
    block = (counts["build_artifact_files"] > 0 or counts["committed_zip"] > 0
             or counts["truly_malformed_json"] > 0 or counts["secret_like"] > 0)
    warn = (counts["bom_files"] > 0 or counts["crlf_files"] > 0 or counts["empty_files"] > 0)
    verdict = "BLOCK" if block else ("PASS_WITH_WARNINGS" if warn else "PASS")
    # trim samples
    for k, v in report.items():
        if isinstance(v, list):
            report[k] = v[:max_samples]
    return counts, report, verdict


def main():
    ap = argparse.ArgumentParser(description="IMPERIUM Hygiene & Honesty Gate v0.1")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--report-out", default="")
    ap.add_argument("--max-samples", type=int, default=50)
    ap.add_argument("--extra-fixture-marker", action="append", default=[])
    args = ap.parse_args()
    markers = tuple(DEFAULT_FIXTURE_MARKERS) + tuple(args.extra_fixture_marker)
    counts, samples, verdict = scan(os.path.abspath(args.repo_root), markers,
                                    DEFAULT_SECRET_ALLOWLIST, args.max_samples)
    out = {
        "schema_version": "imperium.hygiene_gate_report.v0_1",
        "tool": "imperium_hygiene_gate_v0_1",
        "capability_tag": "LOCAL_SCRIPT_FIRST",
        "repo_root": os.path.abspath(args.repo_root),
        "counts": counts,
        "samples": samples,
        "verdict": verdict,
    }
    text = json.dumps(out, ensure_ascii=True, indent=2)
    if args.report_out:
        with open(args.report_out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    print(text)
    sys.exit({"PASS": 0, "PASS_WITH_WARNINGS": 1, "BLOCK": 2}[verdict])


if __name__ == "__main__":
    main()
