"""Canonical, evidence-derived organ verdict calculation.

Verdicts are computed from current bytes and a separate validator execution.
References, declared check names, or an organ's own requested verdict never
constitute proof on their own.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence



class Verdict(str, Enum):
    PASS_PROVEN = "PASS_PROVEN"
    PASS_WITH_DEBT = "PASS_WITH_DEBT"
    BLOCK = "BLOCK"
    NOT_PROVEN = "NOT_PROVEN"
    NOT_APPLICABLE_PROVEN = "NOT_APPLICABLE_PROVEN"


ORGAN_VALIDATOR_ID = "organ_evidence_validator_v1"
ORGAN_VALIDATOR_VERSION = "1.0.0"
OPERATIONAL = "OPERATIONAL"
SCAFFOLD_ONLY = "SCAFFOLD_ONLY"
_HEX = set("0123456789abcdef")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value.lower()) <= _HEX


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp missing")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp is not UTC")
    return parsed


@dataclass(frozen=True)
class VerdictContext:
    task_id: str
    warp_id: str
    base_head: str
    evidence_root: Path
    validator_root: Path


def run_validator(
    *,
    validator_path: Path | str,
    evidence_path: Path | str,
    organ_id: str,
    check_id: str,
    task_id: str,
    warp_id: str,
    base_head: str,
    timeout_seconds: float = 15,
    executable: Path | str | None = None,
) -> dict[str, Any]:
    """Execute one fixed validator in a separate process and return metadata."""

    validator = Path(validator_path).resolve()
    evidence = Path(evidence_path).resolve()
    python = Path(executable or sys.executable).resolve()
    argv = [
        str(python),
        str(validator),
        "--evidence",
        str(evidence),
        "--task-id",
        task_id,
        "--warp-id",
        warp_id,
        "--base-head",
        base_head,
        "--organ-id",
        organ_id,
        "--check-id",
        check_id,
    ]
    started = utc_now()
    timed_out = False
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    env_keys = ("SystemRoot", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP")
    env = {key: os.environ[key] for key in env_keys if key in os.environ}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "NO_COLOR": "1"})
    try:
        completed = subprocess.run(
            argv,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
        exit_code = completed.returncode
        stdout, stderr = completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    ended = utc_now()
    try:
        result = json.loads(stdout.strip()) if stdout.strip() else None
    except json.JSONDecodeError:
        result = None
    return {
        "schema_version": "imperium.core_reference_corridor.validator_execution.v0_1",
        "validator_id": ORGAN_VALIDATOR_ID,
        "validator_version": ORGAN_VALIDATOR_VERSION,
        "validator_adapter_path": str(validator),
        "validator_adapter_sha256": sha256_file(validator) if validator.is_file() else None,
        "executable_path": str(python),
        "validator_executable_path": str(python),
        "executable_sha256": sha256_file(python) if python.is_file() else None,
        "validator_sha256": sha256_file(python) if python.is_file() else None,
        "argv": argv,
        "exact_argv": argv,
        "started_at_utc": started,
        "ended_at_utc": ended,
        "finished_at_utc": ended,
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "stdout_sha256": _sha256_text(stdout),
        "stderr_sha256": _sha256_text(stderr),
        "result": result,
    }


def build_validated_claim(
    evidence_path: Path | str,
    *,
    validator_path: Path | str,
    organ_id: str,
    check_id: str,
    task_id: str,
    warp_id: str,
    base_head: str,
    classification: str = OPERATIONAL,
) -> dict[str, Any]:
    evidence = Path(evidence_path).resolve()
    execution = run_validator(
        validator_path=validator_path,
        evidence_path=evidence,
        organ_id=organ_id,
        check_id=check_id,
        task_id=task_id,
        warp_id=warp_id,
        base_head=base_head,
    )
    return {
        "check_id": check_id,
        "classification": classification,
        "evidence_ref": str(evidence),
        "evidence_sha256": sha256_file(evidence),
        "validator_execution": execution,
    }


def _result(check_id: str, critical: bool, verdict: str, reasons: list[str], **extra: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "critical": critical,
        "verdict": verdict,
        "reasons": reasons,
        **extra,
    }


def _execution_aliases(execution: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "validator_id": execution.get("validator_id"),
        "validator_version": execution.get("validator_version"),
        "validator_executable_path": execution.get("validator_executable_path"),
        "validator_sha256": execution.get("validator_sha256"),
        "exact_argv": execution.get("exact_argv"),
        "started_at_utc": execution.get("started_at_utc"),
        "finished_at_utc": execution.get("finished_at_utc"),
        "validator_exit_code": execution.get("exit_code"),
    }


def _resolve_scoped(raw: str, root: Path) -> Path:
    candidate = Path(raw)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if not _path_within(resolved, root):
        raise PermissionError(str(resolved))
    return resolved


def _argv_value(argv: Sequence[str], flag: str) -> str | None:
    try:
        index = list(argv).index(flag)
    except ValueError:
        return None
    return argv[index + 1] if index + 1 < len(argv) else None


def assess_check(
    organ_id: str,
    check_id: str,
    claim: Mapping[str, Any] | None,
    context: VerdictContext,
    *,
    critical: bool = True,
) -> dict[str, Any]:
    if not isinstance(claim, Mapping):
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["CHECK_CLAIM_MISSING"])
    classification = str(claim.get("classification", OPERATIONAL))
    evidence_ref = claim.get("evidence_ref")
    if not isinstance(evidence_ref, str) or not evidence_ref:
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["EVIDENCE_REF_MISSING"], classification=classification)
    try:
        evidence = _resolve_scoped(evidence_ref, context.evidence_root)
    except PermissionError:
        return _result(check_id, critical, Verdict.BLOCK.value, ["EVIDENCE_REF_OUTSIDE_ROOT"], evidence_ref=evidence_ref, classification=classification)
    if not evidence.is_file():
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["EVIDENCE_FILE_MISSING"], evidence_ref=evidence_ref, classification=classification)
    expected_hash = claim.get("evidence_sha256")
    if expected_hash is None:
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["EVIDENCE_HASH_MISSING"], evidence_ref=evidence_ref, classification=classification)
    if not _valid_sha256(expected_hash):
        return _result(check_id, critical, Verdict.BLOCK.value, ["EVIDENCE_HASH_INVALID"], evidence_ref=evidence_ref, classification=classification)
    actual_hash = sha256_file(evidence)
    if actual_hash != str(expected_hash).lower():
        return _result(check_id, critical, Verdict.BLOCK.value, ["EVIDENCE_HASH_MISMATCH"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    try:
        document = json.loads(evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _result(check_id, critical, Verdict.BLOCK.value, ["EVIDENCE_UNREADABLE"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    bindings = {"task_id": context.task_id, "warp_id": context.warp_id, "base_head": context.base_head}
    mismatches = [f"{field.upper()}_BINDING_MISMATCH" for field, expected in bindings.items() if document.get(field) != expected]
    if mismatches:
        return _result(check_id, critical, Verdict.BLOCK.value, mismatches, evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    execution = claim.get("validator_execution")
    if not isinstance(execution, Mapping):
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_EXECUTION_MISSING"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    required_meta = {
        "validator_id", "validator_version", "validator_adapter_path", "validator_adapter_sha256",
        "validator_sha256", "validator_executable_path", "exact_argv", "started_at_utc",
        "finished_at_utc", "exit_code", "result"
    }
    missing_meta = sorted(required_meta - set(execution))
    if missing_meta:
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_METADATA_MISSING:" + ",".join(missing_meta)], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    if execution.get("validator_id") != ORGAN_VALIDATOR_ID or execution.get("validator_version") != ORGAN_VALIDATOR_VERSION:
        return _result(
            check_id,
            critical,
            Verdict.BLOCK.value,
            ["VALIDATOR_IDENTITY_NOT_ADMITTED"],
            evidence_ref=evidence_ref,
            evidence_sha256=actual_hash,
            classification=classification,
        )
    try:
        validator = _resolve_scoped(str(execution["validator_adapter_path"]), context.validator_root)
    except PermissionError:
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_PATH_OUTSIDE_ROOT"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    if not validator.is_file():
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_FILE_MISSING"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    admitted_validator = Path(__file__).resolve().with_name("organ_evidence_validator.py")
    if validator != admitted_validator:
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_ADAPTER_NOT_ADMITTED"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    adapter_hash = execution.get("validator_adapter_sha256")
    if not _valid_sha256(adapter_hash) or sha256_file(validator) != str(adapter_hash).lower():
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_ADAPTER_HASH_MISMATCH"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    executable = Path(str(execution["validator_executable_path"]))
    if not executable.is_absolute() or not executable.is_file():
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_EXECUTABLE_MISSING"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    executable_hash = execution.get("validator_sha256")
    if not _valid_sha256(executable_hash) or sha256_file(executable) != str(executable_hash).lower():
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_EXECUTABLE_HASH_MISMATCH"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    argv = execution.get("exact_argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_ARGV_INVALID"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification)
    argv_bindings = {
        "--evidence": str(evidence),
        "--task-id": context.task_id,
        "--warp-id": context.warp_id,
        "--base-head": context.base_head,
        "--organ-id": organ_id,
        "--check-id": check_id,
    }
    argv_mismatches = [f"VALIDATOR_ARGV_BINDING_MISMATCH:{flag}" for flag, expected in argv_bindings.items() if _argv_value(argv, flag) != expected]
    if len(argv) < 2 or Path(argv[0]).resolve() != executable.resolve():
        argv_mismatches.append("VALIDATOR_ARGV_EXECUTABLE_MISMATCH")
    if len(argv) < 2 or Path(argv[1]).resolve() != validator:
        argv_mismatches.append("VALIDATOR_ARGV_PATH_MISMATCH")
    if argv_mismatches:
        return _result(check_id, critical, Verdict.BLOCK.value, argv_mismatches, evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, **_execution_aliases(execution))
    try:
        if _parse_timestamp(execution["finished_at_utc"]) < _parse_timestamp(execution["started_at_utc"]):
            raise ValueError("validator end precedes start")
    except (TypeError, ValueError):
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_TIME_INVALID"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, **_execution_aliases(execution))
    if execution.get("timed_out") or execution.get("exit_code") != 0:
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_PROCESS_FAILED"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, validator_execution=dict(execution), **_execution_aliases(execution))
    validation = execution.get("result")
    if not isinstance(validation, Mapping):
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_RESULT_MISSING"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, **_execution_aliases(execution))
    result_bindings = {
        "validator_id": execution["validator_id"],
        "validator_version": execution["validator_version"],
        "evidence_sha256": actual_hash,
        "task_id": context.task_id,
        "warp_id": context.warp_id,
        "base_head": context.base_head,
        "organ_id": organ_id,
        "check_id": check_id,
    }
    result_mismatches = [f"VALIDATOR_RESULT_BINDING_MISMATCH:{field}" for field, expected in result_bindings.items() if validation.get(field) != expected]
    if result_mismatches:
        return _result(check_id, critical, Verdict.BLOCK.value, result_mismatches, evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, **_execution_aliases(execution))
    if validation.get("verdict") == Verdict.NOT_PROVEN.value:
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["VALIDATOR_DID_NOT_PROVE_CHECK"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, validator_execution=dict(execution), **_execution_aliases(execution))
    if validation.get("verdict") != Verdict.PASS_PROVEN.value:
        return _result(check_id, critical, Verdict.BLOCK.value, ["VALIDATOR_REJECTED_EVIDENCE"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, validator_execution=dict(execution), **_execution_aliases(execution))
    if classification == SCAFFOLD_ONLY:
        return _result(check_id, critical, Verdict.NOT_PROVEN.value, ["SCAFFOLD_ONLY_NOT_OPERATIONAL_PROOF"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, validator_execution=dict(execution), **_execution_aliases(execution))
    if classification != OPERATIONAL:
        return _result(check_id, critical, Verdict.BLOCK.value, ["EVIDENCE_CLASSIFICATION_INVALID"], evidence_ref=evidence_ref, evidence_sha256=actual_hash, classification=classification, **_execution_aliases(execution))
    return _result(
        check_id,
        critical,
        Verdict.PASS_PROVEN.value,
        [],
        evidence_ref=evidence_ref,
        evidence_sha256=actual_hash,
        classification=classification,
        measured_check=dict(validation.get("measured_check", {})),
        validator_execution=dict(execution),
        **_execution_aliases(execution),
    )


def evaluate_organ(
    organ_id: str,
    required_checks: Sequence[str],
    claims: Mapping[str, Mapping[str, Any]] | None,
    context: VerdictContext,
    *,
    accepted_debt: Sequence[str] = (),
) -> dict[str, Any]:
    claim_map = claims if isinstance(claims, Mapping) else {}
    results = [assess_check(organ_id, check_id, claim_map.get(check_id), context) for check_id in required_checks]
    proven = [item["check_id"] for item in results if item["verdict"] == Verdict.PASS_PROVEN.value]
    not_proven = [
        {"check_id": item["check_id"], "reasons": item["reasons"]}
        for item in results
        if item["verdict"] == Verdict.NOT_PROVEN.value
    ]
    blocking = [
        {"check_id": item["check_id"], "reasons": item["reasons"], "evidence_ref": item.get("evidence_ref")}
        for item in results
        if item["verdict"] == Verdict.BLOCK.value
    ]
    debt = sorted({str(item) for item in accepted_debt if str(item)})
    total = max(1, len(required_checks))
    passed_ratio = len(proven) / total
    evidence_integrity = round(
        sum(1 for item in results if item.get("evidence_sha256") and item["verdict"] != Verdict.BLOCK.value) / total,
        3,
    )
    reproducibility = round(
        sum(1 for item in results if isinstance(item.get("validator_execution"), Mapping)) / total,
        3,
    )
    scope_coverage = round(passed_ratio, 3)
    unknown_count = len(not_proven)
    if blocking:
        verdict, confidence = Verdict.BLOCK.value, 0.0
    elif not_proven:
        verdict = Verdict.NOT_PROVEN.value
        confidence = round(min(passed_ratio, evidence_integrity, reproducibility, scope_coverage), 3)
    elif debt:
        verdict = Verdict.PASS_WITH_DEBT.value
        confidence = round(min(0.99, max(0.5, 1.0 - min(0.49, 0.1 * len(debt)))), 3)
    else:
        verdict, confidence = Verdict.PASS_PROVEN.value, 1.0
    return {
        "verdict": verdict,
        "confidence": confidence,
        "confidence_basis": {
            "required_checks_total": len(required_checks),
            "required_checks_passed": len(proven),
            "evidence_integrity": evidence_integrity,
            "reproducibility": reproducibility,
            "unknowns": unknown_count,
            "scope_coverage": scope_coverage,
            "accepted_debt_count": len(debt),
            "blocking_check_count": len(blocking),
        },
        "check_results": results,
        "proven": proven,
        "not_proven": not_proven,
        "accepted_debt": debt,
        "blocking_evidence": blocking,
        "evidence_refs": sorted({str(item["evidence_ref"]) for item in results if item.get("evidence_ref")}),
    }


def enforce_throne_guard(throne: dict[str, Any], organ_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    critical_blocks = []
    critical_not_proven = []
    for record in organ_records:
        if record.get("organ_id") == "THRONE":
            continue
        for result in record.get("check_results", []):
            if not isinstance(result, Mapping) or result.get("critical") is not True:
                continue
            if result.get("verdict") == Verdict.BLOCK.value:
                critical_blocks.append(
                    {
                        "organ_id": record.get("organ_id"),
                        "check_id": result.get("check_id"),
                        "reasons": result.get("reasons", []),
                        "evidence_ref": result.get("evidence_ref"),
                    }
                )
            elif result.get("verdict") == Verdict.NOT_PROVEN.value:
                critical_not_proven.append(
                    {
                        "organ_id": record.get("organ_id"),
                        "check_id": result.get("check_id"),
                        "reasons": result.get("reasons", []),
                    }
                )
    if critical_blocks:
        throne["verdict"] = Verdict.BLOCK.value
        throne["confidence"] = 0.0
        throne.setdefault("confidence_basis", {})["blocking_check_count"] = len(critical_blocks)
        throne.setdefault("blocking_evidence", []).extend(critical_blocks)
        throne.setdefault("not_proven", []).append(
            {"check_id": "critical_organ_block_absent", "reasons": ["CRITICAL_ORGAN_BLOCK_PRESENT"]}
        )
    elif critical_not_proven and str(throne.get("verdict", "")).startswith("PASS"):
        throne["verdict"] = Verdict.NOT_PROVEN.value
        throne["confidence"] = min(float(throne.get("confidence", 0.0)), 0.99)
        throne.setdefault("confidence_basis", {})["unknowns"] = len(critical_not_proven)
        throne.setdefault("not_proven", []).append(
            {
                "check_id": "critical_organ_proof_complete",
                "reasons": ["CRITICAL_ORGAN_NOT_PROVEN"],
                "organs": critical_not_proven,
            }
        )
    return throne
