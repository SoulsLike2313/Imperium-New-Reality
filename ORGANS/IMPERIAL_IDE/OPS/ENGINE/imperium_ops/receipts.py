"""receipts - structured proof for every claim.

No PASS may exist without a matching receipt. Each receipt type declares its
required fields; validation reports missing fields and fake-green risk so the
Receipts panel and the Administratum gate can act on it.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


EVIDENCE_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6"]
MIN_EVIDENCE = "E3"

# Receipt type -> required field names.
RECEIPT_SCHEMAS: Dict[str, List[str]] = {
    "command_receipt": ["task_id", "command", "exit_code", "output_digest", "evidence_level"],
    "validation_receipt": ["task_id", "validator", "result", "details", "evidence_level"],
    "smoke_receipt": ["task_id", "scenario", "result", "exit_code", "evidence_level"],
    "safety_gate_receipt": ["task_id", "action", "allowed", "reasons"],
    "git_commit_push_receipt": ["task_id", "branch", "commit", "pushed", "in_scope", "secrets_detected"],
    "taskpack_admission_receipt": ["task_id", "admitted", "blockers", "sha256"],
    "resolver_receipt": ["task_id", "resolved_path", "searched_paths"],
    "administratum_bundle_gate_receipt": ["task_id", "verdict", "missing_lines", "evidence_level"],
    "mechanicus_tool_receipt": ["task_id", "tool", "mode", "allowed", "result"],
}

# Tokens that, when used as a result without evidence, indicate fake-green.
_GREEN_WORDS = {"pass", "passed", "ok", "success", "released", "done", "green"}


def make_receipt(receipt_type: str, **fields) -> dict:
    """Create a receipt dict with type + timestamp; unknown types are tagged."""
    receipt = {
        "receipt_type": receipt_type,
        "created_at": _now(),
        "status": "CANDIDATE_NOT_CANON",
    }
    receipt.update(fields)
    if receipt_type not in RECEIPT_SCHEMAS:
        receipt["_warning"] = f"unknown receipt_type: {receipt_type}"
    return receipt


def evidence_ok(level: str) -> bool:
    """True if evidence level meets or exceeds the minimum."""
    try:
        return EVIDENCE_ORDER.index(level) >= EVIDENCE_ORDER.index(MIN_EVIDENCE)
    except ValueError:
        return False


def validate_receipt(receipt: dict) -> Tuple[bool, List[str]]:
    """Return (ok, missing_fields) against the receipt's declared schema."""
    rtype = receipt.get("receipt_type", "")
    schema = RECEIPT_SCHEMAS.get(rtype)
    if schema is None:
        return False, [f"unknown receipt_type: {rtype}"]
    missing = [f for f in schema if receipt.get(f) in (None, "")]
    return (not missing), missing


def fake_green_risk(receipt: dict) -> List[str]:
    """Detect claims of success that lack supporting evidence.

    A 'green' result is suspect when:
    - there is no evidence_level, or it is below the minimum, AND
    - there is no command/exit_code/output to back it up.
    """
    reasons: List[str] = []
    result = str(receipt.get("result", receipt.get("verdict", ""))).strip().lower()
    looks_green = any(w == result or w in result.split() for w in _GREEN_WORDS)
    if not looks_green:
        return reasons
    level = receipt.get("evidence_level")
    if not level:
        reasons.append("green result without evidence_level")
    elif not evidence_ok(str(level)):
        reasons.append(f"green result with weak evidence_level={level} (< {MIN_EVIDENCE})")
    has_proof = any(
        receipt.get(k) not in (None, "")
        for k in ("command", "exit_code", "output_digest", "details")
    )
    if not has_proof:
        reasons.append("green result without command/exit_code/output proof")
    return reasons


def write_receipt(path: str, receipt: dict) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def load_receipt(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def link_to_task(receipt: dict) -> str:
    return str(receipt.get("task_id", ""))
