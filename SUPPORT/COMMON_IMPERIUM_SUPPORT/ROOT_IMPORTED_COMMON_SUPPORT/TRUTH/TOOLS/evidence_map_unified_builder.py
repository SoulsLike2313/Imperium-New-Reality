#!/usr/bin/env python3
"""Build Unified Evidence Map foundation artifacts for NewGen truth spine."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-EVIDENCE-MAP-UNIFIED-VM3-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
CURRENT_TRUTH_REL = f"{TRUTH_ROOT_REL}/CURRENT_TRUTH_ROOT_V0_1.json"
REPORT_INDEX_REL = f"{TRUTH_ROOT_REL}/REPORT_STATUS_INDEX_V0_1.json"
EVIDENCE_SOURCE_MAP_REL = f"{TRUTH_ROOT_REL}/EVIDENCE_SOURCE_MAP_V0_1.json"
UNIFIED_MAP_REL = f"{TRUTH_ROOT_REL}/EVIDENCE_MAP_UNIFIED_V0_1.json"
FRESHNESS_INDEX_REL = f"{TRUTH_ROOT_REL}/EVIDENCE_FRESHNESS_INDEX_V0_1.json"
STATUS_NORMALIZATION_REL = f"{TRUTH_ROOT_REL}/REPORT_STATUS_NORMALIZATION_TABLE_V0_1.json"
NOT_PROVEN_REL = f"{TRUTH_ROOT_REL}/NOT_PROVEN_REGISTER_V0_1.json"
SANCTUM_STATE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

TASK_ID_RE = re.compile(r"(TASK-\d{8}-[A-Z0-9_-]+)")
TASK_DATE_RE = re.compile(r"TASK-(\d{8})-")

CANONICAL_STATUSES = [
    "PASS",
    "PASS_STRICT",
    "PASS_WITH_WARN",
    "WARN",
    "BLOCK",
    "PARTIAL",
    "UNKNOWN",
    "MISSING",
    "FOUNDATION_ONLY",
    "PENDING_POST_COMMIT",
    "STALE",
]

ALLOWED_FRESHNESS = [
    "CURRENT",
    "STALE",
    "UNKNOWN",
    "MISSING",
    "FOUNDATION_ONLY",
    "PARTIAL",
]

ALLOWED_PROOF_LEVELS = [
    "STRONG",
    "PARTIAL",
    "FOUNDATION",
    "WEAK",
    "UNKNOWN",
    "MISSING",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS" / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Build NewGen Unified Evidence Map foundation artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--unified-map-output", type=Path, default=default_repo_root / UNIFIED_MAP_REL)
    parser.add_argument("--freshness-index-output", type=Path, default=default_repo_root / FRESHNESS_INDEX_REL)
    parser.add_argument("--status-normalization-output", type=Path, default=default_repo_root / STATUS_NORMALIZATION_REL)
    parser.add_argument("--not-proven-output", type=Path, default=default_repo_root / NOT_PROVEN_REL)
    parser.add_argument("--current-truth-output", type=Path, default=default_repo_root / CURRENT_TRUTH_REL)
    parser.add_argument(
        "--build-report",
        type=Path,
        default=default_report_dir / "EVIDENCE_MAP_UNIFIED_BUILD_REPORT.json",
    )
    return parser.parse_args()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def task_id_from_text(text: str) -> str | None:
    match = TASK_ID_RE.search(text)
    if not match:
        return None
    return match.group(1)


def parse_task_date(task_id: str) -> dt.date | None:
    match = TASK_DATE_RE.search(task_id)
    if not match:
        return None
    digits = match.group(1)
    try:
        return dt.date(int(digits[0:4]), int(digits[4:6]), int(digits[6:8]))
    except ValueError:
        return None


def normalize_status(raw_status: str) -> str:
    status = raw_status.strip().upper()
    if status in {"PASS", "PASS_STRICT"}:
        return status
    if status in {"PASS_WITH_WARN", "PASS_WITH_WARNING", "PASS_WITH_WARNINGS"}:
        return "PASS_WITH_WARN"
    if status.startswith("PASS_WITH_WARN"):
        return "PASS_WITH_WARN"
    if status in {"WARN", "WARNING", "WARN_FOUNDATION_ONLY"}:
        return "WARN"
    if status in {"PARTIAL"}:
        return "PARTIAL"
    if status in {"UNKNOWN", ""}:
        return "UNKNOWN"
    if "MISSING" in status:
        return "MISSING"
    if "FOUNDATION" in status:
        return "FOUNDATION_ONLY"
    if "STALE" in status:
        return "STALE"
    if "PENDING" in status:
        return "PENDING_POST_COMMIT"
    if "BLOCK" in status or "FAIL" in status:
        return "BLOCK"
    return "UNKNOWN"


def status_to_proof_level(status: str) -> str:
    normalized = normalize_status(status)
    if normalized in {"PASS", "PASS_STRICT"}:
        return "STRONG"
    if normalized in {"PASS_WITH_WARN", "WARN", "PARTIAL", "STALE"}:
        return "PARTIAL"
    if normalized in {"FOUNDATION_ONLY", "PENDING_POST_COMMIT"}:
        return "FOUNDATION"
    if normalized == "MISSING":
        return "MISSING"
    if normalized == "BLOCK":
        return "WEAK"
    return "UNKNOWN"


def freshness_from_hint(status: str, freshness_hint: str, exists: bool) -> str:
    normalized = normalize_status(status)
    hint = freshness_hint.strip().upper()

    if not exists:
        return "MISSING"
    if normalized == "MISSING":
        return "MISSING"
    if normalized in {"FOUNDATION_ONLY", "PENDING_POST_COMMIT"}:
        return "FOUNDATION_ONLY"
    if normalized in {"PARTIAL", "WARN"}:
        return "PARTIAL"
    if normalized == "STALE":
        return "STALE"
    if hint in {"CURRENT", "STALE", "UNKNOWN"}:
        return hint
    return "UNKNOWN"


def summarize_counts(values: list[str], allowed: list[str]) -> dict[str, int]:
    result = {value: 0 for value in allowed}
    for value in values:
        if value in result:
            result[value] += 1
    return result


def normalize_report_link(path: str | None) -> str | None:
    if path is None:
        return None
    cleaned = str(path).strip()
    if not cleaned:
        return None
    return cleaned


def record_id(source_kind: str, source_path: str, task_id: str | None, phase_id: str | None) -> str:
    identity = f"{source_kind}|{source_path}|{task_id or 'NONE'}|{phase_id or 'NONE'}"
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:16].upper()
    return f"EVID-{digest}"


def evidence_status_from_source_entry(entry: dict[str, Any]) -> str:
    existence_status = str(entry.get("existence_status", "UNKNOWN")).strip().upper()
    proof_strength = str(entry.get("proof_strength", "UNKNOWN")).strip().upper()

    if existence_status == "MISSING":
        return "MISSING"
    if proof_strength == "STRONG":
        return "PASS"
    if proof_strength == "FOUNDATION":
        return "FOUNDATION_ONLY"
    if proof_strength == "PARTIAL":
        return "PARTIAL"
    if proof_strength == "WEAK":
        return "WARN"
    return "UNKNOWN"


def freshness_from_task_date(task_id: str | None, newest_task_date: dt.date | None) -> str:
    if task_id is None or newest_task_date is None:
        return "UNKNOWN"
    task_date = parse_task_date(task_id)
    if task_date is None:
        return "UNKNOWN"
    if (newest_task_date - task_date).days <= 1:
        return "CURRENT"
    return "STALE"


def linked_reports_from_refs(refs: list[str]) -> list[str]:
    paths: list[str] = []
    for raw in refs:
        ref = str(raw)
        if ref.startswith("FILE:IMPERIUM_NEW_GENERATION/REPORTS/"):
            paths.append(ref.removeprefix("FILE:"))
    return unique(paths)


def build_normalization_table(task_id: str, generated_at: str) -> dict[str, Any]:
    mappings = [
        {
            "raw_status": "PASS",
            "canonical_status": "PASS",
            "freshness_hint": "CURRENT",
            "proof_level_hint": "STRONG",
            "no_fake_green_note": "PASS remains PASS only with linked evidence.",
        },
        {
            "raw_status": "PASS_STRICT",
            "canonical_status": "PASS_STRICT",
            "freshness_hint": "CURRENT",
            "proof_level_hint": "STRONG",
            "no_fake_green_note": "STRICT PASS still requires receipts and validator proof.",
        },
        {
            "raw_status": "PASS_WITH_WARN",
            "canonical_status": "PASS_WITH_WARN",
            "freshness_hint": "PARTIAL",
            "proof_level_hint": "PARTIAL",
            "no_fake_green_note": "Warnings remain explicit; do not upgrade to strict PASS.",
        },
        {
            "raw_status": "WARN",
            "canonical_status": "WARN",
            "freshness_hint": "PARTIAL",
            "proof_level_hint": "PARTIAL",
            "no_fake_green_note": "WARN is not acceptable as full proof success.",
        },
        {
            "raw_status": "BLOCK",
            "canonical_status": "BLOCK",
            "freshness_hint": "UNKNOWN",
            "proof_level_hint": "WEAK",
            "no_fake_green_note": "BLOCK is never re-labeled as PASS.",
        },
        {
            "raw_status": "PARTIAL",
            "canonical_status": "PARTIAL",
            "freshness_hint": "PARTIAL",
            "proof_level_hint": "PARTIAL",
            "no_fake_green_note": "PARTIAL keeps unresolved boundaries explicit.",
        },
        {
            "raw_status": "UNKNOWN",
            "canonical_status": "UNKNOWN",
            "freshness_hint": "UNKNOWN",
            "proof_level_hint": "UNKNOWN",
            "no_fake_green_note": "UNKNOWN stays UNKNOWN until direct evidence exists.",
        },
        {
            "raw_status": "MISSING",
            "canonical_status": "MISSING",
            "freshness_hint": "MISSING",
            "proof_level_hint": "MISSING",
            "no_fake_green_note": "Missing artifacts are never treated as green.",
        },
        {
            "raw_status": "FOUNDATION_ONLY",
            "canonical_status": "FOUNDATION_ONLY",
            "freshness_hint": "FOUNDATION_ONLY",
            "proof_level_hint": "FOUNDATION",
            "no_fake_green_note": "Foundation-only does not imply production proof.",
        },
        {
            "raw_status": "PENDING_POST_COMMIT",
            "canonical_status": "PENDING_POST_COMMIT",
            "freshness_hint": "FOUNDATION_ONLY",
            "proof_level_hint": "FOUNDATION",
            "no_fake_green_note": "Pending closure cannot be reported as complete PASS.",
        },
        {
            "raw_status": "STALE",
            "canonical_status": "STALE",
            "freshness_hint": "STALE",
            "proof_level_hint": "PARTIAL",
            "no_fake_green_note": "Stale evidence cannot be treated as current truth.",
        },
    ]

    return {
        "schema_id": "REPORT_STATUS_NORMALIZATION_TABLE_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "canonical_statuses": CANONICAL_STATUSES,
        "mappings": mappings,
        "limitations": [
            "Normalization is deterministic and foundation-oriented.",
            "Unknown legacy variants default to UNKNOWN to avoid fake-green upgrades.",
        ],
    }


def collect_unified_records(
    repo_root: Path,
    task_id: str,
    current_truth: dict[str, Any],
    report_index: dict[str, Any],
    evidence_source_map: dict[str, Any],
    newest_task_date: dt.date | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    records: list[dict[str, Any]] = []

    report_entries = report_index.get("entries", [])
    if not isinstance(report_entries, list):
        report_entries = []

    for entry in report_entries:
        if not isinstance(entry, dict):
            continue

        source_path = str(entry.get("report_path", "")).strip()
        linked_reports = unique(
            [
                item
                for item in [
                    normalize_report_link(source_path),
                    normalize_report_link(entry.get("validator_report_path")),
                    normalize_report_link(entry.get("final_owner_report_path")),
                    normalize_report_link(entry.get("final_receipt_path")),
                ]
                if item is not None
            ]
        )

        derived_task_id = str(entry.get("task_id", "")).strip() or None
        source_exists = bool(source_path) and (repo_root / source_path).exists()
        status = normalize_status(str(entry.get("status", "UNKNOWN")))
        date_freshness = freshness_from_task_date(derived_task_id, newest_task_date)
        hinted_freshness = str(entry.get("freshness", date_freshness)).strip().upper()
        freshness = freshness_from_hint(status, hinted_freshness, source_exists)

        proof_level = status_to_proof_level(status)
        notes = entry.get("notes", [])
        if not isinstance(notes, list):
            notes = []
        known_limitations = [str(item) for item in notes]
        if not source_exists:
            known_limitations.append("report_path_missing_or_not_materialized")

        record = {
            "evidence_id": record_id("REPORT_STATUS_INDEX_ENTRY", source_path, derived_task_id, None),
            "source_path": source_path,
            "source_kind": "REPORT_STATUS_INDEX_ENTRY",
            "task_id": derived_task_id,
            "phase_id": None,
            "status": status,
            "freshness": freshness,
            "proof_level": proof_level,
            "linked_reports": linked_reports,
            "known_limitations": unique(known_limitations),
        }
        records.append(record)

    phase_coverage = current_truth.get("phase_coverage", {})
    raw_phases = []
    if isinstance(phase_coverage, dict):
        raw_phases = phase_coverage.get("phases", [])
    if not isinstance(raw_phases, list):
        raw_phases = []

    for phase in raw_phases:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("phase_id", "")).strip() or None
        phase_status = normalize_status(str(phase.get("status", "UNKNOWN")))
        refs = phase.get("evidence_refs", [])
        if not isinstance(refs, list):
            refs = []

        source_path = f"{CURRENT_TRUTH_REL}::{phase_id or 'PHASE_UNKNOWN'}"
        linked_reports = linked_reports_from_refs([str(item) for item in refs])
        limits = phase.get("limitations", [])
        if not isinstance(limits, list):
            limits = []

        records.append(
            {
                "evidence_id": record_id("CURRENT_TRUTH_PHASE_ENTRY", source_path, str(current_truth.get("task_id", "")).strip() or None, phase_id),
                "source_path": source_path,
                "source_kind": "CURRENT_TRUTH_PHASE_ENTRY",
                "task_id": str(current_truth.get("task_id", "")).strip() or None,
                "phase_id": phase_id,
                "status": phase_status,
                "freshness": freshness_from_hint(phase_status, "FOUNDATION_ONLY", True),
                "proof_level": status_to_proof_level(phase_status),
                "linked_reports": linked_reports,
                "known_limitations": unique([str(item) for item in limits] + ["phase_coverage_snapshot_only"]),
            }
        )

    source_entries = evidence_source_map.get("entries", [])
    if not isinstance(source_entries, list):
        source_entries = []

    for entry in source_entries:
        if not isinstance(entry, dict):
            continue
        source_path = str(entry.get("path", "")).strip()
        source_exists = bool(source_path) and (repo_root / source_path).exists()
        evidence_status = evidence_status_from_source_entry(entry)

        derived_task_id = task_id_from_text(source_path)
        date_freshness = freshness_from_task_date(derived_task_id, newest_task_date)
        freshness = freshness_from_hint(evidence_status, date_freshness, source_exists)

        raw_strength = str(entry.get("proof_strength", "UNKNOWN")).strip().upper()
        strength_map = {
            "STRONG": "STRONG",
            "FOUNDATION": "FOUNDATION",
            "PARTIAL": "PARTIAL",
            "WEAK": "WEAK",
            "UNKNOWN": "UNKNOWN",
        }
        proof_level = strength_map.get(raw_strength, "UNKNOWN")
        if not source_exists and proof_level != "MISSING":
            proof_level = "MISSING"

        phase_id_raw = str(entry.get("phase_id", "")).strip()
        phase_id = phase_id_raw if phase_id_raw and phase_id_raw != "GLOBAL_REPORT_INDEX" else None

        linked_reports = [source_path] if "/REPORTS/" in source_path else []
        known_limitations = entry.get("known_limitations", [])
        if not isinstance(known_limitations, list):
            known_limitations = []

        records.append(
            {
                "evidence_id": record_id("EVIDENCE_SOURCE_MAP_ENTRY", source_path, derived_task_id, phase_id),
                "source_path": source_path,
                "source_kind": "EVIDENCE_SOURCE_MAP_ENTRY",
                "task_id": derived_task_id,
                "phase_id": phase_id,
                "status": evidence_status,
                "freshness": freshness,
                "proof_level": proof_level,
                "linked_reports": linked_reports,
                "known_limitations": unique([str(item) for item in known_limitations] + ["legacy_evidence_map_snapshot"]),
            }
        )

    sanctum_state_path = repo_root / SANCTUM_STATE_REL
    sanctum_exists = sanctum_state_path.exists()
    sanctum_status = "FOUNDATION_ONLY" if sanctum_exists else "MISSING"
    sanctum_freshness = "FOUNDATION_ONLY" if sanctum_exists else "MISSING"

    records.append(
        {
            "evidence_id": record_id("SANCTUM_STATE_REFERENCE", SANCTUM_STATE_REL, None, None),
            "source_path": SANCTUM_STATE_REL,
            "source_kind": "SANCTUM_STATE_REFERENCE",
            "task_id": None,
            "phase_id": None,
            "status": sanctum_status,
            "freshness": sanctum_freshness,
            "proof_level": "FOUNDATION" if sanctum_exists else "MISSING",
            "linked_reports": [],
            "known_limitations": [
                "sanctum_state_is_read_only_foundation_surface",
                "no_live_backend_claim",
            ],
        }
    )

    if not sanctum_exists:
        warnings.append("SANCTUM_STATE_MISSING")

    if not records:
        warnings.append("UNIFIED_RECORDS_EMPTY")

    records.sort(key=lambda item: (item["source_kind"], item["source_path"], item["evidence_id"]))
    return records, unique(warnings)


def build_freshness_index(task_id: str, generated_at: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for record in records:
        entries.append(
            {
                "evidence_id": record["evidence_id"],
                "source_path": record["source_path"],
                "freshness": record["freshness"],
                "status": record["status"],
                "notes": [
                    f"source_kind={record['source_kind']}",
                    f"proof_level={record['proof_level']}",
                ],
            }
        )

    freshness_values = [entry["freshness"] for entry in entries]

    return {
        "schema_id": "EVIDENCE_FRESHNESS_INDEX_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "allowed_freshness_values": ALLOWED_FRESHNESS,
        "entries": entries,
        "summary": {
            "total_entries": len(entries),
            "freshness_counts": summarize_counts(freshness_values, ALLOWED_FRESHNESS),
        },
        "limitations": [
            "Freshness derives from bounded report/task/date signals, not runtime telemetry.",
            "FOUNDATION_ONLY and PARTIAL are explicit non-production freshness classes.",
        ],
    }


def build_not_proven_register(
    task_id: str,
    generated_at: str,
    records: list[dict[str, Any]],
    current_truth: dict[str, Any],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for record in records:
        status = normalize_status(record["status"])
        if status not in {"WARN", "UNKNOWN", "MISSING", "PARTIAL", "FOUNDATION_ONLY", "STALE", "PENDING_POST_COMMIT"}:
            continue

        area = record["source_kind"]
        claim_id = "CLAIM-" + hashlib.sha1(f"{record['evidence_id']}|{status}".encode("utf-8")).hexdigest()[:12].upper()

        if status == "MISSING":
            reason = "Required evidence path is missing."
            next_step = "Create or restore missing artifact before PASS claim."
        elif status in {"UNKNOWN", "STALE"}:
            reason = "Evidence freshness or certainty is not current/proven."
            next_step = "Run a bounded verification/update task and re-index freshness."
        elif status == "FOUNDATION_ONLY":
            reason = "Artifact is foundation-level, not production proof."
            next_step = "Promote with strict validator coverage when scoped by Owner."
        elif status == "PENDING_POST_COMMIT":
            reason = "Closure metadata is pending post-commit finalization."
            next_step = "Finalize closure receipt and re-run validator."
        else:
            reason = "Evidence is partial or warn-level."
            next_step = "Tighten evidence links and clarify missing criteria."

        entries.append(
            {
                "claim_id": claim_id,
                "area": area,
                "source_ref": record["source_path"],
                "current_status": status,
                "reason": reason,
                "recommended_next_step": next_step,
                "linked_evidence_ids": [record["evidence_id"]],
            }
        )

    known_warnings = current_truth.get("known_warnings", [])
    if isinstance(known_warnings, list):
        for index, warning in enumerate(known_warnings, start=1):
            entries.append(
                {
                    "claim_id": f"CLAIM-KNOWN-WARNING-{index:03d}",
                    "area": "CURRENT_TRUTH_ROOT",
                    "source_ref": CURRENT_TRUTH_REL,
                    "current_status": "WARN",
                    "reason": str(warning),
                    "recommended_next_step": "Keep warning explicit and map it to a bounded follow-up task.",
                    "linked_evidence_ids": [],
                }
            )

    # Keep register compact and focused.
    entries = entries[:120]

    status_values = [entry["current_status"] for entry in entries]

    return {
        "schema_id": "NOT_PROVEN_REGISTER_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "entries": entries,
        "summary": {
            "total_entries": len(entries),
            "status_counts": summarize_counts(
                status_values,
                ["WARN", "UNKNOWN", "MISSING", "PARTIAL", "FOUNDATION_ONLY", "STALE", "PENDING_POST_COMMIT"],
            ),
        },
        "limitations": [
            "This register tracks unresolved proof zones and does not auto-resolve UNKNOWN.",
            "Entries are bounded to high-signal foundation artifacts only.",
        ],
    }


def update_current_truth_root(
    repo_root: Path,
    task_id: str,
    generated_at: str,
    current_truth: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(current_truth)

    payload["task_id"] = task_id
    payload["generated_at_utc"] = generated_at

    repo_truth = payload.get("repo_truth", {})
    if not isinstance(repo_truth, dict):
        repo_truth = {}

    repo_truth["repo_root"] = str(repo_root)
    repo_truth["head"] = run_git(repo_root, "rev-parse", "HEAD")
    repo_truth["branch"] = run_git(repo_root, "branch", "--show-current")
    repo_truth["worktree_dirty"] = bool(run_git(repo_root, "status", "--short"))
    repo_truth["head_commit_utc"] = run_git(repo_root, "show", "-s", "--format=%cI", "HEAD")
    payload["repo_truth"] = repo_truth

    payload["report_status_index_path"] = REPORT_INDEX_REL
    payload["evidence_source_map_path"] = EVIDENCE_SOURCE_MAP_REL
    payload["evidence_map_unified_path"] = UNIFIED_MAP_REL
    payload["evidence_freshness_index_path"] = FRESHNESS_INDEX_REL
    payload["report_status_normalization_table_path"] = STATUS_NORMALIZATION_REL
    payload["not_proven_register_path"] = NOT_PROVEN_REL

    payload["evidence_unification"] = {
        "status": "FOUNDATION_ONLY",
        "evidence_map_unified_path": UNIFIED_MAP_REL,
        "evidence_freshness_index_path": FRESHNESS_INDEX_REL,
        "report_status_normalization_table_path": STATUS_NORMALIZATION_REL,
        "not_proven_register_path": NOT_PROVEN_REL,
        "known_limitations": [
            "Foundation-only evidence unification; no production autonomy claim.",
            "Unknown zones remain explicit in NOT_PROVEN_REGISTER_V0_1.",
        ],
        "updated_at_utc": generated_at,
    }

    limitations = payload.get("limitations", [])
    if not isinstance(limitations, list):
        limitations = []
    limitations.append("Unified evidence map/freshness layer is foundation-only and intentionally conservative.")
    payload["limitations"] = unique([str(item) for item in limitations])

    known_warnings = payload.get("known_warnings", [])
    if not isinstance(known_warnings, list):
        known_warnings = []
    payload["known_warnings"] = unique([str(item) for item in known_warnings])

    return payload


def build_payloads(repo_root: Path, task_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    generated_at = utc_now()

    current_truth_path = repo_root / CURRENT_TRUTH_REL
    report_index_path = repo_root / REPORT_INDEX_REL
    evidence_source_map_path = repo_root / EVIDENCE_SOURCE_MAP_REL

    current_truth = load_json(current_truth_path) or {}
    report_index = load_json(report_index_path) or {}
    evidence_source_map = load_json(evidence_source_map_path) or {}

    report_entries = report_index.get("entries", [])
    if not isinstance(report_entries, list):
        report_entries = []

    task_dates = []
    for entry in report_entries:
        if not isinstance(entry, dict):
            continue
        tid = str(entry.get("task_id", "")).strip()
        date = parse_task_date(tid)
        if date is not None:
            task_dates.append(date)

    newest_task_date = max(task_dates) if task_dates else None

    unified_records, warnings = collect_unified_records(
        repo_root,
        task_id,
        current_truth,
        report_index,
        evidence_source_map,
        newest_task_date,
    )

    unified_map = {
        "schema_id": "EVIDENCE_MAP_UNIFIED_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "records": unified_records,
        "summary": {
            "total_records": len(unified_records),
            "status_counts": summarize_counts([item["status"] for item in unified_records], CANONICAL_STATUSES),
            "freshness_counts": summarize_counts([item["freshness"] for item in unified_records], ALLOWED_FRESHNESS),
            "source_kind_counts": summarize_counts(
                [item["source_kind"] for item in unified_records],
                sorted({item["source_kind"] for item in unified_records}),
            ),
            "proof_level_counts": summarize_counts([item["proof_level"] for item in unified_records], ALLOWED_PROOF_LEVELS),
        },
        "limitations": [
            "Unified map is assembled from bounded foundation artifacts only.",
            "No UNKNOWN zone is auto-resolved; unresolved zones are carried into not-proven register.",
        ],
    }

    freshness_index = build_freshness_index(task_id, generated_at, unified_records)
    normalization_table = build_normalization_table(task_id, generated_at)
    not_proven_register = build_not_proven_register(task_id, generated_at, unified_records, current_truth)

    updated_current_truth = update_current_truth_root(repo_root, task_id, generated_at, current_truth)

    build_report = {
        "schema_id": "EVIDENCE_MAP_UNIFIED_BUILD_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "PASS_WITH_WARN" if warnings else "PASS",
        "outputs": {
            "evidence_map_unified": UNIFIED_MAP_REL,
            "evidence_freshness_index": FRESHNESS_INDEX_REL,
            "report_status_normalization_table": STATUS_NORMALIZATION_REL,
            "not_proven_register": NOT_PROVEN_REL,
            "current_truth_root": CURRENT_TRUTH_REL,
        },
        "warnings": warnings,
        "no_fake_green_note": "Builder keeps MISSING/UNKNOWN/PARTIAL/FOUNDATION_ONLY explicit and does not upgrade by assumption.",
    }

    return (
        unified_map,
        freshness_index,
        normalization_table,
        not_proven_register,
        updated_current_truth,
        build_report,
    )


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)

    (
        unified_map,
        freshness_index,
        normalization_table,
        not_proven_register,
        updated_current_truth,
        build_report,
    ) = build_payloads(repo_root, task_id)

    write_json(args.unified_map_output.resolve(), unified_map)
    write_json(args.freshness_index_output.resolve(), freshness_index)
    write_json(args.status_normalization_output.resolve(), normalization_table)
    write_json(args.not_proven_output.resolve(), not_proven_register)
    write_json(args.current_truth_output.resolve(), updated_current_truth)
    write_json(args.build_report.resolve(), build_report)

    print("build_status=PASS")
    print(f"evidence_map_unified={args.unified_map_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"evidence_freshness_index={args.freshness_index_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"report_status_normalization_table={args.status_normalization_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"not_proven_register={args.not_proven_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"current_truth_root_updated={args.current_truth_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"build_report={args.build_report.resolve().relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
