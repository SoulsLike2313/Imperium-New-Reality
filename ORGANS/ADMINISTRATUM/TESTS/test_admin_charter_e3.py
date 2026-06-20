# -*- coding: utf-8 -*-
"""
ADMINISTRATUM Charter v1.0.0 -- control test runner.

Tests:
  T1 (ENFORCED): charter structure (RU + EN sections, verdicts, invariants, NO_LLM principle).
  T2 (ENFORCED-SKIP): admin_*.py imports/CLI. SKIP until ADMIN-TOOLS-0001 lands.
  T3 (ENFORCED-SKIP): append-only smoke. SKIP until tools land.
  T4 (ENFORCED-SKIP): redaction smoke. SKIP until tools land.
  T5 (ENFORCED-SKIP): NO_NETWORK token scan. SKIP until tools land.
  T6 (PLANNED v0_2): RECALL fixture. SKIP.
  T7 (PLANNED v0_2): DRIFT detect. SKIP.
  T8 (PLANNED v0_2): QUOTA. SKIP.
  T9 (PLANNED v0_3): OVERRIDE. SKIP.
  T10 (PLANNED v0_3): e2e. SKIP.

rc=0 if all live ENFORCED pass; rc=1 if any ENFORCED fail; rc=2 on runner exception.

Windows-safe: stdout/stderr reconfigured to UTF-8 with errors='replace'.
ASCII-only labels in printed output.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
import traceback

# Windows-safe console encoding
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


# All 15 RU sections (\u00a7 = section sign)
REQUIRED_RU_SECTIONS = [
    "\u00a70. \u041f\u0440\u0438\u0440\u043e\u0434\u0430 \u043e\u0440\u0433\u0430\u043d\u0430",                   # Nature
    "\u00a71. \u041c\u0438\u0441\u0441\u0438\u044f",                                                         # Mission
    "\u00a72. \u0425\u0443\u043a\u0438 \u0432 Cycle",                                                          # Hooks
    "\u00a73. \u041e\u0431\u044f\u0437\u0430\u043d\u043d\u043e\u0441\u0442\u0438",                              # Duties
    "\u00a74. \u0417\u0430\u043f\u0440\u0435\u0442\u044b",                                                      # Prohibitions
    "\u00a75. \u041a\u0430\u043d\u043e\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0432\u0435\u0440\u0434\u0438\u043a\u0442\u044b",  # Verdicts
    "\u00a76. Receipt-\u0441\u0445\u0435\u043c\u0430",                                                        # Receipt schema
    "\u00a77. \u0410\u0440\u0445\u0438\u0442\u0435\u043a\u0442\u0443\u0440\u0430",                              # Architecture
    "\u00a78. \u041a\u0430\u043d\u043e\u043d-\u0441\u043a\u0440\u0438\u043f\u0442\u044b",                       # Scripts
    "\u00a79. \u041f\u043e\u0440\u043e\u0433\u0438 \u043f\u043e \u0443\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044e",  # Thresholds
    "\u00a710. \u0418\u043d\u0432\u0430\u0440\u0438\u0430\u043d\u0442\u044b",                                  # Invariants
    "\u00a711. \u0412\u0435\u0440\u0441\u0438\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435",        # Versioning
    "\u00a712. CHANGELOG",
    "\u00a713. \u041a\u043e\u043d\u0442\u0440\u043e\u043b\u044c\u043d\u044b\u0435 \u0442\u0435\u0441\u0442\u044b", # Control tests
    "\u00a714. \u0421\u0432\u044f\u0437\u044c \u0441 \u0410\u0441\u0442\u0440\u043e\u043d\u043e\u043c\u0438\u043a\u043e\u043d\u043e\u043c",  # Relation
]

REQUIRED_EN_SECTIONS = [
    "\u00a70. Nature of the organ",
    "\u00a71. Mission",
    "\u00a72. Hooks into Cycle",
    "\u00a73. Duties",
    "\u00a74. Hard prohibitions",
    "\u00a75. Canonical verdicts",
    "\u00a76. Receipt schema",
    "\u00a77. HARNESS file architecture",
    "\u00a78. Canonical scripts",
    "\u00a79. Default thresholds",
    "\u00a710. Invariants",
    "\u00a711. Charter versioning",
    "\u00a712. CHANGELOG",
    "\u00a713. Control tests",
    "\u00a714. Relation to Astronomicon and Throne",
]

CANONICAL_VERDICTS = [
    "ADMIN_RECORDED",
    "ADMIN_HINT_RECALL",
    "ADMIN_HINT_PATTERN",
    "ADMIN_BLOCK_RATE",
    "ADMIN_BLOCK_LOOP",
    "ADMIN_BLOCK_DUP",
    "ADMIN_BLOCK_COOLDOWN",
    "ADMIN_BLOCK_BURST",
    "ADMIN_BLOCK_DRIFT",
    "ADMIN_OVERRIDDEN",
    "ADMIN_FAILED_CLOSED",
]

INVARIANTS = [
    "I1 APPEND_ONLY",
    "I2 NO_SECRETS",
    "I3 NO_LLM_IN_PIPELINE",
    "I4 DETERMINISTIC",
    "I5 FAIL_CLOSED",
    "I6 SIGNED_ONLY",
    "I7 CANONICAL_ORGANS_ONLY",
    "I8 OVERRIDE_LOGGED",
]

NO_LLM_KEYWORDS = [
    "NO_LLM_IN_PIPELINE",
    "script-first",
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


def check_tokens(path, tokens, label):
    if not os.path.isfile(path):
        return False, "file not found: %s" % path
    text = open(path, "r", encoding="utf-8").read()
    missing = [t for t in tokens if t not in text]
    if missing:
        return False, "missing %s: %s" % (label, ", ".join(missing[:5]))
    return True, "all %d %s present" % (len(tokens), label)


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
    ap.add_argument("--charter", default="DOCTRINARIUM/CHARTERS/ADMINISTRATUM.md")
    ap.add_argument("--charter-en", default="DOCTRINARIUM/CHARTERS/ADMINISTRATUM.en.md")
    ap.add_argument("--tools-dir", default="ORGANS/ADMINISTRATUM/TOOLS")
    args = ap.parse_args()

    report = TestReport()
    _safe_print("=" * 72)
    _safe_print("  ADMINISTRATUM Charter -- control test runner v1")
    _safe_print("  cwd        : %s" % os.getcwd())
    _safe_print("  charter    : %s" % args.charter)
    _safe_print("  charter_en : %s" % args.charter_en)
    _safe_print("  tools_dir  : %s" % args.tools_dir)
    _safe_print("  python     : %s" % sys.version.split()[0])
    _safe_print("  stdout_enc : %s" % getattr(sys.stdout, "encoding", "?"))
    _safe_print("=" * 72)

    # T1: structure checks
    _run(report, "T1.1 RU charter sections (15)", check_sections, args.charter, REQUIRED_RU_SECTIONS)
    _run(report, "T1.2 EN charter sections (15)", check_sections, args.charter_en, REQUIRED_EN_SECTIONS)
    _run(report, "T1.3 RU charter verdicts (11)", check_tokens, args.charter, CANONICAL_VERDICTS, "verdicts")
    _run(report, "T1.4 RU charter invariants (8)", check_tokens, args.charter, INVARIANTS, "invariants")
    _run(report, "T1.5 NO_LLM principle declared", check_tokens, args.charter, NO_LLM_KEYWORDS, "keywords")

    # T2-T5: depend on ADMIN-TOOLS-0001
    tools_present = os.path.isdir(args.tools_dir) and any(
        os.path.isfile(os.path.join(args.tools_dir, f))
        for f in ("admin_memorize.py", "admin_recall.py")
    )
    if tools_present:
        report.add("SKIP", "T2 admin_*.py imports/CLI", "check enabled in ADMIN-TOOLS-0001 charter pack")
        report.add("SKIP", "T3 append-only smoke", "check enabled in ADMIN-TOOLS-0001")
        report.add("SKIP", "T4 redaction smoke", "check enabled in ADMIN-TOOLS-0001")
        report.add("SKIP", "T5 NO_NETWORK token scan", "check enabled in ADMIN-TOOLS-0001")
    else:
        report.add("SKIP", "T2 admin_*.py imports/CLI", "tools not yet in canon (ADMIN-TOOLS-0001 pending)")
        report.add("SKIP", "T3 append-only smoke", "tools not yet in canon")
        report.add("SKIP", "T4 redaction smoke", "tools not yet in canon")
        report.add("SKIP", "T5 NO_NETWORK token scan", "tools not yet in canon")

    # T6-T10: PLANNED v0_2 / v0_3
    report.add("SKIP", "T6 RECALL by fixture", "PLANNED v0_2")
    report.add("SKIP", "T7 DRIFT detect", "PLANNED v0_2")
    report.add("SKIP", "T8 QUOTA simulation", "PLANNED v0_2")
    report.add("SKIP", "T9 OVERRIDE flow", "PLANNED v0_3")
    report.add("SKIP", "T10 e2e cycle", "PLANNED v0_3")

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
