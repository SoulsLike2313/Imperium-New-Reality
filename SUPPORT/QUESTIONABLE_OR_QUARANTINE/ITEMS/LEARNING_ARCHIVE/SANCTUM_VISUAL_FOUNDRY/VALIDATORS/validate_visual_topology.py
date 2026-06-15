from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R"

REQUIRED_ORGAN_NODE_UNITS = [
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.ADMINISTRATUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.ASTRONOMICON_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.OFFICIO_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.INQUISITION_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.DOCTRINARIUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.STRATEGIUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.SCHOLA_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.CUSTODES_NODE_LOCKED",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.THRONE_NODE_LOCKED",
]

REQUIRED_RIGHT_PANEL_UNITS = [
    "SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL",
    "SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.ASTRONOMICON_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.OFFICIO_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.INQUISITION_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.DOCTRINARIUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.STRATEGIUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.SCHOLA_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.CUSTODES_PANEL_LOCKED",
    "SANCTUM.RIGHT_CONTEXT_DOCK.THRONE_PANEL_LOCKED",
]

LOCKED_UNITS = {
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.CUSTODES_NODE_LOCKED",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.THRONE_NODE_LOCKED",
    "SANCTUM.RIGHT_CONTEXT_DOCK.CUSTODES_PANEL_LOCKED",
    "SANCTUM.RIGHT_CONTEXT_DOCK.THRONE_PANEL_LOCKED",
}

STUB_UNITS = {
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.ADMINISTRATUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.ASTRONOMICON_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.OFFICIO_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.INQUISITION_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.DOCTRINARIUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.STRATEGIUM_NODE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.SCHOLA_NODE",
    "SANCTUM.RIGHT_CONTEXT_DOCK.ADMINISTRATUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.ASTRONOMICON_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.OFFICIO_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.INQUISITION_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.DOCTRINARIUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.STRATEGIUM_PANEL_STUB",
    "SANCTUM.RIGHT_CONTEXT_DOCK.SCHOLA_PANEL_STUB",
}

PASSPORT_REQUIRED_FIELDS = [
    "visual_unit_id",
    "parent",
    "type",
    "visual_owner",
    "truth_owner",
    "data_source_owner",
    "organ_subject",
    "implementation_owner",
    "purpose",
    "backend_source",
    "backend_source_status",
    "allowed_states",
    "truth_rules",
    "visual_tokens",
    "texture",
    "glow",
    "motion",
    "perf_tier",
    "proof_requirements",
    "integration_status",
    "fake_green_risks",
]

REQUIRED_OWNERSHIP_FIELDS = [
    "visual_owner",
    "truth_owner",
    "data_source_owner",
    "organ_subject",
    "implementation_owner",
]

FORBIDDEN_ROOT_MARKERS = [
    "ORGANS/",
    "ORGANS\\",
    "SANCTUM/",
    "SANCTUM\\",
    "IMPERIUM_TEST_VERSION/",
    "IMPERIUM_TEST_VERSION\\",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str
    path: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_keyed_strings(node: Any, keys: set[str], out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys and isinstance(value, str):
                out.append(value)
            collect_keyed_strings(value, keys, out)
    elif isinstance(node, list):
        for item in node:
            collect_keyed_strings(item, keys, out)


def get_git_head(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def read_owner_report_head(owner_report_path: Path) -> str | None:
    if not owner_report_path.exists():
        return None
    content = owner_report_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"HEAD:\s*`?([0-9a-f]{40})`?", content, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1)


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    repo_root = base_dir.parent.parent
    units_dir = base_dir / "VISUAL_UNITS"
    registry_path = base_dir / "REGISTRY" / "visual_address_registry.json"
    truth_map_path = base_dir / "REGISTRY" / "backend_frontend_truth_map.json"
    motion_budget_path = base_dir / "MOTION" / "motion_budget_v0_1.json"
    report_path = base_dir / "REPORTS" / "validator_v0_2_report.json"
    owner_report_path = base_dir / "REPORTS" / "OWNER_REPORT_RU.md"

    task_dir = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "TASKS"
        / "VM3_ASSIGNED"
        / "TASK-20260520-NEWGEN-VISUAL-TOPOLOGY-HARDEN-10-ORGAN-COVERAGE-VM3-V0_2R"
    )
    officio_ack = task_dir / "OFFICIO_ROLE_ACK_VM3_SERVITOR.json"
    officio_warn = task_dir / "OFFICIO_ROLE_AUTHORITY_MISSING_WARN.json"

    checks: list[CheckResult] = []

    # Officio intake gate
    ack_exists = officio_ack.exists()
    warn_exists = officio_warn.exists()
    checks.append(
        CheckResult(
            name="officio_ack_or_warn_exists",
            ok=ack_exists or warn_exists,
            details="ack found" if ack_exists else "warn found" if warn_exists else "missing both officio ack and warn",
            path=str(task_dir),
        )
    )

    if ack_exists:
        try:
            ack_data = load_json(officio_ack)
            ok = (
                ack_data.get("authority_status") == "FOUND"
                and ack_data.get("taskpack_rules_are_task_specific_not_role_authority") is True
            )
            checks.append(
                CheckResult(
                    name="officio_ack_authority_fields",
                    ok=ok,
                    details="authority_status/taskpack authority fields validated" if ok else "invalid authority fields in officio ack",
                    path=str(officio_ack),
                )
            )
        except Exception as exc:  # noqa: BLE001
            checks.append(
                CheckResult(
                    name="officio_ack_parseable",
                    ok=False,
                    details=f"invalid json: {exc}",
                    path=str(officio_ack),
                )
            )

    # Load core artifacts
    loaded: dict[str, Any] = {}
    for label, path in [
        ("registry", registry_path),
        ("truth_map", truth_map_path),
        ("motion_budget", motion_budget_path),
    ]:
        if not path.exists():
            checks.append(CheckResult(name=f"{label}_exists", ok=False, details="missing file", path=str(path)))
            continue
        try:
            loaded[label] = load_json(path)
            checks.append(CheckResult(name=f"{label}_parseable", ok=True, details="ok", path=str(path)))
        except Exception as exc:  # noqa: BLE001
            checks.append(CheckResult(name=f"{label}_parseable", ok=False, details=f"invalid json: {exc}", path=str(path)))

    registry = loaded.get("registry", {})
    truth_map = loaded.get("truth_map", {})
    motion_budget = loaded.get("motion_budget", {})

    # Collect passports
    passport_files = {p.stem: p for p in units_dir.glob("*.json")}
    required_unit_ids = REQUIRED_ORGAN_NODE_UNITS + REQUIRED_RIGHT_PANEL_UNITS

    # Coverage checks
    missing_nodes = [unit for unit in REQUIRED_ORGAN_NODE_UNITS if unit not in passport_files]
    checks.append(
        CheckResult(
            name="all_10_organ_nodes_exist",
            ok=not missing_nodes,
            details="ok" if not missing_nodes else f"missing nodes: {missing_nodes}",
            path=str(units_dir),
        )
    )

    missing_panels = [unit for unit in REQUIRED_RIGHT_PANEL_UNITS if unit not in passport_files]
    checks.append(
        CheckResult(
            name="all_10_right_panels_exist",
            ok=not missing_panels,
            details="ok" if not missing_panels else f"missing panels: {missing_panels}",
            path=str(units_dir),
        )
    )

    passports: dict[str, Any] = {}
    for unit_id, file_path in passport_files.items():
        try:
            passports[unit_id] = load_json(file_path)
        except Exception as exc:  # noqa: BLE001
            checks.append(CheckResult(name=f"passport_parse_{unit_id}", ok=False, details=f"invalid json: {exc}", path=str(file_path)))

    # Required fields + ownership checks
    for unit_id in required_unit_ids:
        passport = passports.get(unit_id)
        if not isinstance(passport, dict):
            continue

        missing_fields = [field for field in PASSPORT_REQUIRED_FIELDS if field not in passport]
        checks.append(
            CheckResult(
                name=f"passport_required_fields_{unit_id}",
                ok=not missing_fields,
                details="ok" if not missing_fields else f"missing fields: {missing_fields}",
                path=str(passport_files[unit_id]),
            )
        )

        missing_owner_fields = [
            field for field in REQUIRED_OWNERSHIP_FIELDS if not isinstance(passport.get(field), str) or not passport.get(field).strip()
        ]
        checks.append(
            CheckResult(
                name=f"passport_ownership_fields_{unit_id}",
                ok=not missing_owner_fields,
                details="ok" if not missing_owner_fields else f"missing/empty ownership fields: {missing_owner_fields}",
                path=str(passport_files[unit_id]),
            )
        )

    # Locked/stub semantics
    for locked_unit in sorted(LOCKED_UNITS):
        status = passports.get(locked_unit, {}).get("integration_status")
        checks.append(
            CheckResult(
                name=f"locked_unit_not_real_{locked_unit}",
                ok=status not in {"real", "candidate"},
                details=f"integration_status={status}",
                path=str(passport_files.get(locked_unit, "")),
            )
        )

    for stub_unit in sorted(STUB_UNITS):
        status = passports.get(stub_unit, {}).get("integration_status")
        checks.append(
            CheckResult(
                name=f"stub_unit_is_stub_{stub_unit}",
                ok=status == "stub",
                details=f"integration_status={status}",
                path=str(passport_files.get(stub_unit, "")),
            )
        )

    # Backend source rule for real/candidate
    for unit_id, passport in passports.items():
        if not isinstance(passport, dict):
            continue
        status = passport.get("integration_status")
        if status not in {"real", "candidate"}:
            continue

        backend_source = passport.get("backend_source")
        unknown_reason = passport.get("backend_source_unknown_reason")

        unknown_backend = False
        if isinstance(backend_source, str):
            unknown_backend = backend_source.strip() in {"", "UNKNOWN", "OWNER_GATE_REQUIRED"}
        elif backend_source is None:
            unknown_backend = True

        ok = True
        if unknown_backend and (not isinstance(unknown_reason, str) or not unknown_reason.strip()):
            ok = False

        checks.append(
            CheckResult(
                name=f"real_candidate_backend_source_rule_{unit_id}",
                ok=ok,
                details=(
                    "backend source present"
                    if ok and not unknown_backend
                    else "unknown backend has explicit reason"
                    if ok
                    else "real/candidate unit has unknown backend without reason"
                ),
                path=str(passport_files.get(unit_id, "")),
            )
        )

    # Registry references existing passport files
    registry_units = registry.get("units", []) if isinstance(registry, dict) else []
    missing_registry_passports: list[str] = []
    for item in registry_units:
        if not isinstance(item, dict):
            continue
        unit_id = item.get("visual_unit_id")
        path_raw = item.get("passport_path")
        if not isinstance(unit_id, str) or not isinstance(path_raw, str):
            continue
        passport_path = repo_root / path_raw
        if not passport_path.exists() or unit_id not in passports:
            missing_registry_passports.append(unit_id)
    checks.append(
        CheckResult(
            name="registry_references_existing_passports",
            ok=not missing_registry_passports,
            details="ok" if not missing_registry_passports else f"missing refs: {missing_registry_passports}",
            path=str(registry_path),
        )
    )

    # Truth map references existing passports
    truth_entries = truth_map.get("entries", []) if isinstance(truth_map, dict) else []
    missing_truth_refs: list[str] = []
    for entry in truth_entries:
        if not isinstance(entry, dict):
            continue
        unit_id = entry.get("visual_unit_id")
        if isinstance(unit_id, str) and unit_id not in passports:
            missing_truth_refs.append(unit_id)
    checks.append(
        CheckResult(
            name="truth_map_references_existing_units",
            ok=not missing_truth_refs,
            details="ok" if not missing_truth_refs else f"missing refs: {missing_truth_refs}",
            path=str(truth_map_path),
        )
    )

    # Performance tier checks
    perf_tiers = set(motion_budget.get("performance_tiers", [])) if isinstance(motion_budget, dict) else set()
    bad_perf_tiers = []
    for unit_id, passport in passports.items():
        tier = passport.get("perf_tier") if isinstance(passport, dict) else None
        if not isinstance(tier, str) or tier not in perf_tiers:
            bad_perf_tiers.append(f"{unit_id}:{tier}")
    checks.append(
        CheckResult(
            name="required_performance_tiers_exist",
            ok=not bad_perf_tiers,
            details="ok" if not bad_perf_tiers else f"invalid perf_tier refs: {bad_perf_tiers}",
            path=str(motion_budget_path),
        )
    )

    # Forbidden write-target roots
    write_target_values: list[str] = []
    write_target_keys = {"write_target", "write_path", "output_path", "target_root", "destination"}
    for document in [registry, truth_map, *passports.values()]:
        collect_keyed_strings(document, write_target_keys, write_target_values)
    forbidden_hits = [value for value in write_target_values if any(marker in value for marker in FORBIDDEN_ROOT_MARKERS)]
    checks.append(
        CheckResult(
            name="forbidden_write_targets_absent",
            ok=not forbidden_hits,
            details="none" if not forbidden_hits else f"hits={forbidden_hits}",
            path=str(base_dir),
        )
    )

    # Owner report HEAD staleness check
    current_head = get_git_head(repo_root)
    owner_head = read_owner_report_head(owner_report_path)
    head_check_ok = owner_head is None or owner_head == current_head
    checks.append(
        CheckResult(
            name="owner_report_head_not_stale_if_present",
            ok=head_check_ok,
            details=(
                "no HEAD hash present in owner report (check skipped)"
                if owner_head is None
                else f"owner_head={owner_head}, current_head={current_head}"
            ),
            path=str(owner_report_path),
        )
    )

    passed = sum(1 for check in checks if check.ok)
    failed = len(checks) - passed
    verdict = "PASS" if failed == 0 else "FAIL"

    report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "validator": "validate_visual_topology.py",
        "base_dir": str(base_dir),
        "summary": {
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
        },
        "checks": [
            {
                "name": check.name,
                "ok": check.ok,
                "details": check.details,
                "path": check.path,
            }
            for check in checks
        ],
        "verdict": verdict,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"validation_report: {report_path}")
    print(f"verdict: {verdict} ({passed}/{len(checks)} passed)")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
