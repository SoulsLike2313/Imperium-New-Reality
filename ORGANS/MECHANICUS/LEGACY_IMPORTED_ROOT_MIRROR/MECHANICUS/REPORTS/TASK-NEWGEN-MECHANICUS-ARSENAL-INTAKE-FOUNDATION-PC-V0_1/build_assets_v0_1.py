from __future__ import annotations

import json
from pathlib import Path


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1"
STARTING_HEAD = "c818551ca53a24a9fb658d45246456442eb8bd0c"
NOW_UTC = "2026-05-24T00:00:00Z"


def as_pretty_json(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    arsenal_root = repo_root / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "ARSENAL"
    report_root = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "MECHANICUS"
        / "REPORTS"
        / TASK_ID
    )

    categories = [
        "LANGUAGES",
        "TOOLS",
        "UTILITIES",
        "UI_FRAMEWORKS",
        "DATABASES",
        "SEARCH_INDEXING",
        "VISUAL_TESTING",
        "CODE_QUALITY",
        "LOCAL_LLM",
        "CLOUD_LLM_ADAPTERS",
        "PROMPTING_PATTERNS",
        "ALGORITHMS",
        "REFERENCE_CODE",
        "EXAMPLES",
        "PLAYBOOKS",
    ]

    category_descriptions = {
        "LANGUAGES": "Runtimes and programming language baselines.",
        "TOOLS": "Executable tools and CLIs.",
        "UTILITIES": "System and workflow utility capabilities.",
        "UI_FRAMEWORKS": "UI stacks and component frameworks.",
        "DATABASES": "Databases and storage engines.",
        "SEARCH_INDEXING": "Search and indexing capabilities.",
        "VISUAL_TESTING": "Visual capture and regression testing capabilities.",
        "CODE_QUALITY": "Linting, type checking, and quality gates.",
        "LOCAL_LLM": "Local model runtime capabilities.",
        "CLOUD_LLM_ADAPTERS": "Cloud API adapter capabilities.",
        "PROMPTING_PATTERNS": "Prompting templates and operator patterns.",
        "ALGORITHMS": "Reusable algorithmic techniques.",
        "REFERENCE_CODE": "Internal reusable source modules and patterns.",
        "EXAMPLES": "Reference examples and starter patterns.",
        "PLAYBOOKS": "Operational practices and procedures.",
    }

    required_card_fields = [
        "capability_id",
        "name",
        "category",
        "status",
        "owner_organ",
        "purpose",
        "what_problem_it_solves",
        "source_type",
        "source_url_or_path",
        "license_or_trust_note",
        "install_required",
        "install_gate",
        "validation_commands",
        "expected_receipts",
        "safety_notes",
        "security_notes",
        "offline_or_network_dependency",
        "promoted_by_receipt",
        "last_reviewed_utc",
        "next_review_reason",
        "limitations",
        "allowed_use_cases",
        "forbidden_use_cases",
    ]

    raw_cards = [
        {
            "capability_id": "CAP-LANG-PYTHON312-RUNTIME",
            "name": "Python 3.12 runtime",
            "category": "LANGUAGES",
            "status": "SANDBOX",
            "source_type": "external_tool",
            "source_url_or_path": "python --version",
            "install_required": False,
            "install_gate": "GATE-ARSENAL-HOST-RUNTIME-VERIFY",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Default runtime for NewGen scripts and validators.",
            "problem": "Reduces scripting baseline drift across tasks.",
            "next_review_reason": "Needs cross-host runtime receipts before CANON.",
            "limitations": "Version drift remains possible across hosts.",
        },
        {
            "capability_id": "CAP-TOOL-PYTEST",
            "name": "pytest",
            "category": "TOOLS",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "https://docs.pytest.org/",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Python regression test runner.",
            "problem": "Automates repeatable behavioral checks.",
            "next_review_reason": "Requires install and validation receipts.",
            "limitations": "Not admitted as available in this foundation task.",
        },
        {
            "capability_id": "CAP-TOOL-JSONSCHEMA",
            "name": "jsonschema",
            "category": "TOOLS",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "https://python-jsonschema.readthedocs.io/",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Schema-based JSON contract validator.",
            "problem": "Prevents malformed contract/receipt artifacts.",
            "next_review_reason": "Requires host-level install and probe receipts.",
            "limitations": "Cannot be treated as admitted without evidence.",
        },
        {
            "capability_id": "CAP-UTILITY-GIT",
            "name": "git",
            "category": "UTILITIES",
            "status": "SANDBOX",
            "source_type": "built_in",
            "source_url_or_path": "git --version",
            "install_required": False,
            "install_gate": "GATE-U00-GIT-TRUTH",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Repository truth checks and version traceability.",
            "problem": "Supports clean-state and head-verification gates.",
            "next_review_reason": "Needs host policy mapping for broader CANON promotion.",
            "limitations": "Unsafe operations remain possible without discipline.",
        },
        {
            "capability_id": "CAP-UTILITY-POWERSHELL",
            "name": "PowerShell",
            "category": "UTILITIES",
            "status": "SANDBOX",
            "source_type": "built_in",
            "source_url_or_path": "$PSVersionTable.PSVersion",
            "install_required": False,
            "install_gate": "GATE-U21-COMMAND-CHUNKING",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Primary PC executor for bounded automation.",
            "problem": "Provides deterministic command orchestration.",
            "next_review_reason": "Needs command deny-list maturity for CANON.",
            "limitations": "Host permissions can expose risky operations.",
        },
        {
            "capability_id": "CAP-REF-PATHLIB-DISCIPLINE",
            "name": "pathlib / stdlib file operations discipline",
            "category": "REFERENCE_CODE",
            "status": "SANDBOX",
            "source_type": "practice",
            "source_url_or_path": "src/imperium/security/path_policy.py",
            "install_required": False,
            "install_gate": "GATE-U13-PYTHON-TYPE-SAFETY",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Safe stdlib path handling discipline.",
            "problem": "Reduces shell-fragile path mutation logic.",
            "next_review_reason": "Requires cross-module conformance audit.",
            "limitations": "Current evidence is partial and module-centric.",
        },
        {
            "capability_id": "CAP-DB-SQLITE-FTS5-EVIDENCE",
            "name": "SQLite / FTS5 evidence index candidate",
            "category": "DATABASES",
            "status": "CANDIDATE",
            "source_type": "database",
            "source_url_or_path": "sqlite3 --version",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-DB-ADMISSION",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate local evidence indexing substrate.",
            "problem": "Could support searchable receipt/report corpus.",
            "next_review_reason": "Requires admission, schema design, and receipts.",
            "limitations": "No provisioning or validation in this task.",
        },
        {
            "capability_id": "CAP-VIS-PLAYWRIGHT-REGRESSION",
            "name": "Playwright visual regression candidate",
            "category": "VISUAL_TESTING",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "npx playwright --version",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-VISUAL-TOOL-ADMISSION",
            "dependency": "network_optional",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate visual capture/regression lane.",
            "problem": "Would standardize screenshot evidence automation.",
            "next_review_reason": "Requires explicit admission and install receipts.",
            "limitations": "No local validation in foundation scope.",
        },
        {
            "capability_id": "CAP-TOOL-NODE-NPM-NPX",
            "name": "Node/npm/npx candidate",
            "category": "TOOLS",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "node --version && npm --version && npx --version",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION",
            "dependency": "network_optional",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate JS runtime/toolchain lane.",
            "problem": "Supports future visual/test ecosystem dependencies.",
            "next_review_reason": "Requires controlled provisioning receipts.",
            "limitations": "No package-management trust claim allowed yet.",
        },
        {
            "capability_id": "CAP-CQ-RUFF",
            "name": "Ruff candidate",
            "category": "CODE_QUALITY",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "ruff --version",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate Python lint/format accelerator.",
            "problem": "Could speed quality checks in bounded pipelines.",
            "next_review_reason": "Needs admitted rule profile and install receipts.",
            "limitations": "No canonical lint baseline approved yet.",
        },
        {
            "capability_id": "CAP-CQ-PRECOMMIT",
            "name": "pre-commit candidate",
            "category": "CODE_QUALITY",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "pre-commit --version",
            "install_required": True,
            "install_gate": "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION",
            "dependency": "network_optional",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate commit-time hook enforcement.",
            "problem": "Could prevent avoidable hygiene regressions.",
            "next_review_reason": "Requires controlled hook catalog and receipts.",
            "limitations": "No mandatory hook policy admitted.",
        },
        {
            "capability_id": "CAP-CQ-PYRIGHT-MYPY",
            "name": "pyright or mypy type safety candidate",
            "category": "CODE_QUALITY",
            "status": "CANDIDATE",
            "source_type": "external_tool",
            "source_url_or_path": "pyright --version || mypy --version",
            "install_required": True,
            "install_gate": "GATE-U13-PYTHON-TYPE-SAFETY",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Candidate static type-check lane.",
            "problem": "Could detect interface/type drift earlier.",
            "next_review_reason": "Needs tool selection and config admission.",
            "limitations": "No validated type profile in this task.",
        },
        {
            "capability_id": "CAP-TOOL-COMMAND-GATEWAY-INTERNAL",
            "name": "command_gateway internal capability",
            "category": "TOOLS",
            "status": "CANON",
            "source_type": "repo_existing",
            "source_url_or_path": "src/imperium/security/command_gateway.py",
            "install_required": False,
            "install_gate": "GATE-U09-NO-FAKE-GREEN",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "REPO_EVIDENCE_PATHS",
            "canon_evidence_paths": [
                "src/imperium/security/command_gateway.py",
                "src/imperium/security/__init__.py",
            ],
            "purpose": "Allowlisted command execution with verdict receipt shape.",
            "problem": "Constrains arbitrary command execution and captures evidence.",
            "next_review_reason": "Needs periodic allowlist and exception-path audits.",
            "limitations": "Policy quality depends on maintained allowlist boundaries.",
        },
        {
            "capability_id": "CAP-TOOL-PATH-POLICY-INTERNAL",
            "name": "path_policy internal capability",
            "category": "TOOLS",
            "status": "CANON",
            "source_type": "repo_existing",
            "source_url_or_path": "src/imperium/security/path_policy.py",
            "install_required": False,
            "install_gate": "GATE-U02-SCOPE-BOUNDARY",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "REPO_EVIDENCE_PATHS",
            "canon_evidence_paths": [
                "src/imperium/security/path_policy.py",
                "src/imperium/security/__init__.py",
            ],
            "purpose": "Root-bounded path safety enforcement.",
            "problem": "Prevents out-of-scope path traversal and root escape.",
            "next_review_reason": "Requires verification whenever repo layout changes.",
            "limitations": "Callers must use policy functions consistently.",
        },
        {
            "capability_id": "CAP-TOOL-RECEIPT-MODELS-VALIDATORS",
            "name": "receipt models / validators internal capability",
            "category": "TOOLS",
            "status": "CANON",
            "source_type": "repo_existing",
            "source_url_or_path": "src/imperium/receipts/model.py",
            "install_required": False,
            "install_gate": "GATE-U04-EVIDENCE-RECEIPT",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "REPO_EVIDENCE_PATHS",
            "canon_evidence_paths": [
                "src/imperium/receipts/model.py",
                "src/imperium/receipts/validator.py",
                "src/imperium/receipts/__init__.py",
            ],
            "purpose": "Structured receipt model and validator helpers.",
            "problem": "Normalizes PASS/WARN/FAIL/BLOCKED evidence semantics.",
            "next_review_reason": "Review on schema and verdict model evolution.",
            "limitations": "Validator quality depends on contract coverage.",
        },
        {
            "capability_id": "CAP-EXAMPLE-LOCAL-HTTP-DASHBOARD-SERVER",
            "name": "local HTTP dashboard server pattern",
            "category": "EXAMPLES",
            "status": "SANDBOX",
            "source_type": "practice",
            "source_url_or_path": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1/important_six_dashboard_api_smoke_report.json",
            "install_required": False,
            "install_gate": "GATE-U15-OPERATIONALITY-IMPACT",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Bounded local server pattern for dashboard smoke checks.",
            "problem": "Supports repeatable local evidence capture loops.",
            "next_review_reason": "Needs hardened exposure policy before CANON.",
            "limitations": "Pattern is local-only and scenario-specific.",
        },
        {
            "capability_id": "CAP-PLAYBOOK-VISUAL-SCREENSHOT-GATE",
            "name": "visual screenshot gate practice",
            "category": "PLAYBOOKS",
            "status": "SANDBOX",
            "source_type": "practice",
            "source_url_or_path": "IMPERIUM_NEW_GENERATION/COMMON_AGENT_CLI/evidence_policy_for_cli.json",
            "install_required": False,
            "install_gate": "GATE-U09-NO-FAKE-GREEN",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Link visual verdicts to screenshot/report evidence.",
            "problem": "Lowers fake-green risk in visual acceptance flows.",
            "next_review_reason": "Needs broader cross-organ compliance audit.",
            "limitations": "Current evidence is not full-repo coverage.",
        },
        {
            "capability_id": "CAP-PLAYBOOK-SCHEMA-FIRST-CONTRACT",
            "name": "schema-first JSON contract practice",
            "category": "PLAYBOOKS",
            "status": "CANON",
            "source_type": "practice",
            "source_url_or_path": "IMPERIUM_NEW_GENERATION/CONTRACTS",
            "install_required": False,
            "install_gate": "GATE-U09-NO-FAKE-GREEN",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "REPO_EVIDENCE_PATHS",
            "canon_evidence_paths": [
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json",
            ],
            "purpose": "Schema-first rule for critical JSON artifacts.",
            "problem": "Prevents malformed contracts and report drift.",
            "next_review_reason": "Review when contract families evolve.",
            "limitations": "Coverage quality depends on maintained schema scope.",
        },
        {
            "capability_id": "CAP-PLAYBOOK-MECHANICUS-ARSENAL-INTAKE",
            "name": "Mechanicus Arsenal card intake practice",
            "category": "PLAYBOOKS",
            "status": "SANDBOX",
            "source_type": "practice",
            "source_url_or_path": "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/ARSENAL_INTAKE_PROTOCOL_V0_1.md",
            "install_required": False,
            "install_gate": "GATE-ARSENAL-INTAKE-COMPLIANCE",
            "dependency": "offline_preferred",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Controlled intake and triage workflow for capabilities.",
            "problem": "Prevents unregistered tool adoption and trust drift.",
            "next_review_reason": "Needs follow-up promotion cycle evidence.",
            "limitations": "Foundation-only until additional receipts accumulate.",
        },
        {
            "capability_id": "CAP-PLAYBOOK-OSINT-DEEP-RESEARCH",
            "name": "OSINT/deep research practice candidate",
            "category": "PLAYBOOKS",
            "status": "CANDIDATE",
            "source_type": "practice",
            "source_url_or_path": "No implementation in this task",
            "install_required": False,
            "install_gate": "GATE-ARSENAL-RESEARCH-POLICY",
            "dependency": "network_required",
            "promoted_by_receipt": "NOT_PROMOTED",
            "purpose": "Future controlled research playbook candidate.",
            "problem": "Could support strategic discovery workflows.",
            "next_review_reason": "Requires legal/privacy and scope policy.",
            "limitations": "No scraping/automation admitted in foundation scope.",
        },
    ]

    cards: list[dict[str, object]] = []
    for raw in raw_cards:
        cap_id = str(raw["capability_id"])
        status = str(raw["status"])
        card = {
            "capability_id": cap_id,
            "name": raw["name"],
            "category": raw["category"],
            "status": status,
            "owner_organ": "MECHANICUS",
            "purpose": raw["purpose"],
            "what_problem_it_solves": raw["problem"],
            "source_type": raw["source_type"],
            "source_url_or_path": raw["source_url_or_path"],
            "license_or_trust_note": (
                "Internal repo evidence controlled by IMPERIUM."
                if raw["source_type"] in {"repo_existing", "practice"} and "IMPERIUM_NEW_GENERATION" in str(raw["source_url_or_path"])
                else "Host/external trust requires explicit admission receipts."
            ),
            "install_required": raw["install_required"],
            "install_gate": raw["install_gate"],
            "validation_commands": [f"validate:{cap_id.lower()}"],
            "expected_receipts": [f"{cap_id.lower()}_receipt.json"],
            "safety_notes": "Use only in bounded task scope; no blind runtime mutation.",
            "security_notes": "Do not bypass path, command, and evidence gates.",
            "offline_or_network_dependency": raw["dependency"],
            "promoted_by_receipt": raw["promoted_by_receipt"],
            "last_reviewed_utc": NOW_UTC,
            "next_review_reason": raw["next_review_reason"],
            "limitations": raw["limitations"],
            "allowed_use_cases": [
                "Bounded task execution under Mechanicus policy",
                "Evidence-backed validation and report generation",
            ],
            "forbidden_use_cases": [
                "Production-ready claim without receipts",
                "Out-of-scope or unbounded execution",
            ],
        }
        if "canon_evidence_paths" in raw:
            card["canon_evidence_paths"] = raw["canon_evidence_paths"]
        cards.append(card)

    for card in cards:
        card_path = (
            arsenal_root
            / "CATEGORIES"
            / str(card["category"])
            / f"{card['capability_id']}.json"
        )
        card_path.write_text(as_pretty_json(card), encoding="utf-8")

    status_counts = {key: 0 for key in ["CANDIDATE", "SANDBOX", "CANON", "QUARANTINE", "REJECTED"]}
    for card in cards:
        status_counts[str(card["status"])] += 1

    category_registry = {
        "schema_version": "arsenal.category_registry.v0_1",
        "generated_at_utc": NOW_UTC,
        "root": "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES",
        "categories": [
            {
                "category": cat,
                "path": f"IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/{cat}",
                "description": category_descriptions[cat],
                "active": True,
            }
            for cat in categories
        ],
    }
    (arsenal_root / "REGISTRY" / "category_registry_v0_1.json").write_text(
        as_pretty_json(category_registry), encoding="utf-8"
    )

    intake_queue = {
        "schema_version": "arsenal.intake_queue.v0_1",
        "generated_at_utc": NOW_UTC,
        "queue": [
            {
                "capability_id": card["capability_id"],
                "current_status": card["status"],
                "requested_target_status": "SANDBOX" if card["status"] == "CANDIDATE" else "CANON",
                "reason": card["next_review_reason"],
                "card_path": (
                    f"IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/"
                    f"{card['category']}/{card['capability_id']}.json"
                ),
            }
            for card in cards
            if card["status"] in {"CANDIDATE", "SANDBOX"}
        ],
    }
    (arsenal_root / "REGISTRY" / "intake_queue_v0_1.json").write_text(
        as_pretty_json(intake_queue), encoding="utf-8"
    )

    arsenal_registry = {
        "schema_version": "arsenal.registry.v0_1",
        "generated_at_utc": NOW_UTC,
        "task_id": TASK_ID,
        "root_path": "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL",
        "card_count": len(cards),
        "status_counts": status_counts,
        "cards": [
            {
                "capability_id": card["capability_id"],
                "name": card["name"],
                "category": card["category"],
                "status": card["status"],
                "card_path": (
                    f"IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/"
                    f"{card['category']}/{card['capability_id']}.json"
                ),
                "owner_organ": card["owner_organ"],
                "source_type": card["source_type"],
                "install_required": card["install_required"],
            }
            for card in cards
        ],
    }
    (arsenal_root / "REGISTRY" / "arsenal_registry_v0_1.json").write_text(
        as_pretty_json(arsenal_registry), encoding="utf-8"
    )

    capability_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "imperium.newgen.mechanicus.arsenal.capability_card.v0_1",
        "title": "Mechanicus Arsenal Capability Card V0.1",
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "capability_id": {"type": "string", "minLength": 3},
            "name": {"type": "string", "minLength": 1},
            "category": {"type": "string", "enum": categories},
            "status": {"type": "string", "enum": ["CANDIDATE", "SANDBOX", "CANON", "QUARANTINE", "REJECTED"]},
            "owner_organ": {"type": "string", "minLength": 1},
            "purpose": {"type": "string", "minLength": 1},
            "what_problem_it_solves": {"type": "string", "minLength": 1},
            "source_type": {
                "type": "string",
                "enum": [
                    "built_in",
                    "repo_existing",
                    "external_tool",
                    "practice",
                    "reference_code",
                    "algorithm",
                    "database",
                    "adapter",
                ],
            },
            "source_url_or_path": {"type": "string", "minLength": 1},
            "license_or_trust_note": {"type": "string", "minLength": 1},
            "install_required": {"type": "boolean"},
            "install_gate": {"type": "string", "minLength": 1},
            "validation_commands": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "expected_receipts": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "safety_notes": {"type": "string", "minLength": 1},
            "security_notes": {"type": "string", "minLength": 1},
            "offline_or_network_dependency": {
                "type": "string",
                "enum": ["offline_preferred", "network_optional", "network_required"],
            },
            "promoted_by_receipt": {"type": "string", "minLength": 1},
            "last_reviewed_utc": {"type": "string", "format": "date-time"},
            "next_review_reason": {"type": "string", "minLength": 1},
            "limitations": {"type": "string", "minLength": 1},
            "allowed_use_cases": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "forbidden_use_cases": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "canon_evidence_paths": {"type": "array", "items": {"type": "string"}},
        },
        "required": required_card_fields,
    }
    (arsenal_root / "SCHEMAS" / "capability_card_schema_v0_1.json").write_text(
        as_pretty_json(capability_schema), encoding="utf-8"
    )

    arsenal_registry_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "imperium.newgen.mechanicus.arsenal.registry.v0_1",
        "title": "Mechanicus Arsenal Registry V0.1",
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "schema_version": {"type": "string"},
            "generated_at_utc": {"type": "string", "format": "date-time"},
            "task_id": {"type": "string"},
            "root_path": {"type": "string"},
            "card_count": {"type": "integer", "minimum": 0},
            "status_counts": {
                "type": "object",
                "properties": {key: {"type": "integer", "minimum": 0} for key in status_counts.keys()},
                "required": list(status_counts.keys()),
            },
            "cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string"},
                        "name": {"type": "string"},
                        "category": {"type": "string"},
                        "status": {"type": "string"},
                        "card_path": {"type": "string"},
                        "owner_organ": {"type": "string"},
                        "source_type": {"type": "string"},
                        "install_required": {"type": "boolean"},
                    },
                    "required": [
                        "capability_id",
                        "name",
                        "category",
                        "status",
                        "card_path",
                        "owner_organ",
                        "source_type",
                        "install_required",
                    ],
                },
            },
        },
        "required": [
            "schema_version",
            "generated_at_utc",
            "task_id",
            "root_path",
            "card_count",
            "status_counts",
            "cards",
        ],
    }
    (arsenal_root / "SCHEMAS" / "arsenal_registry_schema_v0_1.json").write_text(
        as_pretty_json(arsenal_registry_schema), encoding="utf-8"
    )

    validation_receipt_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "imperium.newgen.mechanicus.arsenal.validation_receipt.v0_1",
        "title": "Mechanicus Arsenal Validation Receipt V0.1",
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "receipt_id": {"type": "string"},
            "task_id": {"type": "string"},
            "validator": {"type": "string"},
            "checked_at_utc": {"type": "string", "format": "date-time"},
            "status": {"type": "string", "enum": ["PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED"]},
            "summary": {"type": "string"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "violations": {"type": "array", "items": {"type": "string"}},
            "evidence_paths": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["receipt_id", "task_id", "validator", "checked_at_utc", "status", "summary"],
    }
    (arsenal_root / "SCHEMAS" / "validation_receipt_schema_v0_1.json").write_text(
        as_pretty_json(validation_receipt_schema), encoding="utf-8"
    )

    baseline_receipt = {
        "receipt_id": "ARSENAL-FOUNDATION-BASELINE-20260524",
        "task_id": TASK_ID,
        "validator": "foundation_bootstrap",
        "checked_at_utc": NOW_UTC,
        "status": "PASS_WITH_WARNINGS",
        "summary": "Foundation structure and seed cards initialized; external tools remain candidate/sandbox.",
        "warnings": [
            "No external tool installation performed in this task.",
            "Most external capabilities remain CANDIDATE pending admission and receipts.",
        ],
        "violations": [],
        "evidence_paths": [
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/category_registry_v0_1.json",
        ],
    }
    (arsenal_root / "RECEIPTS" / "arsenal_foundation_baseline_receipt_v0_1.json").write_text(
        as_pretty_json(baseline_receipt), encoding="utf-8"
    )

    seed_cards_index = {
        "task_id": TASK_ID,
        "generated_at_utc": NOW_UTC,
        "seed_card_count": len(cards),
        "status_counts": status_counts,
        "cards": [
            {
                "capability_id": card["capability_id"],
                "name": card["name"],
                "category": card["category"],
                "status": card["status"],
                "card_path": (
                    f"IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES/"
                    f"{card['category']}/{card['capability_id']}.json"
                ),
            }
            for card in cards
        ],
    }
    (report_root / "seed_cards_index.json").write_text(as_pretty_json(seed_cards_index), encoding="utf-8")

    manifest = {
        "task_id": TASK_ID,
        "generated_at_utc": NOW_UTC,
        "starting_head": STARTING_HEAD,
        "arsenal_root": "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL",
        "report_root": "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-INTAKE-FOUNDATION-PC-V0_1",
        "seed_card_count": len(cards),
        "status_counts": status_counts,
        "created_core_files": [
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/README.md",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/ARSENAL_POLICY_V0_1.md",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/ARSENAL_INTAKE_PROTOCOL_V0_1.md",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/ARSENAL_STATUS_MODEL_V0_1.md",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/category_registry_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/intake_queue_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/capability_card_schema_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/arsenal_registry_schema_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS/validation_receipt_schema_v0_1.json",
        ],
    }
    (report_root / "arsenal_foundation_manifest.json").write_text(
        as_pretty_json(manifest), encoding="utf-8"
    )

    print(f"seed_cards_created={len(cards)}")
    print(json.dumps(status_counts, ensure_ascii=True))


if __name__ == "__main__":
    main()
