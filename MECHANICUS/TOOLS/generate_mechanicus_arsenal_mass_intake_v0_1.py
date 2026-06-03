from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1"
REPO_ROOT = Path(__file__).resolve().parents[3]
ARSENAL_ROOT = REPO_ROOT / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "ARSENAL"
REPORT_ROOT = (
    REPO_ROOT
    / "IMPERIUM_NEW_GENERATION"
    / "MECHANICUS"
    / "REPORTS"
    / TASK_ID
)
DOSSIER_ROOT = REPORT_ROOT / "DOSSIER_SOURCE"
SEED_BATCHES_PATH = DOSSIER_ROOT / "INTAKE_BATCHES" / "candidate_batches_v0_1.json"
CATEGORY_TARGETS_PATH = DOSSIER_ROOT / "CATEGORY_TARGETS.json"
CATEGORIES_ROOT = ARSENAL_ROOT / "CATEGORIES"
REGISTRY_ROOT = ARSENAL_ROOT / "REGISTRY"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def normalize_validation_id(capability_id: str) -> str:
    lowered = capability_id.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered


def source_type_for_category(category: str) -> str:
    if category == "REFERENCE_CODE":
        return "reference_code"
    if category == "ALGORITHMS":
        return "algorithm"
    if category == "DATABASES":
        return "database"
    if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}:
        return "adapter"
    if category in {"PLAYBOOKS", "PROMPTING_PATTERNS", "EXAMPLES"}:
        return "practice"
    return "external_tool"


def install_required_for_item(category: str, capability_id: str, name: str) -> bool:
    if category in {"PLAYBOOKS", "PROMPTING_PATTERNS", "ALGORITHMS", "REFERENCE_CODE", "EXAMPLES"}:
        return False
    built_in_markers = ("POWERSHELL", "GIT", "HTML_CSS", "SQL")
    if any(marker in capability_id for marker in built_in_markers):
        return False
    lower_name = name.lower()
    if "policy" in lower_name or "practice" in lower_name or "pattern" in lower_name:
        return False
    return True


def dependency_for_category(category: str) -> str:
    if category == "CLOUD_LLM_ADAPTERS":
        return "network_required"
    if category in {"LOCAL_LLM", "UI_FRAMEWORKS", "VISUAL_TESTING"}:
        return "network_optional"
    return "offline_preferred"


def source_hint(category: str, name: str) -> str:
    if category == "REFERENCE_CODE":
        return "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCHEMAS"
    if category == "PLAYBOOKS":
        return "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/ARSENAL_INTAKE_PROTOCOL_V0_1.md"
    if category == "PROMPTING_PATTERNS":
        return "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/" + TASK_ID
    if category == "ALGORITHMS":
        return "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS"
    if category == "LOCAL_LLM":
        return "RESERVED_LOCAL_LLM_CANDIDATE_" + name.replace(" ", "_").upper()
    if category == "CLOUD_LLM_ADAPTERS":
        return "RESERVED_CLOUD_LLM_CANDIDATE_" + name.replace(" ", "_").upper()
    return "TO_VERIFY_LOCAL_OR_VENDOR_SOURCE"


def build_card(
    item: dict[str, Any],
    batch: dict[str, Any],
    reviewed_at: str,
) -> dict[str, Any]:
    category = str(item["category"])
    capability_id = str(item["capability_id"])
    name = str(item["name"])
    reserved = bool(item.get("reserved", False) or batch.get("reserved_only", False))
    source_type = source_type_for_category(category)
    install_required = install_required_for_item(category, capability_id, name)
    install_gate = (
        "GATE-ARSENAL-EXTERNAL-INSTALL-ADMISSION" if install_required else "GATE-U09-NO-FAKE-GREEN"
    )

    validation_key = normalize_validation_id(capability_id)
    forbidden_use_cases = [
        "Claiming CANON without validation receipt evidence",
        "Using capability outside bounded task scope",
    ]
    if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}:
        forbidden_use_cases.extend(
            [
                "Configuring secrets or API keys in this intake task",
                "Runtime integration or production claim in reserved phase",
            ]
        )

    license_note = "TO_VERIFY; no promotion beyond CANDIDATE without receipt evidence."
    next_reason = "Mass intake seed; requires bounded validation before SANDBOX promotion."
    limitations = "Candidate-only until validation receipts and trust checks exist."
    policy_tags: list[str] = []
    if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"} or reserved:
        license_note = (
            "RESERVED; CANDIDATE_ONLY; FUTURE_DEDICATED_TASK_REQUIRED; "
            "secret/cost/privacy policy gate required."
        )
        next_reason = "Reserved candidate only; dedicated LLM/cloud policy task required."
        limitations = "RESERVED/CANDIDATE_ONLY in this task; no deep integration permitted."
        policy_tags = ["RESERVED", "CANDIDATE_ONLY", "FUTURE_DEDICATED_TASK_REQUIRED"]

    card: dict[str, Any] = {
        "capability_id": capability_id,
        "name": name,
        "category": category,
        "status": "CANDIDATE",
        "owner_organ": "MECHANICUS",
        "purpose": f"Mass intake candidate for {name} in {category}.",
        "what_problem_it_solves": str(item.get("reason", "Mass intake seed capability.")),
        "source_type": source_type,
        "source_url_or_path": source_hint(category, name),
        "license_or_trust_note": license_note,
        "install_required": install_required,
        "install_gate": install_gate,
        "validation_commands": [f"validate:{validation_key}"],
        "expected_receipts": [f"{validation_key}_validation_receipt.json"],
        "safety_notes": "Bounded use only; no uncontrolled runtime mutation or hidden side effects.",
        "security_notes": "No secret handling in this task; obey path, scope, and evidence gates.",
        "offline_or_network_dependency": dependency_for_category(category),
        "promoted_by_receipt": "NOT_PROMOTED",
        "last_reviewed_utc": reviewed_at,
        "next_review_reason": next_reason,
        "limitations": limitations,
        "allowed_use_cases": [
            "Capability cataloging and validation planning",
            "Scoped candidate execution after explicit admission gate",
        ],
        "forbidden_use_cases": forbidden_use_cases,
        "reserved": reserved,
        "intake_batch_id": str(batch["batch_id"]),
        "desired_future_status": str(item.get("desired_future_status", "CANDIDATE_OR_SANDBOX_AFTER_VALIDATION")),
    }
    if policy_tags:
        card["policy_tags"] = policy_tags
    return card


def create_capability_folder(
    category_root: Path,
    batch: dict[str, Any],
    item: dict[str, Any],
    card: dict[str, Any],
) -> dict[str, str]:
    capability_id = str(item["capability_id"])
    capability_dir = category_root / capability_id
    receipts_dir = capability_dir / "validation_receipts"
    examples_dir = capability_dir / "examples"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(parents=True, exist_ok=True)

    card_path = capability_dir / "capability_card.json"
    write_json(card_path, card)

    write_text(
        capability_dir / "README.md",
        "\n".join(
            [
                f"# {card['name']}",
                "",
                f"- capability_id: `{card['capability_id']}`",
                f"- category: `{card['category']}`",
                f"- status: `{card['status']}`",
                f"- source_type: `{card['source_type']}`",
                f"- install_required: `{card['install_required']}`",
                "",
                "This folder was created by mass intake to establish candidate coverage with honest limits.",
            ]
        ),
    )

    write_text(
        capability_dir / "validation_plan.md",
        "\n".join(
            [
                f"# Validation Plan — {card['capability_id']}",
                "",
                "1. Confirm source/license/trust note.",
                "2. Run bounded local probe command(s).",
                "3. Emit validation receipt JSON under `validation_receipts/`.",
                "4. Re-check fake-CANON and LLM reserved policies before promotion.",
                "",
                f"Planned command key: `{card['validation_commands'][0]}`",
            ]
        ),
    )

    write_text(
        capability_dir / "usage_contract.md",
        "\n".join(
            [
                f"# Usage Contract — {card['capability_id']}",
                "",
                "- Current status is `CANDIDATE`.",
                "- No CANON claim is allowed without receipt evidence.",
                "- Scope is limited to Mechanicus validation tasks.",
                "- Forbidden: unsandboxed runtime mutation, secret injection, and out-of-scope use.",
            ]
        ),
    )

    write_text(
        capability_dir / "risks.md",
        "\n".join(
            [
                f"# Risks — {card['capability_id']}",
                "",
                "- Trust/license uncertainty until verified.",
                "- Potential install/runtime drift if promoted without gate receipts.",
                "- Fake-CANON risk if evidence links are missing.",
            ]
        ),
    )

    write_text(
        receipts_dir / "README.md",
        "\n".join(
            [
                "# Validation Receipts",
                "",
                "Store machine-readable receipt JSON files here when this capability is tested.",
            ]
        ),
    )
    write_text(
        examples_dir / "README.md",
        "\n".join(
            [
                "# Examples",
                "",
                "Optional bounded examples for this capability may be added here after validation planning.",
            ]
        ),
    )

    return {
        "capability_id": capability_id,
        "capability_dir": capability_dir.relative_to(REPO_ROOT).as_posix(),
        "card_path": card_path.relative_to(REPO_ROOT).as_posix(),
    }


def collect_all_cards() -> list[tuple[dict[str, Any], Path]]:
    cards: list[tuple[dict[str, Any], Path]] = []
    for path in sorted(CATEGORIES_ROOT.rglob("*.json")):
        try:
            payload = load_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if {"capability_id", "name", "category", "status"}.issubset(payload.keys()):
            cards.append((payload, path))
    return cards


def canon_evidence_ok(card: dict[str, Any]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    evidence_paths = card.get("canon_evidence_paths", [])
    if isinstance(evidence_paths, list) and evidence_paths:
        for rel in evidence_paths:
            if not isinstance(rel, str):
                missing.append("<non-string-evidence-path>")
                continue
            if not (REPO_ROOT / rel).exists():
                missing.append(rel)
        return (len(missing) == 0, missing)

    promoted_by = str(card.get("promoted_by_receipt", ""))
    if promoted_by.endswith(".json"):
        candidate_paths = [
            REPO_ROOT / promoted_by,
            ARSENAL_ROOT / "RECEIPTS" / promoted_by,
        ]
        if any(path.exists() for path in candidate_paths):
            return (True, [])
        return (False, [promoted_by])
    return (False, ["missing_canon_evidence_paths"])


def main() -> int:
    if not SEED_BATCHES_PATH.is_file():
        raise FileNotFoundError(f"Seed batches file is missing: {SEED_BATCHES_PATH}")
    if not CATEGORY_TARGETS_PATH.is_file():
        raise FileNotFoundError(f"Category targets file is missing: {CATEGORY_TARGETS_PATH}")

    reviewed_at = now_utc()
    seed_batches = load_json(SEED_BATCHES_PATH)
    category_targets = load_json(CATEGORY_TARGETS_PATH)
    batches = list(seed_batches.get("batches", []))

    created: list[dict[str, str]] = []
    new_cards_by_category: Counter[str] = Counter()

    for batch in batches:
        category = str(batch["category"])
        category_root = CATEGORIES_ROOT / category
        category_root.mkdir(parents=True, exist_ok=True)
        items = list(batch.get("items", []))
        for item in items:
            card = build_card(item=item, batch=batch, reviewed_at=reviewed_at)
            created_item = create_capability_folder(category_root, batch, item, card)
            created.append(created_item)
            new_cards_by_category[category] += 1

    write_json(
        REGISTRY_ROOT / "mass_intake_candidate_batches_v0_1.json",
        {
            "schema_id": "mechanicus_mass_intake_batches_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": reviewed_at,
            "source_dossier_path": DOSSIER_ROOT.relative_to(REPO_ROOT).as_posix(),
            "batches": batches,
        },
    )

    all_cards = collect_all_cards()
    status_counts: Counter[str] = Counter()
    category_counts_total: Counter[str] = Counter()
    registry_cards: list[dict[str, Any]] = []
    next_validation_queue: list[dict[str, Any]] = []
    llm_reserved_violations: list[str] = []
    fake_canon_entries: list[dict[str, Any]] = []

    for card, card_path in all_cards:
        category = str(card.get("category", "UNKNOWN"))
        status = str(card.get("status", "UNKNOWN"))
        status_counts[status] += 1
        category_counts_total[category] += 1

        registry_cards.append(
            {
                "capability_id": str(card.get("capability_id", "")),
                "name": str(card.get("name", "")),
                "category": category,
                "status": status,
                "card_path": card_path.relative_to(REPO_ROOT).as_posix(),
                "owner_organ": str(card.get("owner_organ", "MECHANICUS")),
                "source_type": str(card.get("source_type", "external_tool")),
                "install_required": bool(card.get("install_required", False)),
            }
        )

        if status == "CANON":
            ok, missing = canon_evidence_ok(card)
            if not ok:
                fake_canon_entries.append(
                    {
                        "capability_id": str(card.get("capability_id", "")),
                        "category": category,
                        "card_path": card_path.relative_to(REPO_ROOT).as_posix(),
                        "missing_evidence": missing,
                    }
                )
        if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"} and status == "CANON":
            llm_reserved_violations.append(str(card.get("capability_id", "")))

        if status == "CANDIDATE":
            if category in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}:
                reason = "Reserved candidate only; dedicated task + owner gate required before any promotion."
            elif bool(card.get("install_required", False)):
                reason = "Requires local admission/install receipts before SANDBOX promotion."
            else:
                reason = "Requires bounded validation receipts before SANDBOX promotion."
            next_validation_queue.append(
                {
                    "capability_id": str(card.get("capability_id", "")),
                    "current_status": "CANDIDATE",
                    "requested_target_status": "SANDBOX",
                    "reason": reason,
                    "card_path": card_path.relative_to(REPO_ROOT).as_posix(),
                    "category": category,
                }
            )
        elif status == "SANDBOX":
            next_validation_queue.append(
                {
                    "capability_id": str(card.get("capability_id", "")),
                    "current_status": "SANDBOX",
                    "requested_target_status": "CANON",
                    "reason": "Requires receipt evidence and fake-CANON check before promotion.",
                    "card_path": card_path.relative_to(REPO_ROOT).as_posix(),
                    "category": category,
                }
            )

    registry_cards.sort(key=lambda x: (x["category"], x["capability_id"]))
    next_validation_queue.sort(key=lambda x: (x["category"], x["capability_id"]))

    arsenal_registry_payload = {
        "schema_version": "arsenal.registry.v0_1",
        "generated_at_utc": reviewed_at,
        "task_id": TASK_ID,
        "root_path": "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL",
        "card_count": len(registry_cards),
        "status_counts": {
            "CANDIDATE": int(status_counts.get("CANDIDATE", 0)),
            "SANDBOX": int(status_counts.get("SANDBOX", 0)),
            "CANON": int(status_counts.get("CANON", 0)),
            "QUARANTINE": int(status_counts.get("QUARANTINE", 0)),
            "REJECTED": int(status_counts.get("REJECTED", 0)),
        },
        "cards": registry_cards,
    }
    write_json(REGISTRY_ROOT / "arsenal_registry_v0_1.json", arsenal_registry_payload)

    intake_queue_payload = {
        "schema_version": "arsenal.intake_queue.v0_1",
        "generated_at_utc": reviewed_at,
        "queue": next_validation_queue,
    }
    write_json(REGISTRY_ROOT / "intake_queue_v0_1.json", intake_queue_payload)

    category_target_map: dict[str, Any] = dict(category_targets.get("categories", {}))
    coverage_rows: list[dict[str, Any]] = []
    for category, cfg in sorted(category_target_map.items()):
        count = int(category_counts_total.get(category, 0))
        minimum = int(cfg.get("minimum_cards", 0))
        preferred = int(cfg.get("preferred_cards", 0))
        coverage_rows.append(
            {
                "category": category,
                "count": count,
                "minimum_cards": minimum,
                "preferred_cards": preferred,
                "minimum_met": count >= minimum,
                "preferred_met": count >= preferred,
                "reserved_only": bool(cfg.get("reserved_only", False)),
            }
        )

    total_cards = len(registry_cards)
    coverage_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "minimum_total_cards": int(category_targets.get("minimum_total_cards", 80)),
        "recommended_total_cards": int(category_targets.get("recommended_total_cards", 100)),
        "total_cards": total_cards,
        "minimum_total_met": total_cards >= int(category_targets.get("minimum_total_cards", 80)),
        "recommended_total_met": total_cards >= int(category_targets.get("recommended_total_cards", 100)),
        "categories": coverage_rows,
    }

    fake_canon_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "total_canon_cards": int(status_counts.get("CANON", 0)),
        "fake_canon_count": len(fake_canon_entries),
        "fake_canon_entries": fake_canon_entries,
        "llm_cloud_canon_violations": llm_reserved_violations,
    }

    llm_cards = [card for card, _ in all_cards if str(card.get("category", "")) in {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}]
    llm_status_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for card in llm_cards:
        cat = str(card.get("category", "UNKNOWN"))
        st = str(card.get("status", "UNKNOWN"))
        llm_status_counts[cat][st] += 1

    llm_reserved_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "policy_labels_required": ["RESERVED", "CANDIDATE_ONLY", "FUTURE_DEDICATED_TASK_REQUIRED"],
        "llm_status_counts": {
            category: dict(sorted(counts.items()))
            for category, counts in sorted(llm_status_counts.items())
        },
        "llm_cloud_canon_count": len(llm_reserved_violations),
        "llm_cloud_canon_capabilities": llm_reserved_violations,
        "policy_verdict": "PASS" if len(llm_reserved_violations) == 0 else "FAIL",
    }

    owner_questions_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "questions": [
            {
                "question_id": "Q-ARS-001",
                "category": "CODE_QUALITY",
                "question": "Choose primary type checker lane for Python promotion: pyright-first, mypy-first, or dual-lane?",
                "impact_if_unanswered": "Type-safety promotion queue may stall.",
            },
            {
                "question_id": "Q-ARS-002",
                "category": "VISUAL_TESTING",
                "question": "Do we prioritize Playwright-only visual baseline first, or multi-runner strategy later?",
                "impact_if_unanswered": "Visual validation sequence remains ambiguous.",
            },
            {
                "question_id": "Q-ARS-003",
                "category": "DATABASES",
                "question": "Should SQLite remain default evidence store, or should DuckDB become co-primary?",
                "impact_if_unanswered": "Search/evidence architecture may diverge by task.",
            },
            {
                "question_id": "Q-ARS-004",
                "category": "UI_FRAMEWORKS",
                "question": "For owner-facing cockpit work, do we anchor plain HTML/CSS/JS first or React/Vite first?",
                "impact_if_unanswered": "UI stack promotions risk drift.",
            },
            {
                "question_id": "Q-ARS-005",
                "category": "CLOUD_LLM_ADAPTERS",
                "question": "Which secret-policy baseline is required before any cloud adapter leaves CANDIDATE?",
                "impact_if_unanswered": "Cloud adapters remain blocked (intentionally).",
            },
            {
                "question_id": "Q-ARS-006",
                "category": "LOCAL_LLM",
                "question": "Which local runner is the first dedicated validation target (Ollama, llama.cpp, or LM Studio)?",
                "impact_if_unanswered": "Local LLM lane cannot move beyond reserved planning.",
            },
            {
                "question_id": "Q-ARS-007",
                "category": "SEARCH_INDEXING",
                "question": "Do we prioritize ripgrep-index manifest strategy or a DB-backed index strategy first?",
                "impact_if_unanswered": "Search-indexing validations may duplicate effort.",
            },
            {
                "question_id": "Q-ARS-008",
                "category": "TOOLS",
                "question": "Should external tool admissions happen by category waves or by dependency chains?",
                "impact_if_unanswered": "Validation queue prioritization remains unfocused.",
            },
            {
                "question_id": "Q-ARS-009",
                "category": "PROMPTING_PATTERNS",
                "question": "Do we canonize any prompt patterns early, or keep all prompting cards candidate until audit cycle?",
                "impact_if_unanswered": "Prompting lane promotion criteria remain unclear.",
            },
            {
                "question_id": "Q-ARS-010",
                "category": "PLAYBOOKS",
                "question": "Which playbook should be promoted first as cross-organ standard: scope-review or no-fake-green?",
                "impact_if_unanswered": "Operational standardization is delayed.",
            },
        ],
    }

    scope_seed_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "scope_model_version": "servitor_capability_scope_seed_v0_1",
        "summary": {
            "total_cards": total_cards,
            "candidate_cards": int(status_counts.get("CANDIDATE", 0)),
            "sandbox_cards": int(status_counts.get("SANDBOX", 0)),
            "canon_cards": int(status_counts.get("CANON", 0)),
        },
        "categories": [
            {
                "category": category,
                "capability_count": int(category_counts_total.get(category, 0)),
                "reserved_only": bool(category_target_map.get(category, {}).get("reserved_only", False)),
            }
            for category in sorted(category_target_map.keys())
        ],
        "scope_seed": [
            {
                "capability_id": str(card.get("capability_id", "")),
                "category": str(card.get("category", "")),
                "status": str(card.get("status", "")),
                "install_required": bool(card.get("install_required", False)),
                "reserved": bool(card.get("reserved", False)),
                "validation_commands": list(card.get("validation_commands", [])),
                "card_path": path.relative_to(REPO_ROOT).as_posix(),
            }
            for card, path in sorted(
                all_cards, key=lambda row: (str(row[0].get("category", "")), str(row[0].get("capability_id", "")))
            )
        ],
    }

    manifest_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": reviewed_at,
        "seed_batch_source": SEED_BATCHES_PATH.relative_to(REPO_ROOT).as_posix(),
        "new_capability_folder_count": len(created),
        "new_card_count_by_category": dict(sorted(new_cards_by_category.items())),
        "total_cards_after_generation": total_cards,
        "reports_generated": [
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/mass_intake_manifest.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/category_coverage_report.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/fake_canon_detection_report.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/next_validation_queue.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/owner_questions_report.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/llm_reserved_policy_report.json",
            f"IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/{TASK_ID}/servitor_capability_scope_seed_report.json",
        ],
        "registry_updates": [
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/intake_queue_v0_1.json",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/mass_intake_candidate_batches_v0_1.json",
        ],
    }

    write_json(REPORT_ROOT / "mass_intake_manifest.json", manifest_payload)
    write_json(REPORT_ROOT / "category_coverage_report.json", coverage_payload)
    write_json(REPORT_ROOT / "fake_canon_detection_report.json", fake_canon_payload)
    write_json(REPORT_ROOT / "next_validation_queue.json", {"task_id": TASK_ID, "generated_at_utc": reviewed_at, "queue": next_validation_queue})
    write_json(REPORT_ROOT / "owner_questions_report.json", owner_questions_payload)
    write_json(REPORT_ROOT / "llm_reserved_policy_report.json", llm_reserved_payload)
    write_json(REPORT_ROOT / "servitor_capability_scope_seed_report.json", scope_seed_payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
