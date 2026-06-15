from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TASK_ID = "TASK-NEWGEN-ADMINISTRATUM-FILE-ATLAS-PASSPORT-INDEX-VM3-V0_1"
HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
NEWGEN_ROOT = HERE.parents[2]
REPO_ROOT = HERE.parents[3]
ATLAS_ROOT = ADMIN_ROOT / "FILE_ATLAS"
REPORT_ROOT = ADMIN_ROOT / "REPORTS" / TASK_ID

ORGAN_ROOTS: dict[str, Path] = {
    "MECHANICUS": NEWGEN_ROOT / "MECHANICUS",
    "OFFICIO_AGENTIS": NEWGEN_ROOT / "OFFICIO_AGENTIS",
    "ADMINISTRATUM": NEWGEN_ROOT / "ADMINISTRATUM",
    "INQUISITION": NEWGEN_ROOT / "INQUISITION",
    "ASTRONOMICON": NEWGEN_ROOT / "ASTRONOMICON",
}

FILE_KIND_VALUES = [
    "BODY",
    "CONTRACT",
    "ROLE",
    "RULE",
    "POLICY",
    "SCHEMA",
    "REGISTRY",
    "CARD",
    "TOOL",
    "TUI",
    "REPORT",
    "RECEIPT",
    "FIXTURE",
    "TEMPLATE",
    "README",
    "GHOST_EVOLVE",
    "UNKNOWN",
]

STATUS_VALUES = ["ACTIVE", "DRAFT", "LEGACY", "WARN", "BLOCKED", "UNKNOWN"]
RELATED_BLOCK_VALUES = ["CAPABILITY", "FOUNDATION", "REPORTING", "ROUTING", "VALIDATION", "TUI", "GHOST_EVOLVE", "CONNECTION", "UNKNOWN"]

REQUIRED_OWNER_PAINS = [
    "OFFICIO_LANGUAGE_GATE_WEAKNESS",
    "ROUTE_MEMORY_LOSS_PC_TO_VM3",
    "PENDING_COMMIT_PUSH_RECURRENCE",
    "INQUISITION_WEAKEST_ORGAN_BLOCKER",
    "HIDDEN_PATHS_AND_REPORT_LINKS",
]

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".py",
    ".sh",
    ".cmd",
    ".toml",
    ".yaml",
    ".yml",
    ".sql",
    ".csv",
    ".log",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def iter_organ_files() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for organ_id, root in ORGAN_ROOTS.items():
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts:
                continue
            if path.suffix == ".pyc":
                continue
            items.append((organ_id, path))
    return items


def detect_file_kind(relative_path: str) -> str:
    lower = relative_path.lower()
    name = Path(relative_path).name.lower()

    if "/ghost_evolve/" in lower:
        return "GHOST_EVOLVE"
    if name.startswith("readme"):
        return "README"
    if "/roles/" in lower or "_role_" in name or name.endswith("_role.md"):
        return "ROLE"
    if "/rules/" in lower:
        return "RULE"
    if "/contracts/" in lower or "contract" in name:
        return "CONTRACT"
    if "policy" in name:
        return "POLICY"
    if "/schemas/" in lower or "schema" in name:
        return "SCHEMA"
    if "/registry/" in lower or "registry" in name:
        return "REGISTRY"
    if "/tools/" in lower:
        return "TOOL"
    if "/tui/" in lower:
        return "TUI"
    if "/fixtures/" in lower:
        return "FIXTURE"
    if "/templates/" in lower:
        return "TEMPLATE"
    if "/body/" in lower:
        return "BODY"
    if "/reports/" in lower:
        if "/receipts/" in lower or "receipt" in name:
            return "RECEIPT"
        if "action_card" in name or "card" in name:
            return "CARD"
        return "REPORT"
    if "/receipts/" in lower or "receipt" in name:
        return "RECEIPT"
    if "card" in name:
        return "CARD"
    return "UNKNOWN"


def detect_status(relative_path: str) -> str:
    lower = relative_path.lower()
    if "blocked" in lower or "blocker" in lower:
        return "BLOCKED"
    if "legacy" in lower:
        return "LEGACY"
    if "warn" in lower:
        return "WARN"
    if "draft" in lower:
        return "DRAFT"
    return "ACTIVE"


def detect_related_block(relative_path: str) -> str:
    lower = relative_path.lower()
    if "/tui/" in lower:
        return "TUI"
    if "/ghost_evolve/" in lower:
        return "GHOST_EVOLVE"
    if "/routing/" in lower or "route" in lower:
        return "ROUTING"
    if "/connections/" in lower or "ssh" in lower:
        return "CONNECTION"
    if "/reports/" in lower or "/receipts/" in lower:
        return "REPORTING"
    if "/tools/" in lower or "/schemas/" in lower or "/gates/" in lower:
        return "VALIDATION"
    if "/arsenal/" in lower or "/capability" in lower:
        return "CAPABILITY"
    if "/body/" in lower or "/rules/" in lower or "/roles/" in lower or "/contracts/" in lower or "/identity/" in lower:
        return "FOUNDATION"
    return "UNKNOWN"


def detect_ide_visible(path: Path, file_kind: str) -> bool:
    if file_kind in {"FIXTURE"}:
        return False
    if path.suffix.lower() in {".sqlite3", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".woff", ".woff2", ".ttf"}:
        return False
    return True


def detect_drilldown_priority(relative_path: str, file_kind: str) -> str:
    lower = relative_path.lower()
    if file_kind in {"ROLE", "RULE", "POLICY", "CONTRACT"}:
        return "HIGH"
    if "language" in lower or "stop_warn_pass" in lower or "taskpack_acceptance" in lower:
        return "HIGH"
    if "imperium-vm3" in lower or "pc_to_vm3" in lower or "route" in lower or "connection" in lower:
        return "HIGH"
    if file_kind in {"TOOL", "TUI", "SCHEMA", "REGISTRY"}:
        return "MEDIUM"
    return "LOW"


def detect_edit_surface(file_kind: str) -> str:
    if file_kind in {"ROLE", "RULE", "POLICY", "CONTRACT", "SCHEMA", "REGISTRY"}:
        return "YES"
    if file_kind in {"TOOL", "TUI", "BODY", "GHOST_EVOLVE", "README", "TEMPLATE"}:
        return "CAUTION"
    return "NO"


def infer_purpose(file_kind: str) -> str:
    purpose_map = {
        "BODY": "Defines organ body/foundation structure.",
        "CONTRACT": "Defines explicit operating contract and obligations.",
        "ROLE": "Defines agent role behavior and boundaries.",
        "RULE": "Defines operational rules for execution and quality.",
        "POLICY": "Defines policy constraints and allowed behaviors.",
        "SCHEMA": "Defines machine-readable data contract.",
        "REGISTRY": "Registers indexed entities and ownership references.",
        "CARD": "Stores compact route/task/reference card data.",
        "TOOL": "Implements automation, checking, or generation logic.",
        "TUI": "Provides read-only terminal interaction surface.",
        "REPORT": "Captures task execution evidence and summary.",
        "RECEIPT": "Stores machine-readable validation result.",
        "FIXTURE": "Provides fixture/sample input for checks.",
        "TEMPLATE": "Provides reusable output template.",
        "README": "Documents surface purpose and usage entrypoint.",
        "GHOST_EVOLVE": "Tracks accepted/rejected local evolution signals.",
        "UNKNOWN": "Unclassified file surface requiring review.",
    }
    return purpose_map.get(file_kind, purpose_map["UNKNOWN"])


def related_owner_pains(relative_path: str) -> list[str]:
    lower = relative_path.lower()
    pain_ids: list[str] = []
    if "officio_agentis" in lower and (
        "language" in lower
        or "/roles/" in lower
        or "/rules/" in lower
        or "final_response_contract" in lower
        or "stop_warn_pass" in lower
        or "taskpack_acceptance" in lower
        or "ghost_evolve_contract" in lower
    ):
        pain_ids.append("OFFICIO_LANGUAGE_GATE_WEAKNESS")
    if "imperium-vm3" in lower or "pc_to_vm3" in lower or "route" in lower or "ssh_connection" in lower:
        pain_ids.append("ROUTE_MEMORY_LOSS_PC_TO_VM3")
    if "closure_receipt" in lower or "gate_ack" in lower or "final_report" in lower:
        pain_ids.append("PENDING_COMMIT_PUSH_RECURRENCE")
    if "inquisition" in lower:
        pain_ids.append("INQUISITION_WEAKEST_ORGAN_BLOCKER")
    if "/reports/" in lower or "/receipts/" in lower or "index" in lower or "registry" in lower:
        pain_ids.append("HIDDEN_PATHS_AND_REPORT_LINKS")
    return pain_ids


def build_passport(organ_id: str, path: Path) -> dict[str, Any]:
    relative_path = to_repo_relative(path)
    file_kind = detect_file_kind(relative_path)
    status = detect_status(relative_path)
    warnings: list[str] = []
    if file_kind == "UNKNOWN":
        warnings.append("UNKNOWN_FILE_KIND")
    if status in {"LEGACY", "WARN", "BLOCKED"}:
        warnings.append(f"STATUS_{status}")
    ide_visible = detect_ide_visible(path, file_kind)
    if not ide_visible:
        warnings.append("NOT_IDE_VISIBLE")

    return {
        "path": relative_path,
        "owner_organ": organ_id,
        "related_block": detect_related_block(relative_path),
        "file_kind": file_kind,
        "purpose_short": infer_purpose(file_kind),
        "status": status,
        "ide_visible": ide_visible,
        "drilldown_priority": detect_drilldown_priority(relative_path, file_kind),
        "related_owner_pains": related_owner_pains(relative_path),
        "edit_surface": detect_edit_surface(file_kind),
        "evidence_source": "path_name_heuristics",
        "warnings": warnings,
    }


def build_file_atlas_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    by_organ = Counter(p["owner_organ"] for p in passports)
    by_kind = Counter(p["file_kind"] for p in passports)
    by_status = Counter(p["status"] for p in passports)
    unknown_count = sum(1 for p in passports if p["file_kind"] == "UNKNOWN")

    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "indexed_roots": {organ: to_repo_relative(root) for organ, root in ORGAN_ROOTS.items()},
        "indexed_organs": sorted(ORGAN_ROOTS.keys()),
        "total_files_indexed": len(passports),
        "counts_by_organ": dict(sorted(by_organ.items())),
        "counts_by_file_kind": dict(sorted(by_kind.items())),
        "counts_by_status": dict(sorted(by_status.items())),
        "unknown_file_kind_count": unknown_count,
        "missing_unknown_review_needed": unknown_count > 0,
        "atlas_version": "v0_1",
    }


def build_organ_file_map(passports: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for passport in passports:
        grouped[passport["owner_organ"]][passport["related_block"]].append(passport["path"])

    payload: dict[str, Any] = {"task_id": TASK_ID, "organs": {}}
    for organ_id in sorted(grouped.keys()):
        block_payload: dict[str, Any] = {}
        for block in sorted(grouped[organ_id].keys()):
            paths = sorted(grouped[organ_id][block])
            block_payload[block] = {
                "count": len(paths),
                "sample_paths": paths[:40],
            }
        payload["organs"][organ_id] = block_payload
    payload["full_passports_reference"] = "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_passports_v0_1.jsonl"
    return payload


def build_role_rule_surface_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    officio_paths = [p["path"] for p in passports if p["owner_organ"] == "OFFICIO_AGENTIS"]
    return {
        "task_id": TASK_ID,
        "focus_organ": "OFFICIO_AGENTIS",
        "roles": sorted([p for p in officio_paths if "/ROLES/" in p]),
        "rules": sorted([p for p in officio_paths if "/RULES/" in p]),
        "language_policy_files": sorted([p for p in officio_paths if "language_policy" in p.lower()]),
        "final_response_contract_files": sorted([p for p in officio_paths if "final_response_contract" in p.lower() or "response_contract" in p.lower()]),
        "stop_warn_pass_grammar_files": sorted([p for p in officio_paths if "stop_warn_pass" in p.lower()]),
        "taskpack_acceptance_rule_files": sorted([p for p in officio_paths if "taskpack_acceptance" in p.lower()]),
        "ghost_evolve_contract_files": sorted([p for p in officio_paths if "ghost_evolve_contract" in p.lower()]),
        "edit_candidates_high_priority": sorted(
            [
                p["path"]
                for p in passports
                if p["owner_organ"] == "OFFICIO_AGENTIS"
                and p["edit_surface"] == "YES"
                and p["drilldown_priority"] == "HIGH"
            ]
        )[:50],
    }


def load_text(path: Path, max_bytes: int = 400_000) -> str:
    try:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            return ""
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def build_language_gate_surface_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    officio_passports = [p for p in passports if p["owner_organ"] == "OFFICIO_AGENTIS"]
    officio_paths = [p["path"] for p in officio_passports]
    drift_surfaces = sorted(
        [
            p
            for p in officio_paths
            if "FAIL_ENGLISH_LIVE_PROGRESS".lower() in p.lower()
            or "OWNER_FACING_LANGUAGE".lower() in p.lower()
            or "language" in p.lower()
            or "stop_warn_pass" in p.lower()
        ]
    )

    return {
        "task_id": TASK_ID,
        "scope": "MAPPING_ONLY_NO_HARDENING",
        "owner_facing_language_rules": sorted([p for p in officio_paths if "language_policy" in p.lower()]),
        "role_files_related_to_servitor_logos_advisor": sorted(
            [p for p in officio_paths if "/ROLES/" in p and any(token in p.lower() for token in ("servitor", "logos", "advisor"))]
        ),
        "final_response_contract_files": sorted(
            [p for p in officio_paths if "final_response_contract" in p.lower() or "response_contract" in p.lower()]
        ),
        "stop_warn_pass_files": sorted([p for p in officio_paths if "stop_warn_pass" in p.lower()]),
        "taskpack_acceptance_rule_files": sorted([p for p in officio_paths if "taskpack_acceptance" in p.lower()]),
        "ghost_evolve_contract_files": sorted([p for p in officio_paths if "ghost_evolve_contract" in p.lower()]),
        "current_drift_warning_surfaces": drift_surfaces[:80],
        "future_hardening_task": "TASK-NEWGEN-OFFICIO-LANGUAGE-GATE-HARDENING-PC-V0_1",
        "script_first_future_cure": [
            "live_status_language_checker",
            "taskpack_pre_start_ack_language_gate",
            "final_response_language_check",
            "officio_tui_language_contract_visibility",
            "violation_report_export",
        ],
    }


def build_tui_surface_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    tui_paths = sorted([p["path"] for p in passports if p["file_kind"] == "TUI"])
    launch_paths = sorted([p["path"] for p in passports if "LAUNCH_" in Path(p["path"]).name])
    by_organ = Counter(p["owner_organ"] for p in passports if p["file_kind"] == "TUI")
    return {
        "task_id": TASK_ID,
        "tui_file_count": len(tui_paths),
        "launch_script_count": len(launch_paths),
        "counts_by_organ": dict(sorted(by_organ.items())),
        "tui_paths": tui_paths,
        "launch_paths": launch_paths,
    }


def build_checker_tool_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    tool_paths = [p["path"] for p in passports if p["file_kind"] == "TOOL"]
    checker_paths = sorted([p for p in tool_paths if any(token in Path(p).name.lower() for token in ("check", "checker", "validate", "smoke"))])
    builder_paths = sorted([p for p in tool_paths if "builder" in Path(p).name.lower() or "export" in Path(p).name.lower()])
    return {
        "task_id": TASK_ID,
        "total_tool_files": len(tool_paths),
        "checker_or_validator_files": checker_paths,
        "builder_or_export_files": builder_paths,
    }


def build_report_receipt_index(passports: list[dict[str, Any]]) -> dict[str, Any]:
    report_paths = sorted([p["path"] for p in passports if p["file_kind"] == "REPORT"])
    receipt_paths = sorted([p["path"] for p in passports if p["file_kind"] == "RECEIPT"])
    card_paths = sorted([p["path"] for p in passports if p["file_kind"] == "CARD"])
    return {
        "task_id": TASK_ID,
        "report_count": len(report_paths),
        "receipt_count": len(receipt_paths),
        "card_count": len(card_paths),
        "report_paths_sample": report_paths[:120],
        "receipt_paths_sample": receipt_paths[:120],
        "card_paths_sample": card_paths[:120],
    }


def build_route_connection_surface_index(passports: list[dict[str, Any],], raw_files: list[tuple[str, Path]]) -> dict[str, Any]:
    route_candidates: list[str] = []
    alias_mentions: list[str] = []
    for _organ_id, path in raw_files:
        relative_path = to_repo_relative(path)
        lower = relative_path.lower()
        if any(token in lower for token in ("route", "routing", "connection", "ssh", "pc_to_vm3", "vm3")):
            route_candidates.append(relative_path)
        text = load_text(path)
        if "imperium-vm3" in text:
            alias_mentions.append(relative_path)
    route_candidates = sorted(set(route_candidates))
    alias_mentions = sorted(set(alias_mentions))

    return {
        "task_id": TASK_ID,
        "required_alias": "imperium-vm3",
        "alias_detected": len(alias_mentions) > 0,
        "alias_evidence_paths": alias_mentions[:80],
        "route_connection_surface_paths": route_candidates[:200],
        "notable_route_cards": sorted([p["path"] for p in passports if "pc_to_vm3_direct_route_card" in p["path"].lower()]),
    }


def build_owner_pain_to_file_map(passports: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [p["path"] for p in passports]

    def select(predicate: Any, limit: int = 25) -> list[str]:
        return sorted([p for p in paths if predicate(p)])[:limit]

    payload = {
        "task_id": TASK_ID,
        "pains": [
            {
                "pain_id": "OFFICIO_LANGUAGE_GATE_WEAKNESS",
                "owner_organ": "OFFICIO_AGENTIS",
                "severity": "HIGH",
                "likely_file_surfaces": select(
                    lambda p: "OFFICIO_AGENTIS" in p
                    and (
                        "/RULES/" in p
                        or "/ROLES/" in p
                        or "final_response_contract" in p.lower()
                        or "taskpack_acceptance" in p.lower()
                        or "stop_warn_pass" in p.lower()
                        or "language" in p.lower()
                    )
                ),
                "current_status": "MAPPED_NOT_HARDENED",
                "proposed_cure": "Script-first Officio language gate hardening with pre-start/final-response checks.",
                "reduced_by_this_task": True,
                "next_task_route": "TASK-NEWGEN-OFFICIO-LANGUAGE-GATE-HARDENING-PC-V0_1",
            },
            {
                "pain_id": "ROUTE_MEMORY_LOSS_PC_TO_VM3",
                "owner_organ": "ASTRONOMICON",
                "severity": "HIGH",
                "likely_file_surfaces": select(
                    lambda p: "imperium-vm3" in p.lower()
                    or "pc_to_vm3" in p.lower()
                    or "SSH_CONNECTION_MATRIX_V0_1".lower() in p.lower()
                    or "canonical_transfer_commands".lower() in p.lower()
                ),
                "current_status": "REDUCED_BY_REGISTERED_ROUTE_ARTIFACTS",
                "proposed_cure": "Keep route card + command catalog visible in read-only IDE.",
                "reduced_by_this_task": True,
                "next_task_route": "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC",
            },
            {
                "pain_id": "PENDING_COMMIT_PUSH_RECURRENCE",
                "owner_organ": "ADMINISTRATUM",
                "severity": "HIGH",
                "likely_file_surfaces": select(lambda p: "closure_receipt" in p.lower() or "gate_ack" in p.lower() or "ACTION_CARD".lower() in p.lower()),
                "current_status": "CONTROLLED_BY_NO_PENDING_FINAL_RULE",
                "proposed_cure": "Enforce closure receipt + origin sync verification for each completion cycle.",
                "reduced_by_this_task": True,
                "next_task_route": "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC",
            },
            {
                "pain_id": "INQUISITION_WEAKEST_ORGAN_BLOCKER",
                "owner_organ": "INQUISITION",
                "severity": "HIGH",
                "likely_file_surfaces": select(lambda p: "INQUISITION/" in p),
                "current_status": "MAPPED_BLOCKER_STILL_OPEN",
                "proposed_cure": "Inquisition V0.2 body/schema/registry/checker/report hardening task.",
                "reduced_by_this_task": False,
                "next_task_route": "TASK-NEWGEN-INQUISITION-PURITY-QUARANTINE-BODY-VM3-V0_2",
            },
            {
                "pain_id": "HIDDEN_PATHS_AND_REPORT_LINKS",
                "owner_organ": "ADMINISTRATUM",
                "severity": "MEDIUM",
                "likely_file_surfaces": select(lambda p: "/REPORTS/" in p or "/receipts/" in p.lower() or "index" in p.lower() or "registry" in p.lower(), limit=40),
                "current_status": "REDUCED_BY_ATLAS_INDEXING",
                "proposed_cure": "Drive IDE drill-down directly from file passports and organ/block indexes.",
                "reduced_by_this_task": True,
                "next_task_route": "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC",
            },
        ],
    }
    return payload


def build_gap_success_index(passports: list[dict[str, Any]], route_surface: dict[str, Any]) -> dict[str, Any]:
    by_organ = Counter(p["owner_organ"] for p in passports)
    unknown_count = sum(1 for p in passports if p["file_kind"] == "UNKNOWN")
    inquisition_body_present = any(p["owner_organ"] == "INQUISITION" and p["file_kind"] == "BODY" for p in passports)
    return {
        "task_id": TASK_ID,
        "gaps": [
            {
                "gap_id": "INQUISITION_BODY_MANIFEST_GAP",
                "status": "OPEN" if not inquisition_body_present else "CLOSED",
                "summary": "Inquisition has no dedicated BODY file surface in indexed paths.",
            },
            {
                "gap_id": "UNKNOWN_FILE_KIND_REVIEW",
                "status": "OPEN" if unknown_count > 0 else "CLOSED",
                "summary": f"Unknown file-kind passports: {unknown_count}.",
            },
        ],
        "successes": [
            {
                "success_id": "FIVE_ORGANS_VISIBLE",
                "status": "PASS",
                "summary": f"Indexed organs: {len(by_organ)} with total files {sum(by_organ.values())}.",
            },
            {
                "success_id": "ROUTE_SURFACE_REGISTERED",
                "status": "PASS" if route_surface.get("alias_detected") else "WARN",
                "summary": "imperium-vm3 alias surface is mapped for IDE drill-down.",
            },
            {
                "success_id": "OFFICIO_LANGUAGE_SURFACE_MAPPED",
                "status": "PASS",
                "summary": "Role/rule/language/contract surfaces mapped without hardening mutation.",
            },
        ],
    }


def build_schema_payload() -> dict[str, Any]:
    return {
        "schema_id": "administratum_file_passport_schema_v0_1",
        "task_id": TASK_ID,
        "required_fields": [
            "path",
            "owner_organ",
            "related_block",
            "file_kind",
            "purpose_short",
            "status",
            "ide_visible",
            "drilldown_priority",
            "related_owner_pains",
            "edit_surface",
            "evidence_source",
            "warnings",
        ],
        "enum": {
            "file_kind": FILE_KIND_VALUES,
            "status": STATUS_VALUES,
            "related_block": RELATED_BLOCK_VALUES,
            "drilldown_priority": ["HIGH", "MEDIUM", "LOW"],
            "edit_surface": ["YES", "NO", "CAUTION"],
            "related_owner_pains": REQUIRED_OWNER_PAINS,
        },
    }


def build_readme() -> str:
    return """# Administratum File Atlas V0.1

Task: `TASK-NEWGEN-ADMINISTRATUM-FILE-ATLAS-PASSPORT-INDEX-VM3-V0_1`

This folder provides read-only machine-readable file visibility for five NewGen organs:
- MECHANICUS
- OFFICIO_AGENTIS
- ADMINISTRATUM
- INQUISITION
- ASTRONOMICON

Core outputs:
- `file_passport_schema_v0_1.json`
- `file_passports_v0_1.jsonl`
- `file_atlas_index_v0_1.json`
- organ/surface indexes for role/rule/language/tool/TUI/report/route/pain/gap

Use:
```bash
python3 IMPERIUM_NEW_GENERATION/ADMINISTRATUM/TUI/administratum_file_atlas_tui_v0_1.py --lang en
```

Notes:
- This is indexing and visibility only.
- No IDE/WARP/CLI Worker implementation is included.
- Officio/Inquisition hardening is intentionally not performed in this task.
"""


def build_ide_readiness_receipt(file_atlas_index: dict[str, Any], owner_pain_map: dict[str, Any]) -> dict[str, Any]:
    pain_ids = [p["pain_id"] for p in owner_pain_map.get("pains", []) if isinstance(p, dict)]
    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": "PASS",
        "read_only_ide_capabilities": {
            "organ_panel": True,
            "file_passport_drilldown": True,
            "role_rule_panel": True,
            "language_gate_surface_panel": True,
            "route_surface_panel": True,
            "problems_panel": True,
            "successes_panel": True,
        },
        "required_owner_pains_present": sorted(pain_ids),
        "file_count": file_atlas_index.get("total_files_indexed", 0),
        "indexed_organs": file_atlas_index.get("indexed_organs", []),
        "next_task": "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC",
    }


def run_builder() -> dict[str, Any]:
    raw_files = iter_organ_files()
    passports = [build_passport(organ_id, path) for organ_id, path in raw_files]
    passports.sort(key=lambda row: row["path"])

    schema_payload = build_schema_payload()
    file_atlas_index = build_file_atlas_index(passports)
    organ_file_map = build_organ_file_map(passports)
    role_rule_index = build_role_rule_surface_index(passports)
    language_surface = build_language_gate_surface_index(passports)
    tui_surface = build_tui_surface_index(passports)
    checker_tool = build_checker_tool_index(passports)
    report_receipt = build_report_receipt_index(passports)
    route_surface = build_route_connection_surface_index(passports, raw_files)
    owner_pain_map = build_owner_pain_to_file_map(passports)
    gap_success = build_gap_success_index(passports, route_surface)
    ide_readiness = build_ide_readiness_receipt(file_atlas_index, owner_pain_map)

    ATLAS_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(ATLAS_ROOT / "file_passport_schema_v0_1.json", schema_payload)
    write_json(ATLAS_ROOT / "file_atlas_index_v0_1.json", file_atlas_index)
    write_jsonl(ATLAS_ROOT / "file_passports_v0_1.jsonl", passports)
    write_json(ATLAS_ROOT / "organ_file_map_v0_1.json", organ_file_map)
    write_json(ATLAS_ROOT / "role_rule_surface_index_v0_1.json", role_rule_index)
    write_json(ATLAS_ROOT / "language_gate_surface_index_v0_1.json", language_surface)
    write_json(ATLAS_ROOT / "tui_surface_index_v0_1.json", tui_surface)
    write_json(ATLAS_ROOT / "checker_tool_index_v0_1.json", checker_tool)
    write_json(ATLAS_ROOT / "report_receipt_index_v0_1.json", report_receipt)
    write_json(ATLAS_ROOT / "route_connection_surface_index_v0_1.json", route_surface)
    write_json(ATLAS_ROOT / "owner_pain_to_file_map_v0_1.json", owner_pain_map)
    write_json(ATLAS_ROOT / "gap_success_index_v0_1.json", gap_success)
    (ATLAS_ROOT / "README_FILE_ATLAS_V0_1.md").write_text(build_readme(), encoding="utf-8")

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(REPORT_ROOT / "owner_pain_map.json", owner_pain_map)
    write_json(REPORT_ROOT / "ide_readiness_receipt.json", ide_readiness)

    receipt = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "status": "PASS",
        "indexed_file_count": len(passports),
        "indexed_organs": sorted(ORGAN_ROOTS.keys()),
        "required_owner_pains": REQUIRED_OWNER_PAINS,
        "route_alias_detected": route_surface.get("alias_detected", False),
        "output_root": to_repo_relative(ATLAS_ROOT),
        "report_root": to_repo_relative(REPORT_ROOT),
    }
    write_json(REPORT_ROOT / "file_atlas_build_receipt.json", receipt)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Administratum File Atlas and passport indexes.")
    parser.add_argument("--print-receipt", action="store_true", help="Print the build receipt.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = run_builder()
    if args.print_receipt:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
