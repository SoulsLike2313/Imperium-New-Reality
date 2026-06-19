#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Administratum Context Pack — единый источник истины по манифесту/хэшам.

schema_version: imperium.context_pack.v0_1

Сборщик MANIFEST.json для самодостаточного контекст-пака. Любой слой
(PowerShell-ассемблер, верификатор) обязан звать ЭТОТ модуль, а не считать
хэши сам — чтобы был один источник истины (как astra_gate для допуска).
"""
import os
import sys
import json
import hashlib
import argparse
import datetime

SCHEMA_VERSION = "imperium.context_pack.v0_1"
MANIFEST_NAME = "MANIFEST.json"

# Каталоги, без которых пак НЕ самодостаточен.
REQUIRED_DIRS = ["TOOLCHAIN", "HISTORY", "STATE", "DOCTRINE"]

# Файлы, без которых пак НЕ даёт 100% вход в контекст.
REQUIRED_FILES = [
    "TOOLCHAIN/HARNESS/TOOLS/WARP/warp-start.ps1",
    "TOOLCHAIN/HARNESS/TOOLS/WARP/warp-land.ps1",
    "HISTORY/git_head.txt",
    "HISTORY/git_log.txt",
    "HISTORY/git_status.txt",
    "HISTORY/changed_files.txt",
    "STATE/continuity_manifest.json",
    "CONTEXT_ENTRY.md",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def iter_files(root):
    """Детерминированный обход всех файлов пака (кроме самого манифеста)."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if rel == MANIFEST_NAME:
                continue
            yield rel, full


def build(pack_dir, git_head, note=""):
    if not os.path.isdir(pack_dir):
        raise SystemExit("ERROR: нет каталога пака: %s" % pack_dir)
    files = []
    for rel, full in iter_files(pack_dir):
        files.append({
            "path": rel,
            "bytes": os.path.getsize(full),
            "sha256": sha256_file(full),
        })
    files.sort(key=lambda x: x["path"])
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": git_head,
        "note": note or "",
        "file_count": len(files),
        "total_bytes": sum(f["bytes"] for f in files),
        "required_dirs": REQUIRED_DIRS,
        "required_files": REQUIRED_FILES,
        "files": files,
    }
    out = os.path.join(pack_dir, MANIFEST_NAME)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description="Context pack manifest builder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="собрать MANIFEST.json")
    b.add_argument("pack_dir")
    b.add_argument("--git-head", required=True)
    b.add_argument("--note", default="")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        m = build(args.pack_dir, args.git_head, args.note)
        print("MANIFEST written: %d files, %d bytes, head=%s"
              % (m["file_count"], m["total_bytes"], m["git_head"]))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
