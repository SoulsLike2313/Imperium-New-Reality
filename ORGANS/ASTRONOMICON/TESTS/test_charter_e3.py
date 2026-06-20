# -*- coding: utf-8 -*-
"""
ASTRONOMICON Charter v1.0.0 -- control test runner.

Tests:
  T1 (ENFORCED): charter structure (RU + EN, sections, verdicts, invariants).
  T2 (ENFORCED): canonical tools smoke (astra_cycle / astra_gate / imperium_provenance).
  T3 (PLANNED, v0_2): check-task -> TASK_NOT_REGISTERED. SKIP.
  T4 (PLANNED, v0_3): HAND_PACK end-to-end. SKIP.
  T5 (PLANNED, v0_3): form -> pack. SKIP.

rc=0 if all ENFORCED pass; rc=1 if any ENFORCED fail; rc=2 on runner exception.

Windows-safe: stdout/stderr reconfigured to UTF-8 with errors='replace',
plus a global try/except that prints a one-line diagnostic before exit.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
import re
import sys
import traceback

# --- Windows-safe console encoding (cp1251 -> UTF-8 with replace fallback) ---
for _stream in ("stdout", "stderr"):
    _s = getattr(sys, _stream, None)
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", "ascii") or "ascii"
        sys.stdout.write(msg.encode(enc, "replace").decode(enc, "replace") + "\n")


REQUIRED_RU_SECTIONS = [
    "\u00a71. \u041c\u0438\u0441\u0441\u0438\u044f",
    "\u00a72. \u0420\u0435\u0436\u0438\u043c\u044b \u0440\u0430\u0431\u043e\u0442\u044b",
    "\u00a72.1. HAND_PACK",
    "\u00a72.2. AUTO_PACK",
    "\u00a73. \u0426\u0438\u043a\u043b \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0438",
    "\u00a73.1. \u0414\u043e\u043f\u0443\u0441\u043a",
    "\u00a73.2. \u0418\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435",
    "\u00a73.3. \u041f\u0440\u0438\u0437\u0435\u043c\u043b\u0435\u043d\u0438\u0435",
    "\u00a73.4. \u0424\u0438\u043a\u0441\u0430\u0446\u0438\u044f",
    "\u00a73.5. \u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u0437\u0430\u0434\u0430\u0447\u0438",
    "\u00a74. \u0417\u0430\u043f\u0440\u0435\u0442\u044b",
    "\u00a75. \u041a\u0430\u043d\u043e\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0432\u0435\u0440\u0434\u0438\u043a\u0442\u044b",
    "\u00a76. \u0424\u043e\u0440\u043c\u0430\u0442 receipt.json",
    "\u00a77. \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430",
    "\u00a78. \u0411\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0430 Servitor",
    "\u00a79. \u0424\u043e\u0440\u043c\u044b \u043f\u0430\u043a\u043e\u0432",
    "\u00a710. \u0418\u043d\u0432\u0430\u0440\u0438\u0430\u043d\u0442\u044b",
    "\u00a711. \u0412\u0435\u0440\u0441\u0438\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0443\u0441\u0442\u0430\u0432\u0430",
    "\u00a712. CHANGELOG",
    "\u00a713. \u041a\u043e\u043d\u0442\u0440\u043e\u043b\u044c\u043d\u044b\u0435 \u0442\u0435\u0441\u0442\u044b",
    "\u00a714. \u0414\u043e\u043a\u0442\u0440\u0438\u043d\u0430\u0440\u0438\u0443\u043c",
]
REQUIRED_EN_SECTIONS = [
    "\u00a71. Mission",
    "\u00a72. Modes",
    "\u00a72.1. HAND_PACK",
    "\u00a72.2. AUTO_PACK",
    "\u00a73. Validation cycle",
    "\u00a74. Hard prohibitions",
    "\u00a75. Canonical verdicts",
    "\u00a76. Receipt schema",
    "\u00a78. Servitor blocking",
    "\u00a79. Pack forms",
    "\u00a710. Invariants",
    "\u00a711. Charter versioning",
    "\u00a712. CHANGELOG",
    "\u00a713. Control tests",
    "\u00a714. Doctrinarium",
]
REQUIRED_TOOL_TOKENS = {
    "astra_cycle": ["class Cycle", "_clear_untracked_collisions", "PRE_LAND"],
    "astra_gate": ["def validate", "CANON_ORGANS", "declared_evidence_level"],
    "imperium_provenance": ["def sign", "def verify", "NOTION_OPUS"],
}
CANONICAL_VERDICTS = [
    "CYCLE_OK", "CYCLE_DRYRUN_OK",
    "CYCLE_REJECTED_GATE", "CYCLE_REJECTED_PROVENANCE", "CYCLE_REJECTED_PERMIT",
    "CYCLE_FAIL_INTEGRATE", "CYCLE_FAIL_WARP_TEST", "CYCLE_FAIL_LAND", "CYCLE_FAIL_PUSH",
    "TASK_NOT_REGISTERED", "TASK_PENDING", "TASK_BLOCKED_SERVITOR",
]
INVARIANTS_KEYWORDS = [
    "warp", "squash",
    "\u043f\u043e\u0434\u043f\u0438\u0441\u0430\u043d",   # "подписан"
    "\u0441\u0435\u043a\u0440\u0435\u0442",               # "секрет"
    "HARNESS", "append-only",
]


class TestReport:
    def __init__(self):
        self.lines = []
        self.failed = 0
        self.passed = 0
        self.skipped = 0

    def add(self, status, name, msg=""):
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIP":
            self.skipped += 1
        self.lines.append("  [%-4s] %-52s %s" % (status, name, msg))

    def render(self):
        return "\n".join(self.lines)


def check_sections(path, required):
    if not os.path.isfile(path):
        return False, "file not found: %s" % path
    text = open(path, "r", encoding="utf-8").read()
    missing = [s for s in required if s not in text]
    if missing:
        sample = ", ".join(repr(s) for s in missing[:3])
        return False, "missing %d sections: %s%s" % (
            len(missing), sample, " ..." if len(missing) > 3 else ""
        )
    return True, "all %d sections present" % len(required)


def check_verdicts_in_charter(path):
    text = open(path, "r", encoding="utf-8").read()
    missing = [v for v in CANONICAL_VERDICTS if v not in text]
    if missing:
        return False, "missing verdicts: %s" % ", ".join(missing)
    return True, "all %d verdicts described" % len(CANONICAL_VERDICTS)


def check_invariants_section(path):
    text = open(path, "r", encoding="utf-8").read()
    m = re.search(r"\u00a710\..*?\n(.*?)(?:\n## |\n\u00a71)", text, re.DOTALL)
    blob = (m.group(1) if m else text).lower()
    missing = [k for k in INVARIANTS_KEYWORDS if k.lower() not in blob]
    if missing:
        return False, "keywords missing in section: %d" % len(missing)
    return True, "key invariants present"


def check_tool_source(tools_dir, name, tokens):
    f = os.path.join(tools_dir, name + ".py")
    if not os.path.isfile(f):
        return False, "file not found: %s" % f
    src = open(f, "r", encoding="utf-8").read()
    missing = [t for t in tokens if t not in src]
    if missing:
        return False, "missing tokens: %s" % ", ".join(missing)
    return True, "tokens OK"


def check_tool_imports(tools_dir):
    if not os.path.isdir(tools_dir):
        return False, "directory not found: %s" % tools_dir
    sys.path.insert(0, tools_dir)
    try:
        for mod in ("astra_cycle", "astra_gate", "imperium_provenance"):
            spec = importlib.util.find_spec(mod)
            if spec is None:
                return False, "module not importable: %s" % mod
            importlib.import_module(mod)
        return True, "3 canonical tools importable"
    except Exception as exc:
        return False, "import error: %r" % exc
    finally:
        if tools_dir in sys.path:
            sys.path.remove(tools_dir)


def _run(report, label, fn, *args):
    try:
        ok, msg = fn(*args)
    except Exception as exc:
        report.add("FAIL", label, "runner exception: %r" % exc)
        traceback.print_exc()
        return
    report.add("PASS" if ok else "FAIL", label, msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools-dir", default="ORGANS/ASTRONOMICON/TOOLS")
    ap.add_argument("--charter", default="DOCTRINARIUM/CHARTERS/ASTRONOMICON.md")
    ap.add_argument("--charter-en", default="DOCTRINARIUM/CHARTERS/ASTRONOMICON.en.md")
    args = ap.parse_args()

    report = TestReport()
    _safe_print("=" * 72)
    _safe_print("  ASTRONOMICON Charter -- control test runner v2 (utf8-safe)")
    _safe_print("  cwd        : %s" % os.getcwd())
    _safe_print("  charter    : %s" % args.charter)
    _safe_print("  charter_en : %s" % args.charter_en)
    _safe_print("  tools_dir  : %s" % args.tools_dir)
    _safe_print("  python     : %s" % sys.version.split()[0])
    _safe_print("  stdout_enc : %s" % getattr(sys.stdout, "encoding", "?"))
    _safe_print("=" * 72)

    _run(report, "T1.1 RU charter structure", check_sections, args.charter, REQUIRED_RU_SECTIONS)
    _run(report, "T1.2 EN charter structure", check_sections, args.charter_en, REQUIRED_EN_SECTIONS)
    if os.path.isfile(args.charter):
        _run(report, "T1.3 verdicts in charter", check_verdicts_in_charter, args.charter)
        _run(report, "T1.4 section 10 invariants", check_invariants_section, args.charter)
    else:
        report.add("FAIL", "T1.3 verdicts in charter", "no charter file")
        report.add("FAIL", "T1.4 section 10 invariants", "no charter file")

    for tool, tokens in REQUIRED_TOOL_TOKENS.items():
        _run(report, "T2.1 source: %s" % tool, check_tool_source, args.tools_dir, tool, tokens)
    _run(report, "T2.2 import canonical tools", check_tool_imports, args.tools_dir)

    report.add("SKIP", "T3 check-task -> TASK_NOT_REGISTERED", "PLANNED v0_2")
    report.add("SKIP", "T4 HAND_PACK end-to-end", "PLANNED v0_3")
    report.add("SKIP", "T5 form -> pack", "PLANNED v0_3")

    _safe_print(report.render())
    _safe_print("-" * 72)
    _safe_print("  PASS=%d FAIL=%d SKIP=%d" % (report.passed, report.failed, report.skipped))
    _safe_print("=" * 72)
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as exc:
        _safe_print("RUNNER_EXCEPTION: %r" % exc)
        traceback.print_exc()
        rc = 2
    sys.exit(rc)
