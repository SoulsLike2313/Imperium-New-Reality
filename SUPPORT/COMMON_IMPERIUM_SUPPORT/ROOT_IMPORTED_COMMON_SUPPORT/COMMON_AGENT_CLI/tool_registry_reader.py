from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class CheckResult:
    errors: list[str]
    warnings: list[str]
    tool_count: int


DEFAULT_ALLOWED_AVAILABILITY_STATUSES = {
    "AVAILABLE_BOTH",
    "AVAILABLE_VM2",
    "AVAILABLE_PC",
    "KNOWN_NOT_INSTALLED",
    "NOT_FOUND_ON_VM2",
    "NOT_FOUND_ON_PC",
    "BLOCKED_NOT_ADMITTED",
    "UNKNOWN_NEEDS_PROBE",
}

VM2_AVAILABLE_STATUSES = {"AVAILABLE_BOTH", "AVAILABLE_VM2"}

ORGAN_REQUIRED_TOOL_IDS: dict[str, list[str]] = {
    "INQUISITION_AGENT": ["ripgrep", "gitleaks", "semgrep", "bandit", "pip-audit", "git"],
    "MECHANICUS_AGENT": [],
    "ADMINISTRATUM_AGENT": ["git", "jq", "yq", "duckdb"],
    "ASTRONOMICON_AGENT": ["git", "jq", "yq"],
    "STRATEGIUM_AGENT": ["duckdb", "jq", "yq", "git"],
    "OFFICIO_AGENTIS_AGENT": ["jsonschema", "jq", "git"],
    "SCHOLA_IMPERIALIS_AGENT": ["pytest", "git", "jsonschema"],
    "DOCTRINARIUM_AGENT": ["jsonschema", "jq", "yq", "git"],
}

ORGAN_VIRTUAL_CAPABILITIES: dict[str, list[dict[str, Any]]] = {
    "ASTRONOMICON_AGENT": [
        {
            "tool_id": "future_graph_task_map_tools",
            "capability_summary": "future graph/task-map tooling capability",
            "availability_status": "UNKNOWN_NEEDS_PROBE",
        }
    ],
    "STRATEGIUM_AGENT": [
        {
            "tool_id": "report_csv_tools",
            "capability_summary": "report/csv analysis tooling capability",
            "availability_status": "UNKNOWN_NEEDS_PROBE",
        }
    ],
    "OFFICIO_AGENTIS_AGENT": [
        {
            "tool_id": "internal_contract_checker",
            "capability_summary": "internal contract checker capability",
            "availability_status": "UNKNOWN_NEEDS_PROBE",
        }
    ],
    "SCHOLA_IMPERIALIS_AGENT": [
        {
            "tool_id": "regression_corpus_tools",
            "capability_summary": "fixtures and regression corpus tooling capability",
            "availability_status": "UNKNOWN_NEEDS_PROBE",
        }
    ],
    "DOCTRINARIUM_AGENT": [
        {
            "tool_id": "doctrine_law_validators",
            "capability_summary": "doctrine/law validator capability",
            "availability_status": "UNKNOWN_NEEDS_PROBE",
        }
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def parse_index(index_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = load_json(index_path)
    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        raise ValueError(f".tools must be a list: {index_path}")
    parsed: list[dict[str, Any]] = []
    for item in tools:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid tool record (not object): {item!r}")
        parsed.append(item)
    return payload, parsed


def check_registry(index_path: Path) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    tool_count = 0
    try:
        payload, tools = parse_index(index_path)
    except Exception as err:
        return CheckResult(errors=[f"index_load_error: {err}"], warnings=[], tool_count=0)

    schema = str(payload.get("schema_version", ""))
    if not schema:
        errors.append("missing schema_version in TOOL_INDEX.json")
    if not schema.startswith("MECHANICUS_TOOL_INDEX_"):
        warnings.append(f"unexpected TOOL_INDEX schema_version: {schema}")

    root = index_path.parent
    seen_tool_ids: set[str] = set()
    for item in tools:
        tool_count += 1
        tool_id = str(item.get("tool_id", "")).strip()
        card_rel = str(item.get("tool_card_path", "")).strip()
        if not tool_id:
            errors.append("tool record missing tool_id")
            continue
        if tool_id in seen_tool_ids:
            errors.append(f"duplicate tool_id in index: {tool_id}")
            continue
        seen_tool_ids.add(tool_id)

        if not card_rel:
            errors.append(f"tool {tool_id} missing tool_card_path")
            continue
        card_path = (root / card_rel).resolve()
        if not card_path.exists():
            errors.append(f"tool card not found: tool_id={tool_id} path={card_path}")
            continue
        try:
            card = load_json(card_path)
        except Exception as err:
            errors.append(f"tool card invalid JSON: tool_id={tool_id} path={card_path} error={err}")
            continue

        card_tool_id = str(card.get("tool_id", "")).strip()
        if card_tool_id != tool_id:
            errors.append(f"tool_id mismatch index/card: index={tool_id} card={card_tool_id} path={card_path}")
        if str(card.get("schema_version", "")).strip() != "MECHANICUS_TOOL_CARD_V0_1":
            warnings.append(f"unexpected card schema_version for {tool_id}: {card.get('schema_version')}")

        required_fields = [
            "display_name",
            "owner_organ",
            "consumer_organs",
            "capability_summary",
            "allowed_use_cases",
            "forbidden_use_cases",
            "install_policy",
            "pc_status",
            "vm2_status",
            "version_pc",
            "version_vm2",
            "command_examples",
            "evidence_required",
            "failure_policy",
            "admission_status",
        ]
        for field in required_fields:
            if field not in card:
                errors.append(f"tool card missing field: tool_id={tool_id} field={field}")

    return CheckResult(errors=errors, warnings=warnings, tool_count=tool_count)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def default_tool_index_path(repo_root: Optional[Path] = None) -> Path:
    if repo_root is not None:
        return repo_root / "IMPERIUM_NEW_GENERATION" / "ORGAN_AGENTS" / "MECHANICUS_AGENT" / "TOOL_REGISTRY" / "TOOL_INDEX.json"
    return Path(__file__).resolve().parents[1] / "ORGAN_AGENTS" / "MECHANICUS_AGENT" / "TOOL_REGISTRY" / "TOOL_INDEX.json"


def _to_list_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _load_card(index_path: Path, item: dict[str, Any]) -> tuple[dict[str, Any], str]:
    rel = str(item.get("tool_card_path", "")).strip()
    if not rel:
        return {}, ""
    path = (index_path.parent / rel).resolve()
    if not path.exists():
        return {}, str(path)
    try:
        card = load_json(path)
    except Exception:
        return {}, str(path)
    return card, str(path)


def _normalize_tool_row(index_path: Path, item: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    card, card_path = _load_card(index_path, item)
    tool_id = str(item.get("tool_id", "")).strip() or str(card.get("tool_id", "")).strip()
    status = str(item.get("combined_status", "")).strip() or str(card.get("combined_status", "")).strip() or "UNKNOWN_NEEDS_PROBE"
    owner_organ = str(card.get("owner_organ", "")).strip() or str(item.get("owner_organ", "")).strip() or "MECHANICUS_AGENT"
    consumer_organs = _to_list_strings(card.get("consumer_organs"))
    if not consumer_organs:
        consumer_organs = _to_list_strings(item.get("consumer_organs"))

    if status and status not in DEFAULT_ALLOWED_AVAILABILITY_STATUSES:
        warnings.append(f"unexpected_availability_status:{tool_id}:{status}")

    row: dict[str, Any] = {
        "tool_id": tool_id,
        "owner_organ": owner_organ,
        "consumer_organs": consumer_organs,
        "availability_status": status or "UNKNOWN_NEEDS_PROBE",
        "capability_summary": str(card.get("capability_summary", "")).strip(),
        "allowed_use": _to_list_strings(card.get("allowed_use_cases")) or _to_list_strings(card.get("allowed_use")),
        "forbidden_use": _to_list_strings(card.get("forbidden_use_cases")) or _to_list_strings(card.get("forbidden_use")),
        "evidence_required": _to_list_strings(card.get("evidence_required")),
        "failure_policy": str(card.get("failure_policy", "")).strip(),
        "registry_row_source": str(item.get("tool_card_path", "")).strip(),
        "card_path_resolved": card_path,
    }
    return row, warnings


def _virtual_tool_row(organ_id: str, item: dict[str, Any]) -> dict[str, Any]:
    tool_id = str(item.get("tool_id", "")).strip()
    summary = str(item.get("capability_summary", "")).strip()
    status = str(item.get("availability_status", "UNKNOWN_NEEDS_PROBE")).strip() or "UNKNOWN_NEEDS_PROBE"
    return {
        "tool_id": tool_id,
        "owner_organ": "MECHANICUS_AGENT",
        "consumer_organs": [organ_id],
        "availability_status": status,
        "capability_summary": summary,
        "allowed_use": ["task-scoped evidence-first capability use"],
        "forbidden_use": ["fake availability claims", "installation without owner gate"],
        "evidence_required": ["probe report or explicit owner-approved admission record"],
        "failure_policy": "Mark as missing/unknown and continue without install.",
        "registry_row_source": "virtual_focus_capability",
        "card_path_resolved": "",
    }


def _availability_to_missing_reason(status: str) -> str:
    token = status.upper()
    if token in VM2_AVAILABLE_STATUSES:
        return ""
    if token == "AVAILABLE_PC":
        return "available_on_pc_only"
    if token == "KNOWN_NOT_INSTALLED":
        return "known_not_installed"
    if token == "NOT_FOUND_ON_VM2":
        return "not_found_on_vm2"
    if token == "NOT_FOUND_ON_PC":
        return "not_found_on_pc"
    if token == "BLOCKED_NOT_ADMITTED":
        return "blocked_not_admitted"
    return "unknown_or_unprobed"


def build_organ_tool_view(organ_id: str, index_path: Path) -> dict[str, Any]:
    warnings: list[str] = []
    try:
        index_payload, tools = parse_index(index_path)
    except Exception as err:
        return {
            "schema_version": "ORGAN_TOOL_CAPABILITY_VIEW_V0_1",
            "generated_at_utc": utc_now(),
            "organ_id": organ_id,
            "registry_source": str(index_path),
            "verdict": "BLOCKED_TOOL_REGISTRY_UNREADABLE",
            "errors": [f"tool_registry_unreadable:{err}"],
            "warnings": [],
            "relevant_tools": [],
            "available_tools": [],
            "missing_tools": [],
            "evidence_policy": {
                "install_policy": "NO_INSTALL_WITHOUT_OWNER_GATE",
                "required": "Missing tools must be reported as missing; no fake green.",
            },
        }

    by_id: dict[str, dict[str, Any]] = {}
    for item in tools:
        row, row_warnings = _normalize_tool_row(index_path, item)
        warnings.extend(row_warnings)
        tool_id = str(row.get("tool_id", "")).strip()
        if tool_id:
            by_id[tool_id] = row

    normalized_organ = organ_id.strip().upper()
    required_ids = ORGAN_REQUIRED_TOOL_IDS.get(normalized_organ, [])
    relevant_tools: list[dict[str, Any]] = []

    if normalized_organ == "MECHANICUS_AGENT":
        relevant_tools = [by_id[key] for key in sorted(by_id.keys())]
    else:
        for tool_id in required_ids:
            if tool_id in by_id:
                relevant_tools.append(by_id[tool_id])
            else:
                warnings.append(f"required_tool_not_in_registry:{normalized_organ}:{tool_id}")
                relevant_tools.append(
                    {
                        "tool_id": tool_id,
                        "owner_organ": "MECHANICUS_AGENT",
                        "consumer_organs": [normalized_organ],
                        "availability_status": "UNKNOWN_NEEDS_PROBE",
                        "capability_summary": "required organ tool is not present in current TOOL_INDEX registry",
                        "allowed_use": ["registry-check and evidence collection only"],
                        "forbidden_use": ["claiming availability without evidence"],
                        "evidence_required": ["updated tool registry admission evidence"],
                        "failure_policy": "Mark missing and continue without install.",
                        "registry_row_source": "",
                        "card_path_resolved": "",
                    }
                )

    for virtual in ORGAN_VIRTUAL_CAPABILITIES.get(normalized_organ, []):
        warnings.append(f"virtual_focus_capability_unprobed:{normalized_organ}:{virtual.get('tool_id', '')}")
        relevant_tools.append(_virtual_tool_row(normalized_organ, virtual))

    available_tools: list[str] = []
    missing_tools: list[dict[str, str]] = []
    for row in relevant_tools:
        tool_id = str(row.get("tool_id", "")).strip()
        status = str(row.get("availability_status", "")).strip() or "UNKNOWN_NEEDS_PROBE"
        reason = _availability_to_missing_reason(status)
        if reason:
            missing_tools.append({"tool_id": tool_id, "availability_status": status, "reason": reason})
        else:
            available_tools.append(tool_id)

    warnings = list(dict.fromkeys(warnings))
    verdict = "PASS" if not warnings else "WARN"
    return {
        "schema_version": "ORGAN_TOOL_CAPABILITY_VIEW_V0_1",
        "generated_at_utc": utc_now(),
        "organ_id": normalized_organ,
        "registry_source": str(index_path),
        "registry_owner": str(index_payload.get("registry_owner", "MECHANICUS_AGENT")),
        "relevant_tools": relevant_tools,
        "available_tools": available_tools,
        "missing_tools": missing_tools,
        "warnings": warnings,
        "verdict": verdict,
        "evidence_policy": {
            "install_policy": str(index_payload.get("install_policy", "NO_INSTALL_WITHOUT_OWNER_GATE")),
            "required": "No fake green. Missing tools are reported as missing with evidence policy.",
            "field_contract": [
                "tool_id",
                "owner_organ",
                "consumer_organs",
                "availability_status",
                "capability_summary",
                "allowed_use",
                "forbidden_use",
                "evidence_required",
                "failure_policy",
            ],
        },
    }


def cmd_list(index_path: Path, as_json: bool) -> int:
    _, tools = parse_index(index_path)
    rows = []
    for item in tools:
        rows.append(
            {
                "tool_id": str(item.get("tool_id", "")),
                "display_name": str(item.get("display_name", "")),
                "combined_status": str(item.get("combined_status", "")),
                "owner_organ": str(item.get("owner_organ", "")),
                "tool_card_path": str(item.get("tool_card_path", "")),
            }
        )
    if as_json:
        print(json.dumps({"schema_version": "MECHANICUS_TOOL_LIST_V0_1", "tools": rows}, ensure_ascii=True, indent=2))
        return 0

    print("MECHANICUS TOOL REGISTRY LIST")
    print("tool_id | owner_organ | combined_status | tool_card_path")
    for row in rows:
        print(f"{row['tool_id']} | {row['owner_organ']} | {row['combined_status']} | {row['tool_card_path']}")
    return 0


def cmd_check(index_path: Path, report_json: Path | None) -> int:
    result = check_registry(index_path)
    verdict = "PASS" if not result.errors else "BLOCKED_TOOL_REGISTRY_INVALID"
    payload = {
        "schema_version": "TOOL_REGISTRY_CHECK_REPORT_V0_1",
        "generated_at_utc": utc_now(),
        "index_path": str(index_path),
        "tool_count": result.tool_count,
        "errors": result.errors,
        "warnings": result.warnings,
        "verdict": verdict,
    }
    if report_json is not None:
        write_json(report_json, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if verdict == "PASS" else 1


def cmd_organ_view(organ_id: str, index_path: Path) -> int:
    payload = build_organ_tool_view(organ_id=organ_id, index_path=index_path)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    verdict = str(payload.get("verdict", "PASS"))
    return 0 if verdict in {"PASS", "WARN"} else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read and validate Mechanicus Tool Registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List tools from TOOL_INDEX.json")
    p_list.add_argument("--index", required=True)
    p_list.add_argument("--as-json", action="store_true")

    p_check = sub.add_parser("check", help="Validate TOOL_INDEX.json and tool cards")
    p_check.add_argument("--index", required=True)
    p_check.add_argument("--report-json", default=None)

    p_organ = sub.add_parser("organ-view", help="Render organ-specific tool capability view.")
    p_organ.add_argument("--organ", required=True)
    p_organ.add_argument("--index", default=str(default_tool_index_path()))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    index_path = Path(args.index)
    if not index_path.exists():
        raise SystemExit(f"index not found: {index_path}")
    if args.command == "list":
        return cmd_list(index_path=index_path, as_json=bool(args.as_json))
    if args.command == "check":
        report_json = Path(args.report_json) if args.report_json else None
        return cmd_check(index_path=index_path, report_json=report_json)
    if args.command == "organ-view":
        return cmd_organ_view(organ_id=str(args.organ), index_path=index_path)
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
