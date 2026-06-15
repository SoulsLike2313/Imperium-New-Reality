#!/usr/bin/env python3
"""Checker for Officio taskpack acceptance, contracts, and read-only inspector links."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

RULES_TASKPACK = ROOT / "RULES" / "taskpack_acceptance_rules_v0_1.md"
RULES_RESPONSE = ROOT / "RULES" / "final_response_contract_v0_1.md"
BODY_GHOST = ROOT / "BODY" / "ghost_evolve_contract_v0_1.md"
TUI_SOURCE = ROOT / "TUI" / "officio_agentis_tui_v0_1.py"

JSON_TARGETS = [
    ROOT / "BODY" / "officio_agentis_body_manifest_v0_1.json",
    ROOT / "ROLES" / "role_registry_v0_1.json",
    ROOT / "GHOST_EVOLVE" / "ghost_evolve_decision_schema_v0_1.json",
    ROOT / "GHOST_EVOLVE" / "accepted_local_upgrades_index_v0_1.json",
    ROOT / "GHOST_EVOLVE" / "rejected_noise_index_v0_1.json",
]

REQUIRED_GATES = [
    "GATE-U00-GIT-TRUTH",
    "GATE-U01-ROLE-ACK",
    "GATE-U02-SCOPE-BOUNDARY",
    "GATE-U04-EVIDENCE-RECEIPT",
    "GATE-U05-STOP-CONDITIONS",
    "GATE-U08-REPO-PURITY",
    "GATE-U09-NO-FAKE-GREEN",
    "GATE-U12-REPORT-OUTPUT-BUDGET",
    "GATE-U13-PYTHON-TYPE-SAFETY",
    "GATE-U14-WHOLE-REPO-SCOPE-RECON",
    "GATE-U15-OPERATIONALITY-IMPACT",
    "GATE-U16-BILINGUAL-UI",
    "GATE-U17-DELIVERABLE-PACKAGE",
    "GATE-U18-AGENT-FACTORY-COMPLIANCE",
    "GATE-U19-SCRIPT-ARTIFACT-PRESERVATION",
    "GATE-U20-AGENT-KPD-SELF-REVIEW",
    "GATE-U21-COMMAND-CHUNKING",
    "GATE-AI00-NO-DIRECT-MODEL-COMMAND",
]

REQUIRED_RESPONSE_LINES = [
    "1. Step name",
    "2. Full path to report/bundle",
    "3. Verdict",
    "4. Short Russian owner comment",
    "5. Commit/push HEAD if performed",
    "6. Worktree clean yes/no",
    "7. Next allowed task",
]

REQUIRED_TUI_PATH_MARKERS = [
    "BODY/officio_agentis_body_manifest_v0_1.json",
    "ROLES/role_registry_v0_1.json",
    "RULES/stop_warn_pass_grammar_v0_1.md",
    "RULES/taskpack_acceptance_rules_v0_1.md",
    "RULES/final_response_contract_v0_1.md",
    "GHOST_EVOLVE/accepted_local_upgrades_index_v0_1.json",
    "GHOST_EVOLVE/rejected_noise_index_v0_1.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def file_contains_all(path: Path, markers: List[str]) -> Tuple[List[str], List[str]]:
    if not path.exists():
        return markers, []
    text = path.read_text(encoding="utf-8")
    missing = [m for m in markers if m not in text]
    return missing, text.splitlines()


def validate_json_targets() -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    parsed: List[str] = []
    for path in JSON_TARGETS:
        if not path.exists():
            errors.append(f"Missing JSON file: {path.as_posix()}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            parsed.append(path.as_posix())
        except json.JSONDecodeError as exc:
            errors.append(f"JSON parse error in {path.as_posix()}: {exc}")
    return errors, parsed


def detect_mutation_tokens(path: Path) -> List[str]:
    """Detect obvious write calls in read-only inspector source."""
    if not path.exists():
        return ["MISSING_TUI_SOURCE"]
    text = path.read_text(encoding="utf-8").lower()
    tokens = [
        "write_text(",
        "open(",
        "\"w\"",
        "'w'",
        "json.dump(",
        "mkdir(",
    ]
    found: List[str] = []
    for token in tokens:
        if token in text:
            found.append(token)
    # `open(` can be read-only, so keep as warn if no explicit write mode token is found.
    if found == ["open("]:
        return []
    return found


def build_report() -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    missing_gates, _ = file_contains_all(RULES_TASKPACK, REQUIRED_GATES)
    if missing_gates:
        errors.append(f"Taskpack rules missing required gates: {', '.join(missing_gates)}")

    missing_response_lines, _ = file_contains_all(RULES_RESPONSE, REQUIRED_RESPONSE_LINES)
    if missing_response_lines:
        errors.append(f"Final response contract missing lines: {', '.join(missing_response_lines)}")

    ghost_markers = ["Anti-Bloat Rules", "No raw chat dump", "No unlimited array outputs"]
    missing_ghost_markers, _ = file_contains_all(BODY_GHOST, ghost_markers)
    if missing_ghost_markers:
        errors.append(f"Ghost evolve contract missing anti-bloat markers: {', '.join(missing_ghost_markers)}")

    missing_tui_markers, _ = file_contains_all(TUI_SOURCE, REQUIRED_TUI_PATH_MARKERS)
    if missing_tui_markers:
        errors.append(f"TUI source missing data path markers: {', '.join(missing_tui_markers)}")

    mutation_tokens = detect_mutation_tokens(TUI_SOURCE)
    if mutation_tokens:
        errors.append(f"TUI source contains mutation tokens: {', '.join(mutation_tokens)}")

    json_errors, parsed_json_files = validate_json_targets()
    errors.extend(json_errors)
    if not parsed_json_files:
        warnings.append("No JSON files parsed successfully")

    status = "PASS"
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"

    return {
        "checker_id": "officio_taskpack_acceptance_checker_v0_1",
        "generated_at_utc": utc_now(),
        "status": status,
        "inputs": {
            "taskpack_rules": RULES_TASKPACK.as_posix(),
            "final_response_contract": RULES_RESPONSE.as_posix(),
            "ghost_evolve_contract": BODY_GHOST.as_posix(),
            "tui_source": TUI_SOURCE.as_posix(),
        },
        "required_gates": REQUIRED_GATES,
        "errors": errors,
        "warnings": warnings,
        "parsed_json_files": parsed_json_files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Officio taskpack acceptance and contract links.")
    parser.add_argument("--output", help="Optional output report JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
