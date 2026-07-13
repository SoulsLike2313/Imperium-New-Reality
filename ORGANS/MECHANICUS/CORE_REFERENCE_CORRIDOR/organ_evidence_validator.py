"""Separate-process validator for one organ check evidence document.

The validator deliberately has no write path.  It binds one evidence file to the
task, WARP, base HEAD, organ, and required check supplied by the parent runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_verdict import (  # noqa: E402
    ORGAN_VALIDATOR_ID,
    ORGAN_VALIDATOR_VERSION,
    Verdict,
)




def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _measurement(document: Mapping[str, Any], check_id: str) -> dict[str, Any] | None:
    """Return measured inputs only; a declared verdict is never an observation."""

    measured = document.get("measured_checks")
    if not isinstance(measured, list):
        return None
    for item in measured:
        if isinstance(item, Mapping) and item.get("check_id") == check_id:
            return dict(item)
    return None


def _observation_passes(expected: Any, observed: Any) -> bool:
    if expected != observed:
        return False
    return not (
        observed is None
        or observed is False
        or observed == ""
        or observed in ("BLOCK", "FAIL", Verdict.NOT_PROVEN.value)
    )


def validate_document(
    evidence_path: Path,
    *,
    task_id: str,
    warp_id: str,
    base_head: str,
    organ_id: str,
    check_id: str,
) -> dict[str, Any]:
    evidence = evidence_path.resolve()
    evidence_sha256 = sha256_file(evidence)
    document = json.loads(evidence.read_text(encoding="utf-8"))
    reasons: list[str] = []
    bindings = {
        "task_id": task_id,
        "warp_id": warp_id,
        "base_head": base_head,
        "organ_id": organ_id,
    }
    for field, expected in bindings.items():
        if document.get(field) != expected:
            reasons.append(f"{field.upper()}_BINDING_MISMATCH")
    measurement = _measurement(document, check_id)
    binding_failed = bool(reasons)
    if binding_failed:
        verdict = Verdict.BLOCK.value
    elif document.get("contradictions"):
        reasons.append("CONTRADICTORY_EVIDENCE_PRESENT")
        verdict = Verdict.BLOCK.value
    elif measurement is None:
        reasons.append("REQUIRED_CHECK_NOT_PROVEN")
        verdict = Verdict.NOT_PROVEN.value
    else:
        expected = measurement.get("expected")
        observed = measurement.get("observed")
        evidence_id = measurement.get("evidence_id")
        if "expected" not in measurement or "observed" not in measurement or not isinstance(evidence_id, str) or not evidence_id:
            reasons.append("MEASURED_CHECK_INCOMPLETE")
            verdict = Verdict.NOT_PROVEN.value
        elif _observation_passes(expected, observed):
            verdict = Verdict.PASS_PROVEN.value
        else:
            reasons.append("MEASURED_CHECK_FAILED")
            verdict = Verdict.BLOCK.value
    measured_check = None
    if measurement is not None:
        measured_check = {
            "check_id": check_id,
            "expected": measurement.get("expected"),
            "observed": measurement.get("observed"),
            "evidence_id": measurement.get("evidence_id"),
            "verdict": verdict,
        }
    return {
        "schema_version": "imperium.core_reference_corridor.organ_evidence_validation.v0_1",
        "validator_id": ORGAN_VALIDATOR_ID,
        "validator_version": ORGAN_VALIDATOR_VERSION,
        "evidence_path": str(evidence),
        "evidence_sha256": evidence_sha256,
        "task_id": task_id,
        "warp_id": warp_id,
        "base_head": base_head,
        "organ_id": organ_id,
        "check_id": check_id,
        "measured_check": measured_check,
        "reasons": reasons,
        "verdict": verdict,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--warp-id", required=True)
    parser.add_argument("--base-head", required=True)
    parser.add_argument("--organ-id", required=True)
    parser.add_argument("--check-id", required=True)
    args = parser.parse_args(argv)
    try:
        result = validate_document(
            args.evidence,
            task_id=args.task_id,
            warp_id=args.warp_id,
            base_head=args.base_head,
            organ_id=args.organ_id,
            check_id=args.check_id,
        )
    except Exception as exc:  # fail closed at the process boundary
        result = {
            "schema_version": "imperium.core_reference_corridor.organ_evidence_validation.v0_1",
            "verdict": Verdict.BLOCK.value,
            "reasons": [f"VALIDATOR_EXCEPTION:{type(exc).__name__}:{exc}"],
        }
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result["verdict"] in {Verdict.PASS_PROVEN.value, Verdict.NOT_PROVEN.value} else 2


if __name__ == "__main__":
    raise SystemExit(main())
