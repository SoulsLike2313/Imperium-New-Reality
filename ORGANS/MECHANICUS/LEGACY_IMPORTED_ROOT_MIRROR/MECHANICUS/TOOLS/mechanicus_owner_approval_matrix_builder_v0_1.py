from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-ARSENAL-OWNER-APPROVAL-MATRIX-PC-V0_1"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-ARSENAL-OWNER-APPROVAL-MATRIX-PC-V0_1"
)
REGISTRY_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"
USAGE_MAP_REL = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/FIELD_GUIDES/BATCH_001/"
    "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json"
)
DETECTION_RESULTS_REL = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/TOOL_EXPANSION/BATCH_001/tool_detection_results.json"

APPROVED_INSTALL_WAVE_001_IDS = {
    "UTILITIES_7_ZIP",
    "MARKDOWNLINT_CLI",
    "CHECK_JSONSCHEMA_CLI",
    "YAMLLINT_CLI",
}

MATRIX_COLUMNS = [
    "capability_id",
    "category",
    "current_status",
    "what_is_it_ru",
    "why_needed_ru",
    "agent_usage_ru",
    "plus_ru",
    "minus_risk_ru",
    "install_needed",
    "platform_profile_pc_windows",
    "platform_profile_ubuntu_vm3",
    "platform_profile_cross_platform",
    "platform_profile_unknown_notes",
    "install_command_candidate",
    "detect_command",
    "validation_command",
    "stress_test_candidate",
    "receipt_required",
    "recommendation",
    "owner_decision",
    "approved_for_install_wave_001",
    "notes_for_owner_ru",
]

RECOMMENDATION_ENUM = {
    "install",
    "defer",
    "keep_candidate",
    "sandbox",
    "canon_later",
    "reject",
    "quarantine",
}

OWNER_DECISION_ENUM = {"approve", "reject", "hold", "pending"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Mechanicus owner approval matrix and queue artifacts.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--registry", default=REGISTRY_REL)
    parser.add_argument("--usage-map", default=USAGE_MAP_REL)
    parser.add_argument("--detection-results", default=DETECTION_RESULTS_REL)
    return parser.parse_args()


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=path_hint, text=True).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return path_hint


def normalized_path(value: str) -> str:
    return value.replace("\\", "/")


def as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def first_nonempty(*values: str) -> str:
    for value in values:
        text = str(value).strip()
        if text:
            return text
    return ""


def detect_command_map(detection_payload: dict[str, Any]) -> dict[str, list[str]]:
    rows = detection_payload.get("results", [])
    mapping: dict[str, list[str]] = {}
    if not isinstance(rows, list):
        return mapping
    for row in rows:
        if not isinstance(row, dict):
            continue
        capability_id = str(row.get("tool_id", "")).strip()
        commands = as_list(row.get("detection_commands"))
        if capability_id and commands:
            mapping[capability_id] = commands
    return mapping


def install_command_map(detection_payload: dict[str, Any]) -> dict[str, str]:
    rows = detection_payload.get("results", [])
    mapping: dict[str, str] = {}
    if not isinstance(rows, list):
        return mapping
    for row in rows:
        if not isinstance(row, dict):
            continue
        capability_id = str(row.get("tool_id", "")).strip()
        proposed = str(row.get("proposed_install_command", "")).strip()
        if capability_id and proposed:
            mapping[capability_id] = proposed
    return mapping


def guess_install_command(
    capability_id: str,
    name: str,
    install_needed: bool,
    mapped_install: str,
) -> str:
    if not install_needed:
        return ""
    if mapped_install:
        return mapped_install

    key = f"{capability_id} {name}".lower()
    rules: list[tuple[str, str]] = [
        ("7_zip", "winget install 7zip.7zip"),
        ("7-zip", "winget install 7zip.7zip"),
        ("markdownlint", "npm install -g markdownlint-cli"),
        ("check_jsonschema", "python -m pip install --user check-jsonschema"),
        ("yamllint", "python -m pip install --user yamllint"),
        ("ruff", "python -m pip install --user ruff"),
        ("mypy", "python -m pip install --user mypy"),
        ("pyright", "npm install -g pyright"),
        ("pre-commit", "python -m pip install --user pre-commit"),
        ("jsonschema", "python -m pip install --user jsonschema"),
        ("pytest", "python -m pip install --user pytest"),
        ("playwright", "npm install -D @playwright/test"),
        ("react", "npm install react react-dom"),
        ("vite", "npm create vite@latest"),
        ("typescript", "npm install -D typescript"),
        ("tailwind", "npm install -D tailwindcss"),
        ("framer", "npm install framer-motion"),
        ("lucide", "npm install lucide"),
        ("jq", "winget install jqlang.jq"),
        ("yq", "winget install MikeFarah.yq"),
        ("ripgrep", "winget install BurntSushi.ripgrep"),
        ("fd", "winget install sharkdp.fd"),
    ]
    for fragment, command in rules:
        if fragment in key:
            return command
    return "TO_DEFINE_BY_OWNER_INSTALL_GATE"


def guess_detect_command(
    capability_id: str,
    name: str,
    source_type: str,
    card_path: str,
    mapped_detection: list[str],
) -> str:
    if mapped_detection:
        return mapped_detection[0]

    key = f"{capability_id} {name}".lower()
    rules: list[tuple[str, str]] = [
        ("7_zip", "7z i"),
        ("7-zip", "7z i"),
        ("markdownlint", "markdownlint --version"),
        ("check_jsonschema", "check-jsonschema --version"),
        ("yamllint", "yamllint --version"),
        ("ruff", "ruff --version"),
        ("mypy", "mypy --version"),
        ("pyright", "pyright --version"),
        ("pre-commit", "pre-commit --version"),
        ("jsonschema", "python -m jsonschema --version"),
        ("pytest", "pytest --version"),
        ("playwright", "npx playwright --version"),
        ("react", "node -p \"require('react/package.json').version\""),
        ("vite", "npx vite --version"),
        ("typescript", "npx tsc --version"),
        ("tailwind", "npx tailwindcss --help"),
        ("framer", "node -p \"require('framer-motion/package.json').version\""),
        ("lucide", "node -p \"require('lucide/package.json').version\""),
        ("jq", "jq --version"),
        ("yq", "yq --version"),
        ("ripgrep", "rg --version"),
        ("fd", "fd --version"),
        ("git", "git --version"),
        ("powershell", "powershell -NoProfile -Command \"$PSVersionTable.PSVersion.ToString()\""),
        ("python", "python --version"),
        ("sqlite", "python -c \"import sqlite3; print(sqlite3.sqlite_version)\""),
    ]
    for fragment, command in rules:
        if fragment in key:
            return command

    if source_type in {"practice", "reference_code", "algorithm", "repo_existing", "built_in"}:
        return (
            "python -c \"from pathlib import Path; "
            f"p=Path(r'{normalized_path(card_path)}'); "
            "print(p.exists()); raise SystemExit(0 if p.exists() else 2)\""
        )
    return "TO_DEFINE_DETECT_COMMAND"


def recommendation_from_state(
    status: str,
    recommended_next_action: str,
    reserved: bool,
    category: str,
    install_needed: bool,
    approved_wave_001: bool,
) -> str:
    if status == "REJECTED":
        return "reject"
    if status == "QUARANTINE":
        return "quarantine"
    if reserved or category in {"CLOUD_LLM_ADAPTERS", "LOCAL_LLM"}:
        return "defer"
    if status == "CANON":
        return "canon_later"

    action_map = {
        "KEEP_CANDIDATE": "keep_candidate",
        "VALIDATE_SANDBOX": "sandbox",
        "OWNER_DECISION": "defer",
        "PROMOTE_CANON_AFTER_RECEIPT": "canon_later",
    }
    candidate = action_map.get(recommended_next_action, "")

    if approved_wave_001 and install_needed:
        return "install"
    if status == "SANDBOX":
        if candidate in {"install", "defer", "canon_later"}:
            return candidate
        return "sandbox"
    if candidate:
        return candidate
    if install_needed:
        return "keep_candidate"
    return "keep_candidate"


def platform_profiles(
    category: str,
    source_type: str,
    install_needed: bool,
    reserved: bool,
) -> tuple[str, str, str, str]:
    if reserved or category in {"CLOUD_LLM_ADAPTERS", "LOCAL_LLM"}:
        return (
            "DEFERRED_POLICY_LANE; no activation in this task.",
            "FORBIDDEN_IN_THIS_TASK; VM3/Ubuntu untouched by contract.",
            "NOT_EVALUATED_FOR_THIS_TASK",
            "Reserved lane requires separate Owner gate before any runtime action.",
        )

    if install_needed:
        pc = "DETECT_ONLY_NOW; install only after Owner approval wave."
    else:
        pc = "READY_FOR_SCOPE_USAGE_WITH_RECEIPT_DISCIPLINE."

    if source_type in {"practice", "reference_code", "algorithm", "repo_existing", "built_in"}:
        cross = "LIKELY_CROSS_PLATFORM_CONTEXT"
    elif source_type in {"external_tool", "adapter"}:
        cross = "TO_VERIFY_PER_PLATFORM_PROFILE"
    else:
        cross = "UNKNOWN"

    ubuntu = "NOT_TESTED_IN_THIS_TASK; VM3 profile intentionally not touched."
    note = "No installs executed. Detection and planning only."
    return (pc, ubuntu, cross, note)


def make_ru_plus(allowed_use_cases: list[str], status: str) -> str:
    if allowed_use_cases:
        picked = "; ".join(allowed_use_cases[:2])
        return f"Повышает повторяемость задач. Разрешенные use-case: {picked}. Статус сейчас: {status}."
    return f"Повышает операционную дисциплину в статусе {status}."


def make_ru_minus(limitations: str, forbidden_use_cases: list[str], install_needed: bool) -> str:
    parts: list[str] = []
    if limitations:
        parts.append(limitations)
    if forbidden_use_cases:
        parts.append("Forbidden: " + "; ".join(forbidden_use_cases[:2]))
    if install_needed:
        parts.append("Требует owner gate на установку.")
    if not parts:
        parts.append("Риски низкие, но нужен receipt-контур.")
    return " ".join(parts)


def make_matrix_markdown(rows: list[dict[str, Any]], task_id: str) -> str:
    lines = [
        f"# OWNER APPROVAL MATRIX - {task_id}",
        "",
        "| capability_id | category | current_status | recommendation | install_needed | wave_001 | owner_decision |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {capability_id} | {category} | {current_status} | {recommendation} | {install_needed} | {wave} | {owner_decision} |".format(
                capability_id=str(row["capability_id"]).replace("|", "/"),
                category=str(row["category"]).replace("|", "/"),
                current_status=str(row["current_status"]).replace("|", "/"),
                recommendation=str(row["recommendation"]).replace("|", "/"),
                install_needed="true" if bool(row["install_needed"]) else "false",
                wave="true" if bool(row["approved_for_install_wave_001"]) else "false",
                owner_decision=str(row["owner_decision"]).replace("|", "/"),
            )
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    registry_path = repo_root / args.registry
    usage_map_path = repo_root / args.usage_map
    detection_path = repo_root / args.detection_results

    registry_payload = load_json(registry_path)
    usage_map_payload = load_json(usage_map_path)
    detection_payload = load_json(detection_path) if detection_path.exists() else {"results": []}

    cards = registry_payload.get("cards", [])
    if not isinstance(cards, list):
        raise RuntimeError("Invalid registry format: `cards` must be a list.")

    usage_entries = usage_map_payload.get("entries", [])
    if not isinstance(usage_entries, list):
        raise RuntimeError("Invalid usage map format: `entries` must be a list.")
    usage_by_id: dict[str, dict[str, Any]] = {}
    for entry in usage_entries:
        if not isinstance(entry, dict):
            continue
        capability_id = str(entry.get("capability_id", "")).strip()
        if capability_id:
            usage_by_id[capability_id] = entry

    mapped_detect = detect_command_map(detection_payload)
    mapped_install = install_command_map(detection_payload)

    rows: list[dict[str, Any]] = []
    source_paths_missing: list[str] = []

    for card in cards:
        if not isinstance(card, dict):
            continue
        capability_id = str(card.get("capability_id", "")).strip()
        card_path_rel = normalized_path(str(card.get("card_path", "")).strip())
        if not capability_id or not card_path_rel:
            continue

        card_path_abs = repo_root / card_path_rel
        if not card_path_abs.exists():
            source_paths_missing.append(card_path_rel)
            continue
        card_payload = load_json(card_path_abs)
        if not isinstance(card_payload, dict):
            source_paths_missing.append(card_path_rel)
            continue

        usage = usage_by_id.get(capability_id, {})
        category = first_nonempty(str(card_payload.get("category", "")), str(card.get("category", "")))
        status = first_nonempty(str(card_payload.get("status", "")), str(card.get("status", "")))
        name = first_nonempty(str(card_payload.get("name", "")), capability_id)
        source_type = first_nonempty(str(card_payload.get("source_type", "")), str(card.get("source_type", "")))
        install_needed = bool(card_payload.get("install_required", card.get("install_required", False)))
        reserved = bool(card_payload.get("reserved", False)) or bool(usage.get("reserved", False))
        approved_wave_001 = capability_id in APPROVED_INSTALL_WAVE_001_IDS

        validation_commands = as_list(card_payload.get("validation_commands"))
        if not validation_commands:
            validation_commands = as_list(usage.get("validation_commands"))
        validation_command = "; ".join(validation_commands)

        expected_receipts = as_list(card_payload.get("expected_receipts"))
        if not expected_receipts:
            expected_receipts = as_list(usage.get("required_receipts"))
        receipt_required = "; ".join(expected_receipts)

        mapped_detection = mapped_detect.get(capability_id, [])
        detect_command = guess_detect_command(capability_id, name, source_type, card_path_rel, mapped_detection)
        install_command_candidate = guess_install_command(
            capability_id=capability_id,
            name=name,
            install_needed=install_needed,
            mapped_install=mapped_install.get(capability_id, ""),
        )

        recommendation = recommendation_from_state(
            status=status,
            recommended_next_action=str(usage.get("recommended_next_action", "")).strip(),
            reserved=reserved,
            category=category,
            install_needed=install_needed,
            approved_wave_001=approved_wave_001,
        )
        if recommendation not in RECOMMENDATION_ENUM:
            recommendation = "keep_candidate"

        what_is_it_ru = first_nonempty(
            str(usage.get("plain_ru_description", "")),
            f"{name}: capability в категории {category}.",
        )
        why_needed_ru = first_nonempty(
            str(usage.get("why_needed_for_imperium", "")),
            str(card_payload.get("what_problem_it_solves", "")),
            "Нужен для повышения управляемости арсенала и повторяемости задач.",
        )
        agent_usage_ru = (
            first_nonempty(str(usage.get("servitor_scope_rule", "")), "Использовать в scope только в рамках явных gate.") +
            " " +
            first_nonempty(str(usage.get("local_agent_scope_rule", "")), "Локальный агент работает только в допущенном контуре.")
        ).strip()

        allowed_use_cases = as_list(usage.get("allowed_use_cases"))
        if not allowed_use_cases:
            allowed_use_cases = as_list(card_payload.get("allowed_use_cases"))
        forbidden_use_cases = as_list(usage.get("forbidden_use_cases"))
        if not forbidden_use_cases:
            forbidden_use_cases = as_list(card_payload.get("forbidden_use_cases"))

        plus_ru = make_ru_plus(allowed_use_cases, status)
        minus_risk_ru = make_ru_minus(
            limitations=str(card_payload.get("limitations", "")).strip(),
            forbidden_use_cases=forbidden_use_cases,
            install_needed=install_needed,
        )

        (
            platform_pc_windows,
            platform_ubuntu_vm3,
            platform_cross,
            platform_unknown_notes,
        ) = platform_profiles(
            category=category,
            source_type=source_type,
            install_needed=install_needed,
            reserved=reserved,
        )

        stress_test_candidate = (
            "Manual stress candidate: run detect_command and validation_command 3x, "
            "then compare receipt names and verdict stability."
        )
        notes_for_owner_ru = (
            f"source_type={source_type}; install_gate={card_payload.get('install_gate', 'N/A')}; "
            f"reserved={'true' if reserved else 'false'}."
        )

        row: dict[str, Any] = {
            "capability_id": capability_id,
            "category": category,
            "current_status": status,
            "what_is_it_ru": what_is_it_ru,
            "why_needed_ru": why_needed_ru,
            "agent_usage_ru": agent_usage_ru,
            "plus_ru": plus_ru,
            "minus_risk_ru": minus_risk_ru,
            "install_needed": install_needed,
            "platform_profile_pc_windows": platform_pc_windows,
            "platform_profile_ubuntu_vm3": platform_ubuntu_vm3,
            "platform_profile_cross_platform": platform_cross,
            "platform_profile_unknown_notes": platform_unknown_notes,
            "install_command_candidate": install_command_candidate,
            "detect_command": detect_command,
            "validation_command": validation_command,
            "stress_test_candidate": stress_test_candidate,
            "receipt_required": receipt_required,
            "recommendation": recommendation,
            "owner_decision": "pending",
            "approved_for_install_wave_001": approved_wave_001,
            "notes_for_owner_ru": notes_for_owner_ru,
            "name": name,
            "source_type": source_type,
            "card_path": card_path_rel,
        }
        rows.append(row)

    rows.sort(key=lambda item: (str(item["category"]), str(item["capability_id"])))

    status_counts: Counter[str] = Counter(str(row["current_status"]) for row in rows)
    recommendation_counts: Counter[str] = Counter(str(row["recommendation"]) for row in rows)
    category_counts: Counter[str] = Counter(str(row["category"]) for row in rows)
    present_ids = {str(row["capability_id"]) for row in rows}
    missing_wave_capabilities = sorted(APPROVED_INSTALL_WAVE_001_IDS - present_ids)

    matrix_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "report_root": normalized_path(str(report_root.relative_to(repo_root).as_posix())),
        "source_registry": normalized_path(str(registry_path.relative_to(repo_root).as_posix())),
        "source_usage_map": normalized_path(str(usage_map_path.relative_to(repo_root).as_posix())),
        "source_detection_results": normalized_path(str(detection_path.relative_to(repo_root).as_posix())),
        "row_count": len(rows),
        "required_columns": MATRIX_COLUMNS,
        "enums": {
            "recommendation": sorted(RECOMMENDATION_ENUM),
            "owner_decision": sorted(OWNER_DECISION_ENUM),
        },
        "summary": {
            "status_counts": dict(sorted(status_counts.items())),
            "recommendation_counts": dict(sorted(recommendation_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "approved_wave_001_present_count": sum(1 for row in rows if bool(row["approved_for_install_wave_001"])),
            "approved_wave_001_missing_capabilities": missing_wave_capabilities,
            "missing_card_payload_paths": source_paths_missing,
        },
        "rows": rows,
    }

    matrix_json_path = report_root / "owner_approval_matrix_v0_1.json"
    write_json(matrix_json_path, matrix_payload)

    matrix_csv_path = report_root / "OWNER_APPROVAL_MATRIX.csv"
    with matrix_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATRIX_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in MATRIX_COLUMNS})

    matrix_md_path = report_root / "OWNER_APPROVAL_MATRIX.md"
    write_text(matrix_md_path, make_matrix_markdown(rows, args.task_id))

    install_wave_rows = [row for row in rows if bool(row["approved_for_install_wave_001"])]
    recommended_install_rows = [row for row in rows if str(row["recommendation"]) == "install"]
    recommended_install_waves = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "waves": [
            {
                "wave_id": "INSTALL_WAVE_001_OWNER_APPROVED",
                "policy": "Do not install in this task. Planning artifact only.",
                "capability_count": len(install_wave_rows),
                "capabilities": [
                    {
                        "capability_id": row["capability_id"],
                        "install_command_candidate": row["install_command_candidate"],
                        "owner_decision": row["owner_decision"],
                        "recommendation": row["recommendation"],
                        "notes_for_owner_ru": row["notes_for_owner_ru"],
                    }
                    for row in install_wave_rows
                ],
            }
        ],
        "recommended_install_now_count": len(recommended_install_rows),
        "recommended_install_now_capabilities": [
            {
                "capability_id": row["capability_id"],
                "install_command_candidate": row["install_command_candidate"],
            }
            for row in recommended_install_rows
        ],
        "missing_owner_approved_capabilities": missing_wave_capabilities,
    }
    write_json(report_root / "recommended_install_waves_v0_1.json", recommended_install_waves)

    defer_queue_rows = [
        row
        for row in rows
        if str(row["recommendation"]) in {"defer", "keep_candidate", "canon_later", "sandbox"}
    ]
    defer_queue_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "queue_type": "defer_like",
        "count": len(defer_queue_rows),
        "rows": [
            {
                "capability_id": row["capability_id"],
                "category": row["category"],
                "current_status": row["current_status"],
                "recommendation": row["recommendation"],
                "owner_decision": row["owner_decision"],
                "notes_for_owner_ru": row["notes_for_owner_ru"],
            }
            for row in defer_queue_rows
        ],
    }
    write_json(report_root / "defer_queue_v0_1.json", defer_queue_payload)

    reject_or_quarantine_rows = [
        row for row in rows if str(row["recommendation"]) in {"reject", "quarantine"}
    ]
    reject_or_quarantine_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "count": len(reject_or_quarantine_rows),
        "rows": [
            {
                "capability_id": row["capability_id"],
                "category": row["category"],
                "current_status": row["current_status"],
                "recommendation": row["recommendation"],
                "notes_for_owner_ru": row["notes_for_owner_ru"],
            }
            for row in reject_or_quarantine_rows
        ],
    }
    write_json(report_root / "reject_or_quarantine_queue_v0_1.json", reject_or_quarantine_payload)

    decision_template_rows = [
        {
            "capability_id": row["capability_id"],
            "category": row["category"],
            "current_status": row["current_status"],
            "recommendation": row["recommendation"],
            "owner_decision": row["owner_decision"],
            "approved_for_install_wave_001": row["approved_for_install_wave_001"],
            "owner_comment_ru": "",
        }
        for row in rows
    ]
    decision_json_payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "row_count": len(decision_template_rows),
        "rows": decision_template_rows,
    }
    write_json(report_root / "owner_decision_template_v0_1.json", decision_json_payload)

    decision_csv_path = report_root / "owner_decision_template_v0_1.csv"
    decision_columns = [
        "capability_id",
        "category",
        "current_status",
        "recommendation",
        "owner_decision",
        "approved_for_install_wave_001",
        "owner_comment_ru",
    ]
    with decision_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=decision_columns)
        writer.writeheader()
        for row in decision_template_rows:
            writer.writerow(row)

    output_files = [
        "OWNER_APPROVAL_MATRIX.md",
        "OWNER_APPROVAL_MATRIX.csv",
        "owner_approval_matrix_v0_1.json",
        "recommended_install_waves_v0_1.json",
        "defer_queue_v0_1.json",
        "reject_or_quarantine_queue_v0_1.json",
        "owner_decision_template_v0_1.csv",
        "owner_decision_template_v0_1.json",
    ]
    matrix_build_receipt = {
        "task_id": args.task_id,
        "script": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_owner_approval_matrix_builder_v0_1.py",
        "generated_at_utc": utc_now(),
        "row_count": len(rows),
        "output_root": normalized_path(str(report_root.relative_to(repo_root).as_posix())),
        "output_files": [normalized_path(str((report_root / name).relative_to(repo_root).as_posix())) for name in output_files],
        "source_files": [
            normalized_path(str(registry_path.relative_to(repo_root).as_posix())),
            normalized_path(str(usage_map_path.relative_to(repo_root).as_posix())),
            normalized_path(str(detection_path.relative_to(repo_root).as_posix())),
        ],
        "install_actions_performed": False,
        "summary": {
            "status_counts": dict(sorted(status_counts.items())),
            "recommendation_counts": dict(sorted(recommendation_counts.items())),
            "approved_wave_001_missing_capabilities": missing_wave_capabilities,
            "missing_card_payload_paths": source_paths_missing,
        },
        "verdict": "PASS" if not source_paths_missing else "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "matrix_build_receipt.json", matrix_build_receipt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
