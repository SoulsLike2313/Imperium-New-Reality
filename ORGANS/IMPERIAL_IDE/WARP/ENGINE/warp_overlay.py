#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP OVERLAY / ISOLATION (V0.1)

The overlay is the mechanism that keeps the KERNEL clean. The kernel (core repo)
is treated as READ-ONLY baseline. Every write a task wants to make is captured
into the WARP working copy (workdir/artifacts), NEVER written to the kernel.

This module:
  - hashes a baseline so we can detect drift,
  - computes unified diffs between baseline and the warp artifact,
  - classifies a target path into a ZONE so the gate can apply zone policy,
  - refuses to compute a "direct core write" (there is no such path here).

No third-party deps: hashlib + difflib (stdlib).
"""
import difflib
import fnmatch
import hashlib
import os

# Zone classification globs. CORE is the protected kernel; it can only be
# touched through a gated release plan, never by a live warp write.
DEFAULT_ZONE_RULES = [
    ("CORE", ["ORGANS/*/CORE/*", "KERNEL/*", "ORGANS/_CORE_GOVERNANCE/*"]),
    ("GOVERNANCE", ["_CORE_GOVERNANCE/*", "GOVERNANCE/*"]),
    ("SUPPORT", ["SUPPORT/*"]),
    ("RUNTIME", ["WARP/*", "RUNTIME/*", "*/RUNTIME/*"]),
]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_zone(relpath, rules=None):
    rules = rules or DEFAULT_ZONE_RULES
    rp = relpath.replace("\\", "/")
    for zone, globs in rules:
        for g in globs:
            if fnmatch.fnmatch(rp, g):
                return zone
    return "UNKNOWN"


def snapshot_baseline(core_root, relpaths):
    """Hash the current kernel state for the files a task plans to affect."""
    snap = {}
    for rp in relpaths:
        full = os.path.join(core_root, rp)
        snap[rp] = sha256_file(full) if os.path.isfile(full) else None
    return snap


def baseline_text(core_root, relpath):
    full = os.path.join(core_root, relpath)
    if os.path.isfile(full):
        with open(full, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    return ""


def unified_diff(old_text, new_text, relpath):
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile="kernel/" + relpath,
        tofile="warp/" + relpath,
        lineterm="",
    )
    return "\n".join(diff)


def diff_stats(old_text, new_text):
    added = removed = 0
    sm = difflib.SequenceMatcher(None, old_text.splitlines(), new_text.splitlines())
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += (i2 - i1)
        if tag in ("replace", "insert"):
            added += (j2 - j1)
    return {"added": added, "removed": removed}
