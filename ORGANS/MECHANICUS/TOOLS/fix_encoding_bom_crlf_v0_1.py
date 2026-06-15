#!/usr/bin/env python3
"""Normalize encoding: strip UTF-8 BOM and convert CRLF->LF.

Capability tag: LOCAL_SCRIPT_FIRST

Safe by default: runs in --dry-run unless --apply is passed.
Skips intentional fixtures (path contains FIXTURE/FIXTURES) and binaries.
Keeps CRLF for *.ps1 and *.cmd (Windows scripts) per .gitattributes policy.
"""
import argparse
import os

BOM = b"\xef\xbb\xbf"
TEXT_EXT = {".md", ".json", ".jsonl", ".py", ".txt", ".toml", ".js", ".ts",
            ".tsx", ".css", ".tcss", ".html", ".svg", ".yml", ".yaml"}
KEEP_CRLF_EXT = {".ps1", ".cmd", ".bat"}
FIXTURE_MARKERS = ("FIXTURE", "FIXTURES", "fixture", "fixtures")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true", help="actually write changes")
    ap.add_argument("--strip-bom", action="store_true", default=True)
    ap.add_argument("--fix-crlf", action="store_true", default=True)
    args = ap.parse_args()
    root = os.path.abspath(args.repo_root)
    changed_bom, changed_crlf = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        p = dirpath.replace(os.sep, "/")
        if "/.git" in p or "/target" in p or "/node_modules" in p:
            dirnames[:] = [d for d in dirnames if d not in (".git", "target", "node_modules")]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, root).replace(os.sep, "/")
            if any(m in rel for m in FIXTURE_MARKERS):
                continue
            if ext not in TEXT_EXT and ext not in KEEP_CRLF_EXT:
                continue
            try:
                with open(fp, "rb") as fh:
                    data = fh.read()
            except OSError:
                continue
            new = data
            if args.strip_bom and ext in (".json", ".md") and new.startswith(BOM):
                new = new[len(BOM):]
                changed_bom.append(rel)
            if args.fix_crlf and ext not in KEEP_CRLF_EXT and b"\r" in new:
                new = new.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                changed_crlf.append(rel)
            if new != data and args.apply:
                with open(fp, "wb") as fh:
                    fh.write(new)
    mode = "APPLIED" if args.apply else "DRY_RUN"
    print("[%s] bom_stripped=%d crlf_fixed=%d" % (mode, len(changed_bom), len(changed_crlf)))
    for r in changed_bom[:20]:
        print("  BOM " + r)
    for r in changed_crlf[:20]:
        print("  CRLF " + r)


if __name__ == "__main__":
    main()
