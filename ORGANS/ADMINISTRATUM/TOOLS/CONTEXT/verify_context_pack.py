#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Administratum Context Pack — верификатор самодостаточности.

Проверяет, что пак = 100% факта:
  * есть MANIFEST.json нужной схемы;
  * присутствуют все REQUIRED_DIRS / REQUIRED_FILES;
  * каждый файл из манифеста есть на диске и sha256 совпадает;
  * нет файлов на диске вне манифеста (UNTRACKED_FILE);
  * (опц.) git_head совпадает с ожидаемым.

exit: 0 = SELF_SUFFICIENT_OK, 2 = FAIL, 1 = ошибка запуска.
"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_pack_lib import (  # noqa: E402
    SCHEMA_VERSION,
    MANIFEST_NAME,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    sha256_file,
    iter_files,
)


def verify(pack_dir, expect_head=None):
    reasons = []
    mpath = os.path.join(pack_dir, MANIFEST_NAME)
    if not os.path.isfile(mpath):
        return "FAIL", ["NO_MANIFEST          нет MANIFEST.json — пак не самодостаточен"]
    try:
        with open(mpath, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        return "FAIL", ["MANIFEST_UNPARSEABLE %s" % e]

    if manifest.get("schema_version") != SCHEMA_VERSION:
        reasons.append("SCHEMA_MISMATCH      %s != %s"
                       % (manifest.get("schema_version"), SCHEMA_VERSION))

    for d in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(pack_dir, d)):
            reasons.append("MISSING_DIR          %s" % d)
    for rf in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(pack_dir, rf)):
            reasons.append("MISSING_REQUIRED     %s" % rf)

    listed = {e["path"]: e for e in manifest.get("files", [])}

    on_disk = set()
    for rel, full in iter_files(pack_dir):
        on_disk.add(rel)
        if rel not in listed:
            reasons.append("UNTRACKED_FILE       %s (на диске, нет в MANIFEST)" % rel)

    for rel, e in sorted(listed.items()):
        full = os.path.join(pack_dir, rel)
        if not os.path.isfile(full):
            reasons.append("MISSING_FILE         %s (в MANIFEST, нет на диске)" % rel)
            continue
        if sha256_file(full) != e.get("sha256"):
            reasons.append("HASH_MISMATCH        %s" % rel)

    if expect_head and manifest.get("git_head") != expect_head:
        reasons.append("HEAD_MISMATCH        manifest=%s expected=%s"
                       % (manifest.get("git_head"), expect_head))

    verdict = "SELF_SUFFICIENT_OK" if not reasons else "FAIL"
    return verdict, reasons


def main(argv=None):
    ap = argparse.ArgumentParser(description="Context pack verifier")
    ap.add_argument("pack_dir")
    ap.add_argument("--expect-head", default=None)
    args = ap.parse_args(argv)

    verdict, reasons = verify(args.pack_dir, args.expect_head)
    bar = "=" * 60
    print(bar)
    print("  CONTEXT PACK VERIFY")
    print("  pack : %s" % args.pack_dir)
    print(bar)
    for r in reasons:
        print("  [FAIL] %s" % r)
    print("-" * 60)
    print("  VERDICT : %s" % verdict)
    if verdict == "SELF_SUFFICIENT_OK":
        print("  -> Пак самодостаточен: пак = 100%% факта и истории.")
        return 0
    print("  -> Пак НЕ самодостаточен. Не передавать как вход в контекст.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
