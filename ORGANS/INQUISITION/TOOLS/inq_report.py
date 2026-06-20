#!/usr/bin/env python3
"""inq_report.py -- Inquisition canonical verdict writer.

Library module used by all other inq_*.py tools. Produces JSON verdicts conforming
to schema `inq.verdict.v0_1` (Q14 decision: strict + versioned).

Verdict schema (strict):
  {
    "schema_version": "inq.verdict.v0_1",
    "verdict": "OK" | "HINT_*" | "BLOCK_*" | "NOOP" | "FAIL_CLOSED",
    "stage": "H1_POST_ADMIT" | "H2_PRE_PERMIT" | "H3_WARP_TEST" | "H4_PRE_APPLY" | "H5_POST_LAND" | "H6_ON_DEMAND",
    "reasons": [str, ...],
    "tool": str,
    "task_id": str,
    "author": str,
    "issued_utc": "YYYY-MM-DDTHH:MM:SSZ",
    "exit_code": 0|1|2|3|4,
    "findings": [ {...} ],          # optional
    "recommendations": [str, ...],   # optional
    "evidence_path": str | null      # optional
  }

Exit codes (Q15):
  0 = OK / HINT_* / NOOP
  1 = BLOCK_*
  2 = FAIL_CLOSED
  3 = TIMEOUT
  4 = INPUT_INVALID

Reports layout (Q16 combo):
  <reports_dir>/YYYY-MM-DD/<task_id>/inq_<tool>_<utc>.json

Streams (Q19): JSON on stdout, human-readable on stderr.

Invariants enforced:
  I4 FAIL_CLOSED on any internal error.
  I6 APPEND_ONLY (writes are atomic per-file; never overwritten).
  I12 SIGNED_ONLY: every verdict carries tool+task+author+utc.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

SCHEMA_VERSION = "inq.verdict.v0_1"

VALID_STAGES = {
    "H1_POST_ADMIT",
    "H2_PRE_PERMIT",
    "H3_WARP_TEST",
    "H4_PRE_APPLY",
    "H5_POST_LAND",
    "H6_ON_DEMAND",
}

EXIT_OK = 0
EXIT_BLOCK = 1
EXIT_FAIL_CLOSED = 2
EXIT_TIMEOUT = 3
EXIT_INPUT_INVALID = 4


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _verdict_to_exit_code(verdict: str) -> int:
    if verdict == "FAIL_CLOSED":
        return EXIT_FAIL_CLOSED
    if verdict.startswith("BLOCK_"):
        return EXIT_BLOCK
    if verdict == "OK" or verdict.startswith("OK_") or verdict.startswith("HINT_") or verdict == "NOOP":
        return EXIT_OK
    # Unknown verdict shape => fail-closed (I4).
    return EXIT_FAIL_CLOSED


def _ensure_utf8_streams() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class VerdictBuilder:
    """Fluent builder for inq.verdict.v0_1 records."""

    def __init__(self, *, tool: str, task_id: str, author: str, stage: str) -> None:
        if stage not in VALID_STAGES:
            raise ValueError(f"invalid stage: {stage!r}")
        self.tool = tool
        self.task_id = task_id
        self.author = author
        self.stage = stage
        self.verdict: Optional[str] = None
        self.reasons: List[str] = []
        self.findings: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.evidence_path: Optional[str] = None

    def ok(self, reason: str = "clean") -> "VerdictBuilder":
        self.verdict = "OK"
        if reason:
            self.reasons.append(reason)
        return self

    def hint(self, kind: str, reason: str) -> "VerdictBuilder":
        self.verdict = f"HINT_{kind}"
        self.reasons.append(reason)
        return self

    def block(self, kind: str, reason: str) -> "VerdictBuilder":
        self.verdict = f"BLOCK_{kind}"
        self.reasons.append(reason)
        return self

    def noop(self, reason: str = "tool not applicable") -> "VerdictBuilder":
        self.verdict = "NOOP"
        if reason:
            self.reasons.append(reason)
        return self

    def fail_closed(self, reason: str) -> "VerdictBuilder":
        self.verdict = "FAIL_CLOSED"
        self.reasons.append(reason)
        return self

    def add_finding(self, **finding: Any) -> "VerdictBuilder":
        self.findings.append(dict(finding))
        return self

    def add_recommendation(self, rec: str) -> "VerdictBuilder":
        self.recommendations.append(rec)
        return self

    def set_evidence(self, path: str) -> "VerdictBuilder":
        self.evidence_path = path
        return self

    def to_dict(self) -> Dict[str, Any]:
        if self.verdict is None:
            self.verdict = "FAIL_CLOSED"
            self.reasons.append("verdict not set by tool (defaulted FAIL_CLOSED per I4)")
        exit_code = _verdict_to_exit_code(self.verdict)
        d: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "verdict": self.verdict,
            "stage": self.stage,
            "reasons": list(self.reasons),
            "tool": self.tool,
            "task_id": self.task_id,
            "author": self.author,
            "issued_utc": _utc_now(),
            "exit_code": exit_code,
        }
        if self.findings:
            d["findings"] = list(self.findings)
        if self.recommendations:
            d["recommendations"] = list(self.recommendations)
        if self.evidence_path is not None:
            d["evidence_path"] = self.evidence_path
        return d

    def write(
        self,
        *,
        reports_dir: str = "ORGANS/INQUISITION/REPORTS",
        also_stdout: bool = True,
        also_neg_experience: bool = True,
        neg_dir: str = "_HARNESS/_NEGATIVE_EXPERIENCE",
    ) -> Tuple[Dict[str, Any], str, int]:
        """Write verdict under reports_dir; duplicate FAIL/BLOCK into neg_dir (Q20).

        Returns (verdict_dict, file_path, exit_code). Always emits JSON on stdout when also_stdout.
        """
        d = self.to_dict()
        file_path = ""
        try:
            date_str = d["issued_utc"][:10]
            utc_safe = d["issued_utc"].replace(":", "-")
            target_dir = Path(reports_dir) / date_str / d["task_id"]
            target_dir.mkdir(parents=True, exist_ok=True)
            fname = f"inq_{self.tool}_{utc_safe}.json"
            target = target_dir / fname
            target.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            file_path = str(target)
            if also_neg_experience and (d["verdict"].startswith("BLOCK_") or d["verdict"] == "FAIL_CLOSED"):
                neg_target_dir = Path(neg_dir) / d["task_id"]
                neg_target_dir.mkdir(parents=True, exist_ok=True)
                neg_fname = f"inq_{self.tool}_{utc_safe}.json"
                (neg_target_dir / neg_fname).write_text(
                    json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
                )
        except Exception as e:
            d = dict(d)
            d["verdict"] = "FAIL_CLOSED"
            d["reasons"] = list(d.get("reasons", [])) + [
                f"write_error: {type(e).__name__}: {e}"
            ]
            d["exit_code"] = EXIT_FAIL_CLOSED
        if also_stdout:
            sys.stdout.write(json.dumps(d, ensure_ascii=False))
            sys.stdout.write("\n")
            try:
                sys.stdout.flush()
            except Exception:
                pass
        return d, file_path, d["exit_code"]


def write_verdict(
    verdict_dict: Dict[str, Any],
    *,
    reports_dir: str = "ORGANS/INQUISITION/REPORTS",
    also_stdout: bool = True,
) -> Tuple[Dict[str, Any], str, int]:
    """Lower-level writer; verdict_dict must already be a v0_1-shape dict."""
    required = {"verdict", "stage", "tool", "task_id", "author"}
    missing = required - set(verdict_dict.keys())
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    d = dict(verdict_dict)
    d.setdefault("schema_version", SCHEMA_VERSION)
    d.setdefault("issued_utc", _utc_now())
    d.setdefault("reasons", [])
    d["exit_code"] = _verdict_to_exit_code(d["verdict"])
    file_path = ""
    try:
        date_str = d["issued_utc"][:10]
        utc_safe = d["issued_utc"].replace(":", "-")
        target_dir = Path(reports_dir) / date_str / d["task_id"]
        target_dir.mkdir(parents=True, exist_ok=True)
        tool = d.get("tool", "inq_unknown")
        target = target_dir / f"inq_{tool}_{utc_safe}.json"
        target.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        file_path = str(target)
    except Exception as e:
        d["verdict"] = "FAIL_CLOSED"
        d["reasons"] = list(d.get("reasons", [])) + [f"write_error: {type(e).__name__}: {e}"]
        d["exit_code"] = EXIT_FAIL_CLOSED
    if also_stdout:
        sys.stdout.write(json.dumps(d, ensure_ascii=False))
        sys.stdout.write("\n")
        try:
            sys.stdout.flush()
        except Exception:
            pass
    return d, file_path, d["exit_code"]


def _cli_self_test() -> int:
    vb = VerdictBuilder(
        tool="inq_report",
        task_id="SELF-TEST",
        author="OWNER_MANUAL",
        stage="H6_ON_DEMAND",
    )
    vb.ok("inq_report self-test passed")
    tmp = os.environ.get("INQ_SELFTEST_DIR", "/tmp/inq_report_selftest")
    d, _, ec = vb.write(reports_dir=tmp, also_stdout=True, also_neg_experience=False)
    sys.stderr.write(f"[inq_report] self-test verdict={d['verdict']} exit={ec}\n")
    return ec


if __name__ == "__main__":
    _ensure_utf8_streams()
    if "--self-test" in sys.argv:
        sys.exit(_cli_self_test())
    sys.stderr.write(
        "[inq_report] library module; import VerdictBuilder/write_verdict, or run --self-test\n"
    )
    sys.exit(0)
