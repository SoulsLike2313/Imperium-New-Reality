#!/usr/bin/env python3
"""Build NewGen foundation Current Truth Root + Report Status Index + Evidence Source Map."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-CURRENT-TRUTH-ROOT-REPORT-INDEX-VM3-V0_1"
PHASE_REGISTRY_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_PHASE_REGISTRY_V0_1.json"
SANCTUM_STATE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
REPORTS_ROOT_REL = "IMPERIUM_NEW_GENERATION/REPORTS"
CURRENT_TRUTH_REL = "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json"
REPORT_STATUS_INDEX_REL = "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json"
EVIDENCE_SOURCE_MAP_REL = "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_SOURCE_MAP_V0_1.json"
SANCTUM_RECENT_PREFIX = "TASK-20260522-NEWGEN-SANCTUM-"

ALLOWED_STATUSES = [
    "PASS",
    "PASS_WITH_WARN",
    "WARN",
    "BLOCK",
    "UNKNOWN",
    "MISSING",
    "PARTIAL",
    "FOUNDATION_ONLY",
]

FORBIDDEN_CLAIMS = [
    "PRODUCTION_READY",
    "LIVE_BACKEND_READY",
    "AUTONOMOUS_EXECUTION_READY",
    "LIVE_ORGAN_DIALOGUE_READY",
    "FULL_AGENT_AUTONOMY_READY",
]

TASK_ID_RE = re.compile(r"(TASK-\d{8}-[A-Z0-9_-]+)")
TASK_DATE_RE = re.compile(r"TASK-(\d{8})-")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / REPORTS_ROOT_REL / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Build NewGen Current Truth Root v0.1 foundation artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--current-truth-output", type=Path, default=default_repo_root / CURRENT_TRUTH_REL)
    parser.add_argument("--report-index-output", type=Path, default=default_repo_root / REPORT_STATUS_INDEX_REL)
    parser.add_argument("--evidence-map-output", type=Path, default=default_repo_root / EVIDENCE_SOURCE_MAP_REL)
    parser.add_argument(
        "--build-report",
        type=Path,
        default=default_report_dir / "CURRENT_TRUTH_BUILD_REPORT.json",
    )
    return parser.parse_args()


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


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
    if match:
        return match.group(1)
    return None


def parse_task_date(task_id: str) -> dt.date | None:
    match = TASK_DATE_RE.search(task_id)
    if not match:
        return None
    digits = match.group(1)
    try:
        return dt.date(int(digits[0:4]), int(digits[4:6]), int(digits[6:8]))
    except ValueError:
        return None


def normalize_report_status(raw_status: str) -> str:
    status = raw_status.strip().upper()
    if status in {"PASS", "PASS_STRICT"}:
        return "PASS"
    if status in {"PASS_WITH_WARN", "PASS_WITH_WARNING", "PASS_WITH_WARNINGS"}:
        return "PASS_WITH_WARN"
    if status.startswith("PASS_WITH_WARN"):
        return "PASS_WITH_WARN"
    if status in {"WARN", "WARNING", "WARN_FOUNDATION_ONLY"}:
        return "WARN"
    if "BLOCK" in status or "FAIL" in status:
        return "BLOCK"
    if "FOUNDATION" in status:
        return "FOUNDATION_ONLY"
    if "PARTIAL" in status:
        return "PARTIAL"
    if "MISSING" in status:
        return "MISSING"
    if status == "UNKNOWN" or not status:
        return "UNKNOWN"
    return "FOUNDATION_ONLY"


def map_phase_status(registry_status: str, has_existing: bool, has_missing: bool) -> str:
    base = normalize_report_status(registry_status)
    if not has_existing:
        return "MISSING"
    if has_missing and base in {"PASS", "FOUNDATION_ONLY"}:
        return "PARTIAL"
    return base


def list_report_references(entry: dict[str, Any]) -> list[tuple[str, str]]:
    mapping = [
        ("architecture_refs", "ARCHITECTURE_REF"),
        ("contract_refs", "CONTRACT_REF"),
        ("report_refs", "REPORT_REF"),
        ("validator_refs", "VALIDATOR_REF"),
        ("evidence_refs", "EVIDENCE_REF"),
    ]
    refs: list[tuple[str, str]] = []
    for key, evidence_type in mapping:
        values = entry.get(key, [])
        if not isinstance(values, list):
            continue
        for raw in values:
            rel = str(raw).strip()
            if rel:
                refs.append((evidence_type, rel))
    return refs


def proof_strength_for_status(status: str, exists: bool) -> str:
    if not exists:
        return "WEAK"
    if status == "PASS":
        return "STRONG"
    if status == "PASS_WITH_WARN":
        return "PARTIAL"
    if status == "FOUNDATION_ONLY":
        return "FOUNDATION"
    if status in {"WARN", "PARTIAL"}:
        return "PARTIAL"
    if status == "MISSING":
        return "WEAK"
    return "UNKNOWN"


def collect_phase_coverage(
    repo_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, set[str]], list[dict[str, Any]], list[str]]:
    phase_registry_path = repo_root / PHASE_REGISTRY_REL
    phase_registry = load_json(phase_registry_path)
    warnings: list[str] = []
    task_to_phases: dict[str, set[str]] = {}
    evidence_entries: list[dict[str, Any]] = []

    if phase_registry is None:
        warnings.append("PHASE_REGISTRY_MISSING_OR_INVALID")
        phases = []
        for phase_no in range(1, 11):
            phase_id = f"PHASE_{phase_no:02d}_UNKNOWN"
            phases.append(
                {
                    "phase_no": phase_no,
                    "phase_id": phase_id,
                    "name": f"Phase {phase_no}",
                    "status": "MISSING",
                    "evidence_refs": [],
                    "limitations": ["Phase registry is missing or invalid JSON."],
                }
            )
        return phases, task_to_phases, evidence_entries, warnings

    raw_phases = phase_registry.get("phases", [])
    if not isinstance(raw_phases, list):
        raw_phases = []

    sorted_phases = sorted(
        [item for item in raw_phases if isinstance(item, dict)],
        key=lambda item: int(item.get("display_order", 999)),
    )

    phases: list[dict[str, Any]] = []
    seen_numbers: set[int] = set()

    for entry in sorted_phases:
        phase_no = int(entry.get("display_order", 0))
        phase_id = str(entry.get("phase_id", f"PHASE_{phase_no:02d}_UNKNOWN")).strip()
        name = str(entry.get("title", f"Phase {phase_no}")).strip() or f"Phase {phase_no}"
        seen_numbers.add(phase_no)

        refs = list_report_references(entry)
        existing_refs: list[str] = []
        missing_refs: list[str] = []
        for evidence_type, rel in refs:
            abs_path = repo_root / rel
            exists = abs_path.exists()
            if exists:
                existing_refs.append(rel)
            else:
                missing_refs.append(rel)
            evidence_entries.append(
                {
                    "phase_id": phase_id,
                    "evidence_type": evidence_type,
                    "path": rel,
                    "existence_status": "EXISTS" if exists else "MISSING",
                    "proof_strength": proof_strength_for_status(
                        map_phase_status(str(entry.get("status", "UNKNOWN")), bool(existing_refs), bool(missing_refs)),
                        exists,
                    ),
                    "known_limitations": [
                        "From SANCTUM_NG phase registry foundation map.",
                    ],
                }
            )

            if evidence_type == "REPORT_REF":
                task_id = task_id_from_text(rel)
                if task_id:
                    task_to_phases.setdefault(task_id, set()).add(phase_id)

        phase_status = map_phase_status(str(entry.get("status", "UNKNOWN")), bool(existing_refs), bool(missing_refs))
        evidence_refs = [f"FILE:{ref}" for ref in existing_refs]
        evidence_refs.append(f"REGISTRY:{phase_id}")
        limitations = [f"Registry declared status={str(entry.get('status', 'UNKNOWN')).upper()}"]
        if missing_refs:
            limitations.append("Missing refs: " + ", ".join(sorted(missing_refs)))
        known_warnings = entry.get("known_warnings", [])
        if isinstance(known_warnings, list) and known_warnings:
            limitations.extend(str(item) for item in known_warnings)

        if phase_status in {"WARN", "PARTIAL", "MISSING", "UNKNOWN"}:
            warnings.append(f"{phase_id}_{phase_status}")

        phases.append(
            {
                "phase_no": phase_no,
                "phase_id": phase_id,
                "name": name,
                "status": phase_status,
                "evidence_refs": unique(evidence_refs),
                "limitations": unique(limitations),
            }
        )

    for expected in range(1, 11):
        if expected in seen_numbers:
            continue
        phase_id = f"PHASE_{expected:02d}_MISSING"
        phases.append(
            {
                "phase_no": expected,
                "phase_id": phase_id,
                "name": f"Phase {expected}",
                "status": "MISSING",
                "evidence_refs": [f"REGISTRY:{phase_id}"],
                "limitations": ["Missing from SANCTUM_NG phase registry."],
            }
        )
        warnings.append(f"{phase_id}_MISSING")

    phases.sort(key=lambda item: int(item["phase_no"]))
    return phases, task_to_phases, evidence_entries, unique(warnings)


def first_existing_path(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def freshness_from_task_ids(task_ids: list[str], subject_task_id: str) -> str:
    all_dates = [parse_task_date(item) for item in task_ids]
    valid_dates = [item for item in all_dates if item is not None]
    subject_date = parse_task_date(subject_task_id)
    if subject_date is None or not valid_dates:
        return "UNKNOWN"
    newest = max(valid_dates)
    if (newest - subject_date).days <= 1:
        return "CURRENT"
    return "STALE"


def collect_report_status_index(
    repo_root: Path,
    task_id: str,
    phase_task_map: dict[str, set[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    reports_root = repo_root / REPORTS_ROOT_REL
    warnings: list[str] = []
    evidence_entries: list[dict[str, Any]] = []

    task_ids: set[str] = set(phase_task_map.keys())
    task_ids.add(task_id)

    if reports_root.exists():
        for child in sorted(reports_root.iterdir()):
            if not child.is_dir():
                continue
            name = child.name
            if name.startswith(SANCTUM_RECENT_PREFIX):
                task_ids.add(name)

    sorted_tasks = sorted(task_ids)
    entries: list[dict[str, Any]] = []

    for report_task_id in sorted_tasks:
        report_dir = reports_root / report_task_id
        report_rel = report_dir.relative_to(repo_root).as_posix()

        validator_path = first_existing_path(
            [
                report_dir / "VALIDATOR_REPORT.json",
                report_dir / "ACTION_LAYER_VALIDATOR_REPORT.json",
            ]
        )
        owner_report_path = first_existing_path(
            [
                report_dir / "FINAL_OWNER_REPORT_RU.md",
                report_dir / "OWNER_REPORT_RU.md",
            ]
        )
        final_receipt_path = report_dir / "FINAL_RECEIPT.json"

        raw_status = "UNKNOWN"
        notes: list[str] = []
        if not report_dir.exists():
            normalized_status = "MISSING"
            notes.append("REPORT_DIR_MISSING")
        else:
            if final_receipt_path.exists():
                receipt = load_json(final_receipt_path)
                if receipt is None:
                    raw_status = "UNKNOWN"
                    notes.append("FINAL_RECEIPT_INVALID_JSON")
                else:
                    raw_status = str(receipt.get("status", receipt.get("verdict", receipt.get("task_verdict", "UNKNOWN"))))
            else:
                raw_status = "FOUNDATION_ONLY" if report_task_id == task_id else "MISSING"
                notes.append("FINAL_RECEIPT_MISSING")

            normalized_status = normalize_report_status(raw_status)

        if report_task_id == task_id and normalized_status in {"MISSING", "UNKNOWN"}:
            normalized_status = "FOUNDATION_ONLY"
            notes.append("TASK_IN_PROGRESS_FOUNDATION_ONLY")

        evidence_refs: list[str] = []
        if final_receipt_path.exists():
            evidence_refs.append(f"FILE:{final_receipt_path.relative_to(repo_root).as_posix()}")
        if validator_path is not None:
            evidence_refs.append(f"FILE:{validator_path.relative_to(repo_root).as_posix()}")
        if owner_report_path is not None:
            evidence_refs.append(f"FILE:{owner_report_path.relative_to(repo_root).as_posix()}")

        phase_ids = sorted(phase_task_map.get(report_task_id, set()))
        for phase_id in phase_ids:
            evidence_refs.append(f"PHASE:{phase_id}")

        if normalized_status in {"PASS", "PASS_WITH_WARN"} and not evidence_refs:
            normalized_status = "WARN"
            notes.append("PASS_WITHOUT_EVIDENCE_DOWNGRADED_TO_WARN")

        if validator_path is None:
            notes.append("VALIDATOR_REPORT_MISSING")
        if owner_report_path is None:
            notes.append("FINAL_OWNER_REPORT_MISSING")
        if normalized_status == "FOUNDATION_ONLY" and report_task_id != task_id:
            notes.append("FOUNDATION_STATUS_FROM_LEGACY_RECEIPT")

        entry = {
            "task_id": report_task_id,
            "report_path": report_rel,
            "validator_report_path": validator_path.relative_to(repo_root).as_posix() if validator_path else None,
            "final_owner_report_path": owner_report_path.relative_to(repo_root).as_posix() if owner_report_path else None,
            "final_receipt_path": final_receipt_path.relative_to(repo_root).as_posix() if final_receipt_path.exists() else None,
            "status": normalized_status,
            "evidence_refs": unique(evidence_refs),
            "freshness": freshness_from_task_ids(sorted_tasks, report_task_id),
            "notes": unique(notes),
        }
        entries.append(entry)

        field_specs = [
            ("FINAL_RECEIPT", entry["final_receipt_path"]),
            ("VALIDATOR_REPORT", entry["validator_report_path"]),
            ("FINAL_OWNER_REPORT", entry["final_owner_report_path"]),
        ]
        for evidence_type, rel in field_specs:
            if rel is None:
                continue
            path_obj = repo_root / rel
            exists = path_obj.exists()
            evidence_entries.append(
                {
                    "phase_id": "GLOBAL_REPORT_INDEX",
                    "evidence_type": evidence_type,
                    "path": rel,
                    "existence_status": "EXISTS" if exists else "MISSING",
                    "proof_strength": proof_strength_for_status(normalized_status, exists),
                    "known_limitations": [
                        "Report index field snapshot.",
                    ],
                }
            )

        if normalized_status in {"WARN", "UNKNOWN", "MISSING", "PARTIAL"}:
            warnings.append(f"{report_task_id}_{normalized_status}")

    return entries, evidence_entries, unique(warnings)


def summarise_statuses(values: list[str]) -> dict[str, int]:
    summary = {status: 0 for status in ALLOWED_STATUSES}
    for value in values:
        if value in summary:
            summary[value] += 1
    return summary


def context_source_mix_snapshot() -> dict[str, Any]:
    return {
        "method": "FOUNDATION_ESTIMATE_V0_1",
        "percentages": {
            "taskpack": 44,
            "strategic_pdf": 16,
            "newgen_reports_registries_contracts": 26,
            "officio_doctrinarium_authority": 10,
            "mechanicus_tools_validators": 3,
            "owner_live_correction": 0,
            "servitor_inference": 1,
        },
        "note": "Taskpack-dominant foundation run; percentages are bounded estimates, not telemetry.",
    }


def build_action_layer_status(index_entries: list[dict[str, Any]]) -> dict[str, Any]:
    status_by_task = {entry["task_id"]: entry["status"] for entry in index_entries}
    evidence_refs: list[str] = []
    component_statuses: list[str] = []

    for suffix in [
        "TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1",
        "TASK-20260522-NEWGEN-SANCTUM-FILE-BACKED-ACTION-LAYER-VM3-V0_1",
        "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1",
    ]:
        if suffix not in status_by_task:
            continue
        component_statuses.append(status_by_task[suffix])

    for entry in index_entries:
        if "SANCTUM" not in entry["task_id"] and "ACTION-LAYER" not in entry["task_id"]:
            continue
        for ref in entry["evidence_refs"]:
            if ref.startswith("FILE:IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM"):
                evidence_refs.append(ref)

    if not component_statuses:
        overall = "UNKNOWN"
    elif any(status == "BLOCK" for status in component_statuses):
        overall = "BLOCK"
    elif any(status in {"WARN", "PARTIAL", "UNKNOWN"} for status in component_statuses):
        overall = "WARN"
    else:
        overall = "FOUNDATION_ONLY"

    return {
        "overall_status": overall,
        "components": {
            "truth_shell": status_by_task.get("TASK-20260522-NEWGEN-SANCTUM-TRUTH-SHELL-VM3-V0_1", "UNKNOWN"),
            "file_backed_action_layer": status_by_task.get(
                "TASK-20260522-NEWGEN-SANCTUM-FILE-BACKED-ACTION-LAYER-VM3-V0_1",
                "UNKNOWN",
            ),
            "action_layer_hardening": status_by_task.get(
                "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1",
                "UNKNOWN",
            ),
        },
        "evidence_refs": unique(evidence_refs),
        "known_limitations": [
            "Action layer is foundation-level and file-backed only.",
            "No production backend or autonomous action claims are made.",
        ],
    }


def build_sanctum_truth_shell(repo_root: Path) -> tuple[dict[str, Any], list[str]]:
    state_path = repo_root / SANCTUM_STATE_REL
    warnings: list[str] = []
    if not state_path.exists():
        return {
            "state_path": SANCTUM_STATE_REL,
            "exists": False,
            "status": "MISSING",
            "mode": "UNKNOWN",
            "communication_gate_status": "UNKNOWN",
        }, ["SANCTUM_STATE_MISSING"]

    state = load_json(state_path)
    if state is None:
        return {
            "state_path": SANCTUM_STATE_REL,
            "exists": True,
            "status": "WARN",
            "mode": "UNKNOWN",
            "communication_gate_status": "UNKNOWN",
        }, ["SANCTUM_STATE_INVALID_JSON"]

    mode = str(state.get("mode", "UNKNOWN"))
    communication_gate = state.get("communication_gate", {})
    if not isinstance(communication_gate, dict):
        communication_gate = {}
    comm_status = str(communication_gate.get("STATUS", "UNKNOWN"))
    status = "FOUNDATION_ONLY" if mode == "READ_ONLY_FOUNDATION" else "WARN"
    if status == "WARN":
        warnings.append("SANCTUM_STATE_MODE_NOT_FOUNDATION")

    return {
        "state_path": SANCTUM_STATE_REL,
        "exists": True,
        "status": status,
        "mode": mode,
        "communication_gate_status": comm_status,
    }, warnings


def build_payloads(repo_root: Path, task_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    phases, phase_task_map, phase_evidence, phase_warnings = collect_phase_coverage(repo_root)
    report_entries, report_evidence, report_warnings = collect_report_status_index(repo_root, task_id, phase_task_map)
    sanctum_summary, sanctum_warnings = build_sanctum_truth_shell(repo_root)
    action_layer = build_action_layer_status(report_entries)

    head = run_git(repo_root, "rev-parse", "HEAD")
    branch = run_git(repo_root, "branch", "--show-current")
    status_short = run_git(repo_root, "status", "--short")
    head_commit_utc = run_git(repo_root, "show", "-s", "--format=%cI", "HEAD")
    generated_at = utc_now()

    phase_statuses = [item["status"] for item in phases]
    report_statuses = [item["status"] for item in report_entries]
    known_warnings = unique(phase_warnings + report_warnings + sanctum_warnings)

    report_status_index = {
        "schema_id": "REPORT_STATUS_INDEX_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "allowed_status_values": ALLOWED_STATUSES,
        "entries": report_entries,
        "summary": {
            "total_entries": len(report_entries),
            "status_counts": summarise_statuses(report_statuses),
            "freshness_counts": {
                "CURRENT": sum(1 for item in report_entries if item["freshness"] == "CURRENT"),
                "STALE": sum(1 for item in report_entries if item["freshness"] == "STALE"),
                "UNKNOWN": sum(1 for item in report_entries if item["freshness"] == "UNKNOWN"),
            },
        },
    }

    evidence_entries = []
    for entry in phase_evidence + report_evidence:
        evidence_entries.append(
            {
                "phase_id": str(entry["phase_id"]),
                "evidence_type": str(entry["evidence_type"]),
                "path": str(entry["path"]),
                "existence_status": str(entry["existence_status"]),
                "proof_strength": str(entry["proof_strength"]),
                "known_limitations": [str(item) for item in entry.get("known_limitations", [])],
            }
        )

    evidence_source_map = {
        "schema_id": "EVIDENCE_SOURCE_MAP_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "entries": sorted(
            evidence_entries,
            key=lambda item: (
                item["phase_id"],
                item["evidence_type"],
                item["path"],
            ),
        ),
        "limitations": [
            "Foundation-only map; not a global evidence engine.",
            "Covers phase registry refs plus selected report index evidence fields.",
            "Freshness is date-derived from task ids, not from runtime telemetry.",
        ],
    }

    current_truth_root = {
        "schema_id": "CURRENT_TRUTH_ROOT_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "newgen_mode": "FOUNDATION_TRUTH_SPINE_V0_1",
        "repo_truth": {
            "repo_root": str(repo_root),
            "head": head,
            "branch": branch,
            "worktree_dirty": bool(status_short),
            "head_commit_utc": head_commit_utc,
        },
        "phase_coverage": {
            "phases": phases,
            "summary": {
                "total_phases": len(phases),
                "status_counts": summarise_statuses(phase_statuses),
            },
        },
        "sanctum_ng_truth_shell": sanctum_summary,
        "action_layer_status": action_layer,
        "known_warnings": known_warnings,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "context_source_mix_snapshot": context_source_mix_snapshot(),
        "report_status_index_path": REPORT_STATUS_INDEX_REL,
        "evidence_source_map_path": EVIDENCE_SOURCE_MAP_REL,
        "report_index_summary": report_status_index["summary"],
        "limitations": [
            "UNKNOWN zones are intentionally preserved as UNKNOWN/MISSING/PARTIAL/FOUNDATION_ONLY.",
            "No production autonomy, live backend, or full organ dialogue is claimed.",
            "Strategic PDF is used as compass only; broader tasks are deferred.",
        ],
    }

    build_report = {
        "schema_id": "CURRENT_TRUTH_BUILD_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "PASS_WITH_WARN" if known_warnings else "PASS",
        "outputs": {
            "current_truth_root": CURRENT_TRUTH_REL,
            "report_status_index": REPORT_STATUS_INDEX_REL,
            "evidence_source_map": EVIDENCE_SOURCE_MAP_REL,
        },
        "phase_status_counts": current_truth_root["phase_coverage"]["summary"]["status_counts"],
        "report_status_counts": report_status_index["summary"]["status_counts"],
        "known_warnings": known_warnings,
        "forbidden_claims_set": FORBIDDEN_CLAIMS,
    }

    return current_truth_root, report_status_index, evidence_source_map, build_report


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)

    current_truth_output = args.current_truth_output.resolve()
    report_index_output = args.report_index_output.resolve()
    evidence_map_output = args.evidence_map_output.resolve()
    build_report_output = args.build_report.resolve()

    current_truth_root, report_status_index, evidence_source_map, build_report = build_payloads(repo_root, task_id)

    write_json(current_truth_output, current_truth_root)
    write_json(report_index_output, report_status_index)
    write_json(evidence_map_output, evidence_source_map)
    write_json(build_report_output, build_report)

    print("build_status=PASS")
    print(f"current_truth_root={current_truth_output.relative_to(repo_root).as_posix()}")
    print(f"report_status_index={report_index_output.relative_to(repo_root).as_posix()}")
    print(f"evidence_source_map={evidence_map_output.relative_to(repo_root).as_posix()}")
    print(f"build_report={build_report_output.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
