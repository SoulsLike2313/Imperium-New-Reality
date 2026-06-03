from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-CAPABILITY-SCOPE-EXPORT-PC-V0_1"
RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}
PACK_VERSION = "0.1"


@dataclass(frozen=True)
class ScopeConfig:
    scope_id: str
    filename: str
    purpose: str
    target_task_types: tuple[str, ...]
    focus_capabilities: tuple[str, ...]
    explicit_forbidden_capabilities: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    required_receipts: tuple[str, ...]
    required_gates: tuple[str, ...]
    warnings: tuple[str, ...]
    examples_of_use: tuple[str, ...]
    future_promotion_candidates: tuple[str, ...]


COMMON_GATES: tuple[str, ...] = (
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
    "GATE-U19-SCRIPT-ARTIFACT-PRESERVATION",
    "GATE-U20-AGENT-KPD-SELF-REVIEW",
    "GATE-U21-COMMAND-CHUNKING",
)


SCOPE_CONFIGS: tuple[ScopeConfig, ...] = (
    ScopeConfig(
        scope_id="code_quality_task",
        filename="scope_code_quality_task_v0_1.json",
        purpose="Python/code-quality checks for Mechanicus and NewGen scripts with strict no-install drift.",
        target_task_types=("code_quality", "python_quality_gate", "script_quality_hardening"),
        focus_capabilities=(
            "CAP-CQ-RUFF",
            "CODE_QUALITY_RUFF",
            "CAP-CQ-PYRIGHT-MYPY",
            "CODE_QUALITY_MYPY",
            "CAP-CQ-PRECOMMIT",
            "CODE_QUALITY_PRE_COMMIT",
            "CODE_QUALITY_PY_COMPILE",
            "CODE_QUALITY_PYTEST",
            "CAP-TOOL-PYTEST",
            "CAP-TOOL-JSONSCHEMA",
            "CODE_QUALITY_JSONSCHEMA",
            "CODE_QUALITY_SCHEMA_FIRST_VALIDATION",
            "CODE_QUALITY_PYRIGHT",
            "CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT",
            "CAP-TOOL-RECEIPT-MODELS-VALIDATORS",
            "TOOLS_RECEIPT_VALIDATOR",
            "CAP-LANG-PYTHON312-RUNTIME",
            "LANGUAGES_PYTHON_312_RUNTIME",
        ),
        explicit_forbidden_capabilities=("CODE_QUALITY_PYRIGHT",),
        forbidden_actions=(
            "pre-commit hook auto-enable",
            "pyright install",
            "global mutation outside task scope",
            "silent package installation",
        ),
        required_receipts=(
            "python_quality_validation_receipt.json",
            "scope_pack_check_report.json",
            "fake_canon_detector_report.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "pre-commit is SANDBOX framework only; never auto-enable hooks in this scope.",
            "CODE_QUALITY_PYRIGHT stays forbidden for execution in this scope.",
        ),
        examples_of_use=(
            "python -m py_compile <script.py>",
            "python -m ruff check IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS",
            "python -m mypy IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_scope_exporter_v0_2.py",
            "python -m pytest <bounded_tests_if_present>",
        ),
        future_promotion_candidates=(
            "CODE_QUALITY_SCHEMA_FIRST_VALIDATION",
            "TOOLS_CANDIDATE_CHECK_WORKFLOW",
        ),
    ),
    ScopeConfig(
        scope_id="json_schema_validation_task",
        filename="scope_json_schema_validation_task_v0_1.json",
        purpose="Schema-first validation of JSON artifacts: cards, receipts, registry, taskpacks, scope exports.",
        target_task_types=("schema_validation", "json_contract_enforcement", "receipt_validation"),
        focus_capabilities=(
            "CAP-TOOL-JSONSCHEMA",
            "CODE_QUALITY_JSONSCHEMA",
            "CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT",
            "CAP-TOOL-RECEIPT-MODELS-VALIDATORS",
            "TOOLS_RECEIPT_VALIDATOR",
            "REFERENCE_CODE_CAPABILITY_CARD_SCHEMA",
            "REFERENCE_CODE_VALIDATION_RECEIPT_SCHEMA",
            "REFERENCE_CODE_SCOPE_EXPORT_SCHEMA",
            "CODE_QUALITY_SCHEMA_FIRST_VALIDATION",
            "REFERENCE_CODE_SAFE_JSON_WRITE_HELPER",
            "CAP-TOOL-PATH-POLICY-INTERNAL",
            "TOOLS_PATH_POLICY",
            "UTILITIES_JQ",
            "UTILITIES_YQ",
        ),
        explicit_forbidden_capabilities=(),
        forbidden_actions=(
            "schema bypass",
            "manual-only JSON trust",
            "fake PASS without schema evidence",
        ),
        required_receipts=(
            "schema_validation_receipt.json",
            "scope_pack_check_report.json",
            "administratum_evidence_map.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Candidate schema references remain context-only until SANDBOX/CANON promotion evidence exists.",
        ),
        examples_of_use=(
            "python -m json.tool <artifact.json>",
            "python -m jsonschema -i <artifact.json> <schema.json>",
        ),
        future_promotion_candidates=(
            "REFERENCE_CODE_SCOPE_EXPORT_SCHEMA",
            "CODE_QUALITY_SCHEMA_FIRST_VALIDATION",
        ),
    ),
    ScopeConfig(
        scope_id="mechanicus_tool_validation_task",
        filename="scope_mechanicus_tool_validation_task_v0_1.json",
        purpose="Validate Arsenal capabilities and produce receipts/status recommendations without fake CANON.",
        target_task_types=("tool_validation", "arsenal_receipt_audit", "registry_sync_check"),
        focus_capabilities=(
            "CAP-TOOL-RECEIPT-MODELS-VALIDATORS",
            "TOOLS_RECEIPT_VALIDATOR",
            "CAP-TOOL-COMMAND-GATEWAY-INTERNAL",
            "TOOLS_COMMAND_GATEWAY",
            "CAP-TOOL-PATH-POLICY-INTERNAL",
            "TOOLS_PATH_POLICY",
            "ALGORITHMS_FAKE_GREEN_DETECTOR",
            "ALGORITHMS_DIFF_CLASSIFIER",
            "ALGORITHMS_EVIDENCE_RANKING",
            "ALGORITHMS_CAPABILITY_PROMOTION_RULES",
            "PLAYBOOKS_CANDIDATE_CHECK_PLAYBOOK",
            "PLAYBOOKS_SCOPE_REVIEW_PLAYBOOK",
            "TOOLS_CANDIDATE_CHECK_WORKFLOW",
            "TOOLS_SCOPE_REVIEW_TOOL",
            "SEARCH_INDEXING_RECEIPT_PATH_INDEX",
            "SEARCH_INDEXING_REPORT_PATH_INDEX",
            "CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE",
            "EXAMPLES_MECHANICUS_TOOL_INTAKE_EXAMPLE",
            "PROMPTING_PATTERNS_NO_FAKE_GREEN_RESPONSE_PATTERN",
        ),
        explicit_forbidden_capabilities=(),
        forbidden_actions=(
            "fake CANON",
            "status changes without receipt",
            "receipt omission for critical validation claim",
        ),
        required_receipts=(
            "validation_receipt.json",
            "capability_status_change_report.json",
            "registry_sync_report.json",
            "fake_canon_detector_report.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Candidate algorithms/workflows are planning-only unless separately validated.",
        ),
        examples_of_use=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_capability_validator_v0_1.py",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py",
        ),
        future_promotion_candidates=(
            "ALGORITHMS_FAKE_GREEN_DETECTOR",
            "TOOLS_SCOPE_REVIEW_TOOL",
        ),
    ),
    ScopeConfig(
        scope_id="controlled_tool_provision_task",
        filename="scope_controlled_tool_provision_task_v0_1.json",
        purpose="Owner-approved detection/install/validation lane with controlled receipts and no silent install.",
        target_task_types=("controlled_provision", "approved_install_lane", "tool_presence_repair"),
        focus_capabilities=(
            "CAP-TOOL-COMMAND-GATEWAY-INTERNAL",
            "TOOLS_COMMAND_GATEWAY",
            "CAP-TOOL-PATH-POLICY-INTERNAL",
            "TOOLS_PATH_POLICY",
            "CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE",
            "PLAYBOOKS_MECHANICUS_TOOL_INTAKE_PLAYBOOK",
            "TOOLS_CANDIDATE_CHECK_WORKFLOW",
            "TOOLS_SCOPE_REVIEW_TOOL",
            "CAP-UTILITY-GIT",
            "TOOLS_GIT",
            "CAP-UTILITY-POWERSHELL",
            "LANGUAGES_POWERSHELL",
            "CAP-LANG-PYTHON312-RUNTIME",
            "LANGUAGES_PYTHON_312_RUNTIME",
            "CAP-TOOL-JSONSCHEMA",
            "CAP-CQ-RUFF",
            "CAP-CQ-PYRIGHT-MYPY",
            "CAP-CQ-PRECOMMIT",
            "PROMPTING_PATTERNS_OWNER_DECISION_QUEUE_PROMPT",
        ),
        explicit_forbidden_capabilities=(),
        forbidden_actions=(
            "silent install",
            "network provisioning without Owner approval",
            "pre-commit hooks auto-enable",
            "unapproved package provisioning",
        ),
        required_receipts=(
            "tool_detection_report.json",
            "controlled_provision_results.json",
            "install_receipts_index.json",
            "validation_receipts_index.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Provisioning scope is constrained to explicit Owner-approved list only.",
        ),
        examples_of_use=(
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_controlled_provision_runner_v0_1.py",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_install_receipt_builder_v0_1.py",
        ),
        future_promotion_candidates=("PLAYBOOKS_MECHANICUS_TOOL_INTAKE_PLAYBOOK",),
    ),
    ScopeConfig(
        scope_id="repo_hygiene_task",
        filename="scope_repo_hygiene_task_v0_1.json",
        purpose="NewGen-scoped hygiene checks: dirty-tree/runtime-junk/fake-green under Inquisition oversight.",
        target_task_types=("repo_hygiene", "inquisition_cleanliness_audit", "runtime_junk_scan"),
        focus_capabilities=(
            "ALGORITHMS_DIRTY_TREE_CLASSIFIER",
            "ALGORITHMS_RUNTIME_JUNK_CLASSIFIER",
            "ALGORITHMS_DIFF_CLASSIFIER",
            "ALGORITHMS_FAKE_GREEN_DETECTOR",
            "PLAYBOOKS_CLEAN_WORKTREE_PLAYBOOK",
            "PLAYBOOKS_INQUISITION_HYGIENE_PLAYBOOK",
            "PLAYBOOKS_NO_RUNTIME_JUNK_PLAYBOOK",
            "PLAYBOOKS_COMMIT_PUSH_GATE_PLAYBOOK",
            "TOOLS_COMMIT_PUSH_WORKFLOW",
            "EXAMPLES_INQUISITION_HYGIENE_SCAN_EXAMPLE",
            "CAP-UTILITY-GIT",
            "TOOLS_GIT",
            "CAP-UTILITY-POWERSHELL",
            "LANGUAGES_POWERSHELL",
            "CAP-TOOL-PATH-POLICY-INTERNAL",
            "TOOLS_PATH_POLICY",
            "SEARCH_INDEXING_REPORT_PATH_INDEX",
            "SEARCH_INDEXING_RECEIPT_PATH_INDEX",
        ),
        explicit_forbidden_capabilities=(),
        forbidden_actions=(
            "broad full repo cleanup",
            "unreviewed deletion",
            "runtime-junk cleanup without evidence receipt",
        ),
        required_receipts=(
            "inquisition_cleanliness_report.json",
            "fake_canon_detector_report.json",
            "scope_pack_check_report.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Hygiene work must stay bounded to declared scope and touched paths.",
        ),
        examples_of_use=(
            "git status --short",
            "git diff --name-status",
            "python IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py",
        ),
        future_promotion_candidates=(
            "ALGORITHMS_DIRTY_TREE_CLASSIFIER",
            "PLAYBOOKS_INQUISITION_HYGIENE_PLAYBOOK",
        ),
    ),
    ScopeConfig(
        scope_id="taskpack_generation_task",
        filename="scope_taskpack_generation_task_v0_1.json",
        purpose="Structured ZIP dossier/taskpack generation with read-first/language/gate contracts and closure receipts.",
        target_task_types=("taskpack_generation", "zip_dossier_build", "gatepack_assembly"),
        focus_capabilities=(
            "TOOLS_TASKPACK_DOSSIER_BUILDER",
            "EXAMPLES_TASKPACK_EXAMPLE",
            "PROMPTING_PATTERNS_STRUCTURED_ZIP_DOSSIER_PROMPT",
            "PROMPTING_PATTERNS_READ_FIRST_GATE_PROMPT",
            "PROMPTING_PATTERNS_4_PART_OWNER_REPORT_PROMPT",
            "PROMPTING_PATTERNS_OWNER_DECISION_QUEUE_PROMPT",
            "PROMPTING_PATTERNS_TASK_CONTINUATION_PROMPT",
            "PROMPTING_PATTERNS_VOLUME_BUDGET_PROMPT",
            "UTILITIES_7_ZIP",
            "UTILITIES_ARCHIVE_MANIFEST_GENERATOR",
            "UTILITIES_SHA256_HASHING",
            "PLAYBOOKS_COMMIT_PUSH_GATE_PLAYBOOK",
            "TOOLS_COMMIT_PUSH_WORKFLOW",
            "CAP-TOOL-RECEIPT-MODELS-VALIDATORS",
            "TOOLS_RECEIPT_VALIDATOR",
            "REFERENCE_CODE_OWNER_QUESTION_SCHEMA",
            "REFERENCE_CODE_VALIDATION_RECEIPT_SCHEMA",
        ),
        explicit_forbidden_capabilities=(),
        forbidden_actions=(
            "chat-only prompts when dossier required",
            "missing acceptance gates",
            "taskpack without closure receipt",
        ),
        required_receipts=(
            "taskpack_manifest.json",
            "closure_receipt.json",
            "scope_pack_check_report.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Taskpack generation must keep machine artifacts UTF-8 safe and owner summaries RU-ready.",
        ),
        examples_of_use=(
            "Build dossier files: TASK.md + TASK.json + ACCEPTANCE_GATES.md + templates",
            "Attach _MANIFEST.json and hash ZIP before handoff",
        ),
        future_promotion_candidates=(
            "TOOLS_TASKPACK_DOSSIER_BUILDER",
            "UTILITIES_ARCHIVE_MANIFEST_GENERATOR",
        ),
    ),
    ScopeConfig(
        scope_id="visual_readiness_task",
        filename="scope_visual_readiness_task_v0_1.json",
        purpose="Visual readiness only: detect/defer prerequisites and contracts without prototype creation.",
        target_task_types=("visual_readiness", "visual_preflight", "runtime_visual_gate_precheck"),
        focus_capabilities=(
            "CAP-TOOL-NODE-NPM-NPX",
            "CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE",
            "VISUAL_TESTING_VISUAL_LAYOUT_CONTRACT",
            "VISUAL_TESTING_SCREENSHOT_BASELINE_PRACTICE",
            "VISUAL_TESTING_SCREENSHOT_MANIFEST",
            "VISUAL_TESTING_PLAYWRIGHT",
            "CAP-VIS-PLAYWRIGHT-REGRESSION",
            "VISUAL_TESTING_RESPONSIVE_VIEWPORT_CHECKLIST",
            "VISUAL_TESTING_STATIC_HTML_VISUAL_CHECK",
            "VISUAL_TESTING_VISUAL_EVIDENCE_REPORT",
            "EXAMPLES_VISUAL_GATE_EXAMPLE",
            "UI_FRAMEWORKS_REACT",
            "UI_FRAMEWORKS_VITE",
            "UI_FRAMEWORKS_PLAIN_HTML_CSS_JS_COCKPIT",
            "LANGUAGES_HTML_CSS",
            "LANGUAGES_JAVASCRIPT",
            "LANGUAGES_TYPESCRIPT",
        ),
        explicit_forbidden_capabilities=("UI_FRAMEWORKS_REACT", "UI_FRAMEWORKS_VITE"),
        forbidden_actions=(
            "React/Vite project creation",
            "Playwright browser install",
            "visual prototype comparison",
            "LLM/cloud activation",
        ),
        required_receipts=(
            "scope_pack_check_report.json",
            "inquisition_cleanliness_report.json",
            "forbidden_capability_guard_report.json",
        ),
        required_gates=COMMON_GATES,
        warnings=(
            "Playwright capability may be detected but remains deferred for this scope.",
            "Visual readiness does not authorize runtime prototype execution.",
        ),
        examples_of_use=(
            "Check Node/npm/npx presence and document status only",
            "Review visual contracts/perf budget without launching prototypes",
        ),
        future_promotion_candidates=(
            "VISUAL_TESTING_VISUAL_LAYOUT_CONTRACT",
            "VISUAL_TESTING_SCREENSHOT_BASELINE_PRACTICE",
        ),
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path_hint,
            text=True,
        ).strip()
        if root:
            return Path(root)
    except Exception:
        pass
    return path_hint


def get_subject_implementation_ref(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "@"], cwd=repo_root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def build_pack(
    *,
    config: ScopeConfig,
    cards_by_id: dict[str, dict[str, Any]],
    usage_by_id: dict[str, dict[str, Any]],
    common_owner_decision_ids: set[str],
    generated_at: str,
    source_registry: str,
    subject_implementation_ref: str,
) -> tuple[dict[str, Any], list[str]]:
    canon_allowed: set[str] = set()
    sandbox_allowed: set[str] = set()
    candidate_context_only: set[str] = set()
    owner_decision_required: set[str] = set(common_owner_decision_ids)
    forbidden: set[str] = set(config.explicit_forbidden_capabilities)
    missing_focus: list[str] = []

    aggregated_receipts: set[str] = set(config.required_receipts)
    for capability_id in config.focus_capabilities:
        card = cards_by_id.get(capability_id)
        if not card:
            missing_focus.append(capability_id)
            continue
        status = str(card.get("status", "")).strip()
        category = str(card.get("category", "")).strip()
        if capability_id in config.explicit_forbidden_capabilities:
            forbidden.add(capability_id)
        elif status in {"QUARANTINE", "REJECTED"}:
            forbidden.add(capability_id)
        elif category in RESERVED_CATEGORIES or bool(card.get("reserved")):
            owner_decision_required.add(capability_id)
        elif status == "CANON":
            canon_allowed.add(capability_id)
        elif status == "SANDBOX":
            sandbox_allowed.add(capability_id)
        else:
            candidate_context_only.add(capability_id)

        usage_entry = usage_by_id.get(capability_id, {})
        raw_receipts = usage_entry.get("required_receipts", [])
        if isinstance(raw_receipts, list):
            for item in raw_receipts:
                value = str(item).strip()
                if value:
                    aggregated_receipts.add(value)

    warnings = list(config.warnings)
    if missing_focus:
        warnings.append(
            "Some focus capabilities are missing in registry and were not exported: "
            + ", ".join(sorted(missing_focus))
        )

    pack = {
        "scope_id": config.scope_id,
        "version": PACK_VERSION,
        "generated_at_utc": generated_at,
        "source_registry": source_registry,
        "purpose": config.purpose,
        "target_task_types": list(config.target_task_types),
        "canon_allowed": sorted(canon_allowed),
        "sandbox_allowed": sorted(sandbox_allowed),
        "candidate_context_only": sorted(candidate_context_only),
        "owner_decision_required": sorted(owner_decision_required),
        "forbidden": sorted(forbidden),
        "required_receipts": sorted(aggregated_receipts),
        "required_gates": list(config.required_gates),
        "warnings": warnings,
        "examples_of_use": list(config.examples_of_use),
        "future_promotion_candidates": list(config.future_promotion_candidates),
        "forbidden_actions": list(config.forbidden_actions),
        "last_generated_from_commit": subject_implementation_ref,
        "receipt_subject_head": subject_implementation_ref,
        "receipt_content_head": "PENDING_COMMIT",
        "external_delivery_head": "PENDING_PUSH",
        "remote_head_after_push": "PENDING_PUSH",
        "self_head_paradox_handled": True,
        "clean_pass_allowed": False,
        "caps_triggered": ["CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"],
    }
    return pack, missing_focus


def build_schema_payload() -> dict[str, Any]:
    array_of_strings = {"type": "array", "items": {"type": "string"}, "uniqueItems": True}
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Mechanicus Capability Scope Pack V0.1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "scope_id",
            "version",
            "generated_at_utc",
            "source_registry",
            "purpose",
            "target_task_types",
            "canon_allowed",
            "sandbox_allowed",
            "candidate_context_only",
            "owner_decision_required",
            "forbidden",
            "required_receipts",
            "required_gates",
            "warnings",
            "examples_of_use",
            "future_promotion_candidates",
            "forbidden_actions",
            "last_generated_from_commit",
            "receipt_subject_head",
            "receipt_content_head",
            "external_delivery_head",
            "remote_head_after_push",
            "self_head_paradox_handled",
            "clean_pass_allowed",
            "caps_triggered",
        ],
        "properties": {
            "scope_id": {"type": "string"},
            "version": {"type": "string"},
            "generated_at_utc": {"type": "string"},
            "source_registry": {"type": "string"},
            "purpose": {"type": "string"},
            "target_task_types": array_of_strings,
            "canon_allowed": array_of_strings,
            "sandbox_allowed": array_of_strings,
            "candidate_context_only": array_of_strings,
            "owner_decision_required": array_of_strings,
            "forbidden": array_of_strings,
            "required_receipts": array_of_strings,
            "required_gates": array_of_strings,
            "warnings": array_of_strings,
            "examples_of_use": array_of_strings,
            "future_promotion_candidates": array_of_strings,
            "forbidden_actions": array_of_strings,
            "last_generated_from_commit": {"type": "string"},
            "receipt_subject_head": {"type": "string"},
            "receipt_content_head": {"type": "string"},
            "external_delivery_head": {"type": "string"},
            "remote_head_after_push": {"type": "string"},
            "self_head_paradox_handled": {"type": "boolean"},
            "clean_pass_allowed": {"type": "boolean"},
            "caps_triggered": array_of_strings,
        },
    }


def write_index_ru(index_path: Path, summaries: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# Mechanicus Scope Packs Index RU (V0.1)")
    lines.append("")
    lines.append("Назначение: быстрый доступ будущего Servitor/local-agent к разрешенным capability-срезам по типам задач.")
    lines.append("")
    lines.append("| Scope ID | Файл | CANON | SANDBOX | CANDIDATE | OWNER_DECISION | FORBIDDEN |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for row in summaries:
        lines.append(
            "| {scope_id} | {filename} | {canon} | {sandbox} | {candidate} | {owner} | {forbidden} |".format(
                scope_id=row["scope_id"],
                filename=row["filename"],
                canon=row["canon_allowed_count"],
                sandbox=row["sandbox_allowed_count"],
                candidate=row["candidate_context_only_count"],
                owner=row["owner_decision_required_count"],
                forbidden=row["forbidden_count"],
            )
        )
    lines.append("")
    lines.append("## Важные правила")
    lines.append("- `visual_readiness_task` = только readiness; без запуска визуальных прототипов.")
    lines.append("- `controlled_tool_provision_task` = только Owner-approved install lane; silent install запрещен.")
    lines.append("- Во всех scope действует запрет на LLM/cloud activation без отдельного Owner gate.")
    lines.append("")
    lines.append("## Как применять")
    lines.append("1. Определи тип задачи.")
    lines.append("2. Открой соответствующий scope pack.")
    lines.append("3. Используй только `canon_allowed`/`sandbox_allowed` по условиям gates/receipts.")
    lines.append("4. `candidate_context_only` — для планирования, не для исполнения.")
    lines.append("5. Проверь `forbidden_actions` до запуска команд.")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate task-scoped Mechanicus capability packs (v0.2 exporter).")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--registry",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
    )
    parser.add_argument(
        "--usage-map",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/FIELD_GUIDES/BATCH_001/ARSENAL_AGENT_USAGE_MAP_BATCH_001.json",
    )
    parser.add_argument(
        "--output-root",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1",
    )
    parser.add_argument(
        "--schema-file",
        default="scope_pack_schema_v0_1.json",
        help="File name or absolute path for schema output.",
    )
    parser.add_argument(
        "--index-file",
        default="SCOPE_PACKS_INDEX_RU.md",
        help="File name or absolute path for RU index output.",
    )
    parser.add_argument(
        "--manifest-file",
        default="scope_pack_generation_manifest.json",
        help="File name or absolute path for generation manifest output.",
    )
    args = parser.parse_args()

    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    registry_path = (repo_root / args.registry).resolve()
    usage_map_path = (repo_root / args.usage_map).resolve()
    output_root = (repo_root / args.output_root).resolve()

    schema_path = Path(args.schema_file)
    if not schema_path.is_absolute():
        schema_path = output_root / schema_path
    index_path = Path(args.index_file)
    if not index_path.is_absolute():
        index_path = output_root / index_path
    manifest_path = Path(args.manifest_file)
    if not manifest_path.is_absolute():
        manifest_path = output_root / manifest_path

    registry_payload = read_json(registry_path)
    cards = registry_payload.get("cards", [])
    if not isinstance(cards, list):
        raise RuntimeError("Registry cards must be a list.")

    cards_by_id: dict[str, dict[str, Any]] = {}
    for raw in cards:
        if not isinstance(raw, dict):
            continue
        capability_id = str(raw.get("capability_id", "")).strip()
        if capability_id:
            cards_by_id[capability_id] = raw

    usage_by_id: dict[str, dict[str, Any]] = {}
    if usage_map_path.exists():
        usage_payload = read_json(usage_map_path)
        entries = usage_payload.get("entries", [])
        if isinstance(entries, list):
            for item in entries:
                if not isinstance(item, dict):
                    continue
                capability_id = str(item.get("capability_id", "")).strip()
                if capability_id:
                    usage_by_id[capability_id] = item

    common_owner_decision_ids = {
        capability_id
        for capability_id, card in cards_by_id.items()
        if str(card.get("category", "")).strip() in RESERVED_CATEGORIES or bool(card.get("reserved"))
    }

    generated_at = utc_now()
    subject_implementation_ref = get_subject_implementation_ref(repo_root)
    source_registry_rel = registry_path.relative_to(repo_root).as_posix()

    output_root.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    missing_focus_by_scope: dict[str, list[str]] = {}

    for config in SCOPE_CONFIGS:
        pack, missing_focus = build_pack(
            config=config,
            cards_by_id=cards_by_id,
            usage_by_id=usage_by_id,
            common_owner_decision_ids=common_owner_decision_ids,
            generated_at=generated_at,
            source_registry=source_registry_rel,
            subject_implementation_ref=subject_implementation_ref,
        )
        output_path = output_root / config.filename
        write_json(output_path, pack)

        summaries.append(
            {
                "scope_id": config.scope_id,
                "filename": config.filename,
                "path": output_path.relative_to(repo_root).as_posix(),
                "canon_allowed_count": len(pack["canon_allowed"]),
                "sandbox_allowed_count": len(pack["sandbox_allowed"]),
                "candidate_context_only_count": len(pack["candidate_context_only"]),
                "owner_decision_required_count": len(pack["owner_decision_required"]),
                "forbidden_count": len(pack["forbidden"]),
            }
        )
        missing_focus_by_scope[config.scope_id] = sorted(missing_focus)

    schema_payload = build_schema_payload()
    write_json(schema_path, schema_payload)
    write_index_ru(index_path, summaries)

    manifest = {
        "task_id": args.task_id,
        "generated_at_utc": generated_at,
        "exporter": "mechanicus_capability_scope_exporter_v0_2.py",
        "repo_root": str(repo_root),
        "source_registry": source_registry_rel,
        "source_usage_map": usage_map_path.relative_to(repo_root).as_posix() if usage_map_path.exists() else "",
        "output_root": output_root.relative_to(repo_root).as_posix(),
        "scope_pack_schema": schema_path.relative_to(repo_root).as_posix(),
        "scope_pack_index_ru": index_path.relative_to(repo_root).as_posix(),
        "scope_pack_count": len(SCOPE_CONFIGS),
        "scope_packs": summaries,
        "missing_focus_capabilities_by_scope": missing_focus_by_scope,
        "reserved_owner_decision_capabilities": sorted(common_owner_decision_ids),
        "last_generated_from_commit": subject_implementation_ref,
        "receipt_subject_head": subject_implementation_ref,
        "receipt_content_head": "PENDING_COMMIT",
        "external_delivery_head": "PENDING_PUSH",
        "remote_head_after_push": "PENDING_PUSH",
        "self_head_paradox_handled": True,
        "clean_pass_allowed": False,
        "caps_triggered": ["CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"],
    }
    write_json(manifest_path, manifest)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "generated_scope_packs": len(SCOPE_CONFIGS),
                "manifest": manifest_path.relative_to(repo_root).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
