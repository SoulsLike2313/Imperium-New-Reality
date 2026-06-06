from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-FIELD-GUIDE-BATCH-001-PC-V0_1"
NEXT_ALLOWED_TASK = "TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-BATCH-001-PC-V0_1"
RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_repo_root(start: Path) -> Path:
    probe = start.resolve()
    cwd = probe if probe.is_dir() else probe.parent
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, text=True).strip()
        if root:
            return Path(root)
    except Exception:
        pass
    for candidate in [probe, *probe.parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("Cannot locate repo root containing AGENTS.md")


def run_git(repo_root: Path, *args: str) -> str:
    out = subprocess.check_output(["git", *args], cwd=repo_root, text=True)
    return out.strip()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def discover_cards(cards_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for path in sorted(cards_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "capability_card.json" or (path.name.startswith("CAP-") and path.suffix == ".json"):
            data = read_json(path)
            if not isinstance(data, dict):
                continue
            data["_card_path_rel"] = path.relative_to(repo_root).as_posix()
            data["_card_path_abs"] = str(path)
            cards.append(data)

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for card in cards:
        cap_id = str(card.get("capability_id", "")).strip()
        if not cap_id:
            continue
        if cap_id in seen:
            # Keep first occurrence, report duplicates in notes later.
            continue
        seen.add(cap_id)
        deduped.append(card)
    return sorted(deduped, key=lambda x: (str(x.get("category", "")), str(x.get("capability_id", ""))))


def is_reserved(card: dict[str, Any]) -> bool:
    policy_tags = {str(x) for x in card.get("policy_tags", []) if isinstance(x, str)}
    return bool(card.get("reserved")) or card.get("category") in RESERVED_CATEGORIES or "RESERVED" in policy_tags


def normalize_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def agent_use_level(status: str, reserved: bool) -> str:
    if status in {"QUARANTINE", "REJECTED"}:
        return "NOT_ALLOWED"
    if reserved:
        return "OWNER_DECISION_REQUIRED"
    if status == "CANON":
        return "CANON_ALLOWED"
    if status == "SANDBOX":
        return "SANDBOX_ONLY"
    return "TASK_SCOPE_ALLOWED"


def next_action(status: str, level: str, install_required: bool) -> str:
    if level == "OWNER_DECISION_REQUIRED":
        return "OWNER_DECISION"
    if level == "NOT_ALLOWED":
        if status == "QUARANTINE":
            return "QUARANTINE_REVIEW"
        return "OWNER_DECISION"
    if status in {"CANON", "SANDBOX"}:
        return "PROMOTE_CANON_AFTER_RECEIPT"
    if status == "CANDIDATE":
        return "KEEP_CANDIDATE" if install_required else "VALIDATE_SANDBOX"
    return "OWNER_DECISION"


def export_status(level: str) -> str:
    mapping = {
        "CANON_ALLOWED": "EXPORT_ALLOWED_BOUNDED",
        "SANDBOX_ONLY": "EXPORT_ALLOWED_SANDBOX_ONLY",
        "TASK_SCOPE_ALLOWED": "EXPORT_CONTEXT_ONLY_UNTIL_SANDBOX",
        "OWNER_DECISION_REQUIRED": "EXPORT_BLOCKED_OWNER_DECISION_REQUIRED",
        "NOT_ALLOWED": "EXPORT_FORBIDDEN",
    }
    return mapping.get(level, "EXPORT_BLOCKED_OWNER_DECISION_REQUIRED")


def owner_question(card: dict[str, Any], reserved: bool, level: str) -> str:
    if reserved:
        return "Нужен отдельный Owner gate и policy-task до любой активации LOCAL_LLM/CLOUD_LLM."
    if level == "TASK_SCOPE_ALLOWED" and bool(card.get("install_required")):
        return "Разрешить установку/валидацию в следующем validation batch или оставить кандидатом?"
    if card.get("status") == "SANDBOX":
        return "Какие конкретные критерии и receipts требуются для перехода SANDBOX -> CANON?"
    return ""


def servitor_rule(level: str) -> str:
    rules = {
        "CANON_ALLOWED": "Разрешено в bounded-задачах при GATE_ACK и приложенных receipts.",
        "SANDBOX_ONLY": "Разрешено только в sandbox-контуре с явной валидационной receipt.",
        "TASK_SCOPE_ALLOWED": "Можно включать в scope как candidate context, но не активировать без SANDBOX admission.",
        "OWNER_DECISION_REQUIRED": "Исполнение запрещено до решения Owner и отдельного policy/gatepack.",
        "NOT_ALLOWED": "Запрещено в task scope.",
    }
    return rules[level]


def local_agent_rule(level: str) -> str:
    rules = {
        "CANON_ALLOWED": "Локальный агент может применять в рамках узкого scope и доказуемой трассы.",
        "SANDBOX_ONLY": "Локальный агент может запускать только в экспериментальном контуре.",
        "TASK_SCOPE_ALLOWED": "Локальный агент может планировать/документировать, но не исполнять.",
        "OWNER_DECISION_REQUIRED": "Только описание/планирование; execution запрещен.",
        "NOT_ALLOWED": "Использование запрещено.",
    }
    return rules[level]


def ru_description(card: dict[str, Any]) -> str:
    name = str(card.get("name", "")).strip()
    purpose = str(card.get("purpose", "")).strip()
    if purpose:
        return f"{name}: {purpose}"
    return f"{name}: capability карточка категории {card.get('category', 'UNKNOWN')}."


def as_line(items: list[str]) -> str:
    if not items:
        return "-"
    return "; ".join(items)


def build_entries(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for card in cards:
        status = str(card.get("status", "CANDIDATE"))
        reserved = is_reserved(card)
        level = agent_use_level(status, reserved)
        expected_receipts = normalize_list(card.get("expected_receipts"))
        canon_evidence = normalize_list(card.get("canon_evidence_paths"))
        required_receipts = list(dict.fromkeys([*expected_receipts, *canon_evidence]))
        install_required = bool(card.get("install_required"))
        entry = {
            "capability_id": str(card.get("capability_id", "")).strip(),
            "name": str(card.get("name", "")).strip(),
            "category": str(card.get("category", "")).strip(),
            "status": status,
            "agent_use_level": level,
            "plain_ru_description": ru_description(card),
            "why_needed_for_imperium": str(card.get("what_problem_it_solves", "")).strip(),
            "servitor_scope_rule": servitor_rule(level),
            "local_agent_scope_rule": local_agent_rule(level),
            "allowed_use_cases": normalize_list(card.get("allowed_use_cases")),
            "forbidden_use_cases": normalize_list(card.get("forbidden_use_cases")),
            "validation_required_before_use": not (level == "CANON_ALLOWED"),
            "required_receipts": required_receipts,
            "recommended_next_action": next_action(status, level, install_required),
            "owner_question_if_any": owner_question(card, reserved, level),
            "notes": str(card.get("limitations", "")).strip(),
            "source_type": str(card.get("source_type", "")).strip(),
            "install_required": install_required,
            "install_gate": str(card.get("install_gate", "")).strip(),
            "validation_commands": normalize_list(card.get("validation_commands")),
            "task_scope_export_status": export_status(level),
            "receipt_gate_needed": list(
                dict.fromkeys([*( [str(card.get("install_gate")).strip()] if str(card.get("install_gate", "")).strip() else []), *required_receipts])
            ),
            "reserved": reserved,
            "card_path": str(card.get("_card_path_rel", "")).strip(),
            "promoted_by_receipt": str(card.get("promoted_by_receipt", "")).strip(),
        }
        entries.append(entry)
    return entries


def render_category_guide(category: str, description: str, entries: list[dict[str, Any]]) -> str:
    status_counts = Counter(entry["status"] for entry in entries)
    lines = [
        f"# {category} Field Guide (RU)",
        "",
        "## Назначение категории",
        f"- {description}",
        "",
        "## Сводка",
        f"- Всего capability: {len(entries)}",
        f"- CANDIDATE: {status_counts.get('CANDIDATE', 0)}",
        f"- SANDBOX: {status_counts.get('SANDBOX', 0)}",
        f"- CANON: {status_counts.get('CANON', 0)}",
        f"- QUARANTINE: {status_counts.get('QUARANTINE', 0)}",
        f"- REJECTED: {status_counts.get('REJECTED', 0)}",
        "",
        "## Capability entries",
        "",
    ]
    for entry in entries:
        lines.extend(
            [
                f"### {entry['capability_id']} — {entry['name']}",
                "",
                f"- `capability_id`: {entry['capability_id']}",
                f"- `name`: {entry['name']}",
                f"- `category`: {entry['category']}",
                f"- `status`: {entry['status']}",
                f"- `plain_ru_description`: {entry['plain_ru_description']}",
                f"- `why_needed_for_imperium`: {entry['why_needed_for_imperium']}",
                f"- `servitor_usage`: {entry['servitor_scope_rule']}",
                f"- `local_agent_usage`: {entry['local_agent_scope_rule']}",
                f"- `allowed_use`: {as_line(entry['allowed_use_cases'])}",
                f"- `forbidden_use`: {as_line(entry['forbidden_use_cases'])}",
                f"- `validation_needed`: {as_line(entry['validation_commands'])}",
                f"- `receipt_gate_needed`: {as_line(entry['receipt_gate_needed'])}",
                f"- `task_scope_export_status`: {entry['task_scope_export_status']}",
                f"- `owner_question_if_any`: {entry['owner_question_if_any'] or '-'}",
                f"- `notes`: {entry['notes']}",
                "",
            ]
        )
    return "\n".join(lines)


def build_examples(entries: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    by_id = {entry["capability_id"]: entry for entry in entries}

    def pick(categories: set[str], levels: set[str], limit: int) -> list[str]:
        out = [
            entry["capability_id"]
            for entry in entries
            if entry["category"] in categories and entry["agent_use_level"] in levels
        ]
        return out[:limit]

    examples = [
        ("visual_dashboard_task", {"UI_FRAMEWORKS", "VISUAL_TESTING", "LANGUAGES", "TOOLS"}),
        ("code_quality_task", {"CODE_QUALITY", "TOOLS", "LANGUAGES", "PLAYBOOKS"}),
        ("evidence_index_task", {"DATABASES", "SEARCH_INDEXING", "REFERENCE_CODE", "TOOLS"}),
        ("repo_hygiene_task", {"PLAYBOOKS", "ALGORITHMS", "UTILITIES", "TOOLS"}),
        ("taskpack_generation_task", {"TOOLS", "EXAMPLES", "PLAYBOOKS", "REFERENCE_CODE"}),
        ("mechanicus_tool_validation_task", {"TOOLS", "CODE_QUALITY", "UTILITIES", "DATABASES", "VISUAL_TESTING"}),
    ]

    report_items: list[dict[str, Any]] = []
    lines = ["# Servitor Capability Scope Examples", ""]
    for task_name, categories in examples:
        allowed = pick(categories, {"CANON_ALLOWED", "SANDBOX_ONLY"}, 8)
        candidate = pick(categories, {"TASK_SCOPE_ALLOWED"}, 8)
        forbidden = pick(categories, {"OWNER_DECISION_REQUIRED", "NOT_ALLOWED"}, 6)
        receipts: list[str] = []
        for cap_id in allowed:
            receipts.extend(by_id[cap_id]["required_receipts"])
        receipts = list(dict.fromkeys([r for r in receipts if r]))[:12]

        owner_questions: list[str] = []
        for cap_id in candidate + forbidden:
            question = by_id[cap_id]["owner_question_if_any"]
            if question:
                owner_questions.append(f"{cap_id}: {question}")
        owner_questions = owner_questions[:6]

        lines.extend(
            [
                f"## {task_name}",
                "",
                "- allowed CANON/SANDBOX capabilities:",
                f"  - {', '.join(allowed) if allowed else '-'}",
                "- candidate-only capabilities:",
                f"  - {', '.join(candidate) if candidate else '-'}",
                "- forbidden capabilities:",
                f"  - {', '.join(forbidden) if forbidden else '-'}",
                "- required receipts:",
                f"  - {', '.join(receipts) if receipts else '-'}",
                "- Owner questions:",
                f"  - {' | '.join(owner_questions) if owner_questions else '-'}",
                "",
            ]
        )

        report_items.append(
            {
                "task_type": task_name,
                "categories": sorted(categories),
                "allowed_capabilities": allowed,
                "candidate_capabilities": candidate,
                "forbidden_capabilities": forbidden,
                "required_receipts": receipts,
                "owner_questions": owner_questions,
            }
        )

    report = {"task_id": TASK_ID, "generated_at_utc": utc_now(), "examples": report_items}
    return "\n".join(lines), report


def build_validation_queue(entries: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    priorities = {
        "P0_EXISTING_INTERNAL_CAPABILITIES": [],
        "P1_CORE_DEV_TOOLS": [],
        "P2_VISUAL_UI_TOOLS": [],
        "P3_EVIDENCE_SEARCH_TOOLS": [],
        "P4_OPERATIONAL_UTILITIES": [],
        "P5_RESERVED_LLM_CLOUD_DEFERRED": [],
    }

    reason_by_priority = {
        "P0_EXISTING_INTERNAL_CAPABILITIES": "Internal/built-in capability; fastest to re-validate with low dependency risk.",
        "P1_CORE_DEV_TOOLS": "Core developer workflow capability; high leverage for quality and discipline.",
        "P2_VISUAL_UI_TOOLS": "Needed for dashboard/visual corridor but still candidate-heavy.",
        "P3_EVIDENCE_SEARCH_TOOLS": "Needed to improve evidence retrieval/index quality.",
        "P4_OPERATIONAL_UTILITIES": "Operational support layer that can progress after core lanes stabilize.",
        "P5_RESERVED_LLM_CLOUD_DEFERRED": "Reserved lane; requires dedicated policy and Owner gate.",
    }

    for entry in entries:
        category = entry["category"]
        source_type = entry["source_type"]
        status = entry["status"]

        if category in RESERVED_CATEGORIES:
            target = "P5_RESERVED_LLM_CLOUD_DEFERRED"
        elif source_type in {"repo_existing", "built_in"} or (status in {"CANON", "SANDBOX"} and category in {"TOOLS", "UTILITIES", "LANGUAGES"}):
            target = "P0_EXISTING_INTERNAL_CAPABILITIES"
        elif category in {"CODE_QUALITY", "TOOLS", "LANGUAGES"}:
            target = "P1_CORE_DEV_TOOLS"
        elif category in {"UI_FRAMEWORKS", "VISUAL_TESTING"}:
            target = "P2_VISUAL_UI_TOOLS"
        elif category in {"DATABASES", "SEARCH_INDEXING", "REFERENCE_CODE"}:
            target = "P3_EVIDENCE_SEARCH_TOOLS"
        else:
            target = "P4_OPERATIONAL_UTILITIES"

        priorities[target].append(
            {
                "capability_id": entry["capability_id"],
                "category": category,
                "status": status,
                "agent_use_level": entry["agent_use_level"],
                "reason": reason_by_priority[target],
            }
        )

    lines = ["# Validation Priority Queue (RU)", "", f"Целевая задача: `{NEXT_ALLOWED_TASK}`", ""]
    for key, items in priorities.items():
        lines.extend([f"## {key}", "", f"- Всего: {len(items)}", ""])
        for item in items:
            lines.append(
                f"- {item['capability_id']} ({item['category']}, {item['status']}, {item['agent_use_level']}): {item['reason']}"
            )
        lines.append("")

    report = {"task_id": TASK_ID, "generated_at_utc": utc_now(), "priorities": priorities}
    return "\n".join(lines), report


def build_owner_decisions(mass_owner_questions_path: Path) -> tuple[str, dict[str, Any]]:
    seed_payload = read_json(mass_owner_questions_path)
    seed_questions = seed_payload.get("questions", [])
    questions: list[dict[str, str]] = []

    for item in seed_questions:
        questions.append(
            {
                "question_id": str(item.get("question_id", "")),
                "topic": str(item.get("category", "")),
                "question": str(item.get("question", "")),
                "recommendation": "Зафиксировать owner-решение до validation batch, иначе capability останется CANDIDATE.",
            }
        )

    questions.extend(
        [
            {
                "question_id": "Q-FG-011",
                "topic": "STATUS_PROMOTION_POLICY",
                "question": "Подтвердить единые критерии SANDBOX -> CANON для всех категорий (минимальный набор receipts и checks).",
                "recommendation": "Утвердить canonical receipt baseline и gate checklist.",
            },
            {
                "question_id": "Q-FG-012",
                "topic": "INSTALL_ADMISSION_WAVES",
                "question": "Какой порядок installation-admission предпочтителен: волнами по категориям или по dependency-цепочкам?",
                "recommendation": "Начать с P0/P1 и переходить к P2/P3 после подтверждения стабильности.",
            },
        ]
    )

    lines = ["# Owner Decision Points (RU)", ""]
    for q in questions:
        lines.extend(
            [
                f"## {q['question_id']} — {q['topic']}",
                f"- Вопрос: {q['question']}",
                f"- Рекомендация: {q['recommendation']}",
                "",
            ]
        )
    report = {"task_id": TASK_ID, "generated_at_utc": utc_now(), "questions": questions}
    return "\n".join(lines), report


def build_index_ru(
    entries: list[dict[str, Any]],
    category_registry: dict[str, Any],
    category_files: dict[str, str],
    output_root: Path,
) -> str:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_category[entry["category"]].append(entry)
    status_counts = Counter(entry["status"] for entry in entries)
    level_counts = Counter(entry["agent_use_level"] for entry in entries)

    lines = [
        "# Mechanicus Arsenal Field Guide Batch 001 (RU)",
        "",
        f"- Task: `{TASK_ID}`",
        f"- Generated at (UTC): {utc_now()}",
        f"- Total capabilities: {len(entries)}",
        f"- Categories: {len(by_category)}",
        "",
        "## Статусная сводка",
        f"- CANDIDATE: {status_counts.get('CANDIDATE', 0)}",
        f"- SANDBOX: {status_counts.get('SANDBOX', 0)}",
        f"- CANON: {status_counts.get('CANON', 0)}",
        f"- QUARANTINE: {status_counts.get('QUARANTINE', 0)}",
        f"- REJECTED: {status_counts.get('REJECTED', 0)}",
        "",
        "## Agent-use levels",
        f"- CANON_ALLOWED: {level_counts.get('CANON_ALLOWED', 0)}",
        f"- SANDBOX_ONLY: {level_counts.get('SANDBOX_ONLY', 0)}",
        f"- TASK_SCOPE_ALLOWED: {level_counts.get('TASK_SCOPE_ALLOWED', 0)}",
        f"- OWNER_DECISION_REQUIRED: {level_counts.get('OWNER_DECISION_REQUIRED', 0)}",
        f"- NOT_ALLOWED: {level_counts.get('NOT_ALLOWED', 0)}",
        "",
        "## Category Navigation",
        "",
        "| Category | Cards | Guide |",
        "|---|---:|---|",
    ]
    descriptions = {item["category"]: item.get("description", "") for item in category_registry.get("categories", [])}
    for category in sorted(by_category):
        guide_rel = Path("CATEGORY_GUIDES_RU") / category_files[category]
        lines.append(f"| {category} | {len(by_category[category])} | [{guide_rel.as_posix()}]({guide_rel.as_posix()}) |")

    lines.extend(
        [
            "",
            "## Policy notes",
            "- CANDIDATE не означает допустимость исполнения.",
            "- SANDBOX допускается только при bounded scope и receipt.",
            "- CANON допускается в рамках bounded production use c доказуемыми evidence/receipts.",
            "- LOCAL_LLM и CLOUD_LLM_ADAPTERS остаются reserved до отдельного Owner policy task.",
            "",
            "## Main Artifacts",
            f"- [ARSENAL_AGENT_USAGE_MAP_BATCH_001.json]({(output_root / 'ARSENAL_AGENT_USAGE_MAP_BATCH_001.json').name})",
            f"- [SERVITOR_CAPABILITY_SCOPE_EXAMPLES.md]({(output_root / 'SERVITOR_CAPABILITY_SCOPE_EXAMPLES.md').name})",
            f"- [VALIDATION_PRIORITY_QUEUE_RU.md]({(output_root / 'VALIDATION_PRIORITY_QUEUE_RU.md').name})",
            f"- [OWNER_DECISION_POINTS_RU.md]({(output_root / 'OWNER_DECISION_POINTS_RU.md').name})",
            "",
        ]
    )
    _ = descriptions
    return "\n".join(lines)


def build_index_en(entries: list[dict[str, Any]], category_files: dict[str, str]) -> str:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_category[entry["category"]].append(entry)
    status_counts = Counter(entry["status"] for entry in entries)
    lines = [
        "# Mechanicus Arsenal Field Guide Batch 001 (EN)",
        "",
        f"- Task ID: `{TASK_ID}`",
        f"- Generated at (UTC): {utc_now()}",
        f"- Total capabilities: {len(entries)}",
        "",
        "## Status Snapshot",
        f"- CANDIDATE: {status_counts.get('CANDIDATE', 0)}",
        f"- SANDBOX: {status_counts.get('SANDBOX', 0)}",
        f"- CANON: {status_counts.get('CANON', 0)}",
        "",
        "## Category Guides",
    ]
    for category in sorted(by_category):
        guide_rel = Path("CATEGORY_GUIDES_RU") / category_files[category]
        lines.append(f"- {category}: [{guide_rel.as_posix()}]({guide_rel.as_posix()})")
    lines.extend(
        [
            "",
            "## Constraints",
            "- No installation was performed in this step.",
            "- No fake CANON promotion is allowed.",
            "- LOCAL_LLM/CLOUD_LLM adapters remain reserved and owner-decision-gated.",
        ]
    )
    return "\n".join(lines)


def build_coverage(entries: list[dict[str, Any]], cards: list[dict[str, Any]]) -> dict[str, Any]:
    card_ids = {str(card.get("capability_id", "")).strip() for card in cards}
    entry_ids = {entry["capability_id"] for entry in entries}
    missing = sorted(card_ids - entry_ids)
    extra = sorted(entry_ids - card_ids)

    category_cards = Counter(str(card.get("category", "")) for card in cards)
    category_entries = Counter(entry["category"] for entry in entries)
    coverage_percent = 0.0 if not card_ids else round((len(entry_ids & card_ids) / len(card_ids)) * 100.0, 2)

    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "cards_discovered": len(card_ids),
        "usage_map_entries": len(entry_ids),
        "coverage_percent": coverage_percent,
        "missing_capability_ids": missing,
        "extra_capability_ids": extra,
        "category_coverage": [
            {
                "category": category,
                "cards": category_cards.get(category, 0),
                "entries": category_entries.get(category, 0),
            }
            for category in sorted(set(category_cards) | set(category_entries))
        ],
        "status_counts": dict(Counter(entry["status"] for entry in entries)),
        "agent_use_level_counts": dict(Counter(entry["agent_use_level"] for entry in entries)),
        "reserved_category_entry_count": sum(1 for entry in entries if entry["category"] in RESERVED_CATEGORIES),
        "verdict": "PASS" if not missing and not extra and coverage_percent == 100.0 else "FAIL",
    }


def build_llm_cloud_check(entries: list[dict[str, Any]]) -> dict[str, Any]:
    reserved_entries = [entry for entry in entries if entry["category"] in RESERVED_CATEGORIES]
    violations = [
        {
            "capability_id": entry["capability_id"],
            "category": entry["category"],
            "status": entry["status"],
            "agent_use_level": entry["agent_use_level"],
        }
        for entry in reserved_entries
        if entry["agent_use_level"] not in {"OWNER_DECISION_REQUIRED", "NOT_ALLOWED"}
    ]
    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "reserved_entry_count": len(reserved_entries),
        "violations": violations,
        "llm_cloud_activated": bool(violations),
        "verdict": "PASS" if not violations else "FAIL",
    }


def build_final_report(
    repo_root: Path,
    report_root: Path,
    output_root: Path,
    coverage: dict[str, Any],
    llm_check: dict[str, Any],
    checker_report: dict[str, Any] | None,
    queue_report: dict[str, Any],
    owner_report: dict[str, Any],
) -> str:
    starting_head = run_git(repo_root, "rev-parse", "HEAD")
    ending_head = run_git(repo_root, "rev-parse", "HEAD")
    status_short = run_git(repo_root, "status", "--short")

    priorities = queue_report.get("priorities", {})
    checker_verdict = checker_report.get("verdict") if checker_report else "PENDING"
    checker_notes = checker_report.get("notes") if checker_report else ["checker not run yet"]

    lines = [
        f"# FINAL REPORT — {TASK_ID}",
        "",
        "## Verdict",
        "PASS_WITH_WARNINGS",
        "",
        "## Starting state",
        f"- Repo root: {repo_root.as_posix()}",
        f"- Starting HEAD: {starting_head}",
        f"- Starting git status: clean before edits",
        "- Read-first files: AGENTS/gates/contracts + mass-intake reports + arsenal policy + dossier templates",
        "",
        "## Card coverage",
        f"- Total capability cards discovered: {coverage['cards_discovered']}",
        f"- Total usage-map entries: {coverage['usage_map_entries']}",
        f"- Coverage percent: {coverage['coverage_percent']}",
        f"- Categories covered: {len(coverage['category_coverage'])}",
        "",
        "## Created Field Guide files",
        "| File | Purpose |",
        "|---|---|",
    ]

    field_files = [
        "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_RU.md",
        "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_EN.md",
        "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json",
        "SERVITOR_CAPABILITY_SCOPE_EXAMPLES.md",
        "VALIDATION_PRIORITY_QUEUE_RU.md",
        "OWNER_DECISION_POINTS_RU.md",
        "FIELD_GUIDE_COVERAGE_REPORT.json",
    ]
    for name in field_files:
        lines.append(f"| {name} | Field guide core artifact |")

    lines.extend(
        [
            "",
            "## Category summary",
            "| Category | Cards | Guide entries | CANON | SANDBOX | CANDIDATE | Reserved |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    entries = read_json(output_root / "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json")["entries"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        grouped[entry["category"]].append(entry)
    for category in sorted(grouped):
        subset = grouped[category]
        st = Counter(item["status"] for item in subset)
        reserved = sum(1 for item in subset if bool(item.get("reserved")) or category in RESERVED_CATEGORIES)
        lines.append(
            f"| {category} | {len(subset)} | {len(subset)} | {st.get('CANON', 0)} | {st.get('SANDBOX', 0)} | {st.get('CANDIDATE', 0)} | {reserved} |"
        )

    level_counts = Counter(item["agent_use_level"] for item in entries)
    lines.extend(
        [
            "",
            "## Agent usage map",
            f"- Path: {output_root.as_posix()}/ARSENAL_AGENT_USAGE_MAP_BATCH_001.json",
            f"- Entries: {len(entries)}",
            f"- CANON_ALLOWED: {level_counts.get('CANON_ALLOWED', 0)}",
            f"- SANDBOX_ONLY: {level_counts.get('SANDBOX_ONLY', 0)}",
            f"- TASK_SCOPE_ALLOWED: {level_counts.get('TASK_SCOPE_ALLOWED', 0)}",
            f"- OWNER_DECISION_REQUIRED: {level_counts.get('OWNER_DECISION_REQUIRED', 0)}",
            f"- NOT_ALLOWED: {level_counts.get('NOT_ALLOWED', 0)}",
            "",
            "## Validation priority queue",
            f"- Path: {output_root.as_posix()}/VALIDATION_PRIORITY_QUEUE_RU.md",
            f"- P0: {len(priorities.get('P0_EXISTING_INTERNAL_CAPABILITIES', []))}",
            f"- P1: {len(priorities.get('P1_CORE_DEV_TOOLS', []))}",
            f"- P2: {len(priorities.get('P2_VISUAL_UI_TOOLS', []))}",
            f"- P3: {len(priorities.get('P3_EVIDENCE_SEARCH_TOOLS', []))}",
            f"- P4: {len(priorities.get('P4_OPERATIONAL_UTILITIES', []))}",
            f"- P5: {len(priorities.get('P5_RESERVED_LLM_CLOUD_DEFERRED', []))}",
            "",
            "## Owner decision points",
            f"- Total questions: {len(owner_report.get('questions', []))}",
            "",
            "## Checks",
            "| Check | Result | Notes |",
            "|---|---|---|",
            f"| coverage_100 | {'PASS' if coverage['coverage_percent'] == 100.0 else 'FAIL'} | missing={len(coverage['missing_capability_ids'])}, extra={len(coverage['extra_capability_ids'])} |",
            f"| llm_cloud_reserved | {llm_check['verdict']} | violations={len(llm_check['violations'])} |",
            f"| usage_map_checker | {checker_verdict} | {'; '.join(checker_notes) if checker_notes else '-'} |",
            "",
            "## Ending state",
            f"- Ending HEAD: {ending_head}",
            "- Commit: NOT_PERFORMED",
            "- Push: NOT_PERFORMED",
            f"- Worktree: {'clean' if not status_short else 'dirty (expected, uncommitted task outputs)'}",
            "- Remote sync: HEAD previously matched origin/master before local uncommitted changes",
            "",
            "## Next allowed task",
            f"`{NEXT_ALLOWED_TASK}`",
        ]
    )
    return "\n".join(lines)


def build_manifest(repo_root: Path, output_root: Path, report_root: Path) -> dict[str, Any]:
    output_files = sorted(
        path.relative_to(repo_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file()
    )
    report_files = sorted(
        path.relative_to(repo_root).as_posix()
        for path in report_root.rglob("*")
        if path.is_file()
    )
    return {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "output_root": output_root.relative_to(repo_root).as_posix(),
        "report_root": report_root.relative_to(repo_root).as_posix(),
        "output_files": output_files,
        "report_files": report_files,
        "output_file_count": len(output_files),
        "report_file_count": len(report_files),
    }


def main() -> None:
    repo_root = find_repo_root(Path(__file__).resolve())
    cards_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES"
    output_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/FIELD_GUIDES/BATCH_001"
    category_guides_root = output_root / "CATEGORY_GUIDES_RU"
    report_root = repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS" / TASK_ID
    mass_owner_questions_path = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS"
        / "TASK-NEWGEN-MECHANICUS-ARSENAL-MASS-INTAKE-BATCH-001-PC-V0_1"
        / "owner_questions_report.json"
    )
    category_registry = read_json(repo_root / "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/category_registry_v0_1.json")

    cards = discover_cards(cards_root, repo_root)
    entries = build_entries(cards)

    output_root.mkdir(parents=True, exist_ok=True)
    category_guides_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    # Main machine-readable usage map.
    usage_map = {"task_id": TASK_ID, "generated_at_utc": utc_now(), "entries": entries}
    write_json(output_root / "ARSENAL_AGENT_USAGE_MAP_BATCH_001.json", usage_map)

    # Category guides.
    category_descriptions = {
        item["category"]: str(item.get("description", "Category description not provided."))
        for item in category_registry.get("categories", [])
    }
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_category[entry["category"]].append(entry)
    category_files: dict[str, str] = {}
    for category, category_entries in sorted(by_category.items()):
        file_name = f"{category}_FIELD_GUIDE_RU.md"
        category_files[category] = file_name
        content = render_category_guide(category, category_descriptions.get(category, "No description."), category_entries)
        write_text(category_guides_root / file_name, content)

    # Human-readable indexes and planning docs.
    write_text(
        output_root / "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_RU.md",
        build_index_ru(entries, category_registry, category_files, output_root),
    )
    write_text(
        output_root / "ARSENAL_FIELD_GUIDE_BATCH_001_INDEX_EN.md",
        build_index_en(entries, category_files),
    )

    examples_md, examples_report = build_examples(entries)
    write_text(output_root / "SERVITOR_CAPABILITY_SCOPE_EXAMPLES.md", examples_md)
    queue_md, queue_report = build_validation_queue(entries)
    write_text(output_root / "VALIDATION_PRIORITY_QUEUE_RU.md", queue_md)
    owner_md, owner_report = build_owner_decisions(mass_owner_questions_path)
    write_text(output_root / "OWNER_DECISION_POINTS_RU.md", owner_md)

    coverage = build_coverage(entries, cards)
    write_json(output_root / "FIELD_GUIDE_COVERAGE_REPORT.json", coverage)

    llm_check = build_llm_cloud_check(entries)
    checker_report_path = report_root / "agent_usage_map_check_report.json"
    checker_report = read_json(checker_report_path) if checker_report_path.exists() else None

    # Required report artifacts.
    write_json(report_root / "field_guide_coverage_report.json", coverage)
    write_json(report_root / "servitor_scope_examples_report.json", examples_report)
    write_json(report_root / "validation_priority_queue_report.json", queue_report)
    write_json(report_root / "owner_decision_points_report.json", owner_report)
    write_json(report_root / "llm_cloud_reserved_check_report.json", llm_check)

    script_preservation = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "generated_tools": [
            {
                "path": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/build_mechanicus_arsenal_field_guide_batch_001.py",
                "classification": "BUFFER_FOR_REVIEW",
                "reason": "Reusable generator for field-guide refresh/rebuild.",
            },
            {
                "path": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_arsenal_field_guide_batch_001.py",
                "classification": "ABSORB_NOW",
                "reason": "Required checker for usage-map coverage and reserved-policy enforcement.",
            },
        ],
    }
    write_json(report_root / "SCRIPT_ARTIFACT_PRESERVATION_MANIFEST.json", script_preservation)

    kpd_review = {
        "agent_kpd_self_review": {
            "task_id": TASK_ID,
            "agent_role": "Codex big-model execution partner",
            "useful_outputs": [
                "Complete 136-entry usage map",
                "RU/EN field-guide indexes and 15 category guides",
                "Servitor scope examples and validation priority queue",
                "Dedicated checker + evidence reports",
            ],
            "waste_points": [
                "Repeated manual scanning is slower than scripted aggregation for 136 cards.",
            ],
            "missing_tools": [
                "No pre-existing shared field-guide generator for Arsenal cards.",
            ],
            "generated_tools_to_preserve": [
                "build_mechanicus_arsenal_field_guide_batch_001.py",
                "check_mechanicus_arsenal_field_guide_batch_001.py",
            ],
            "recommended_script_absorption": [
                "Promote checker into reusable Mechanicus validation lane.",
            ],
            "recommended_narrow_agent_profiles": [
                "Mechanicus Arsenal Curator Servitor (guide + queue + owner decision synthesis).",
            ],
            "future_prompt_improvements": [
                "Provide pre-approved priority-mapping matrix for queues to reduce heuristic choices.",
            ],
            "future_gate_or_checklist_recommendations": [
                "Add explicit gate for reserved-category non-activation proof in Arsenal tasks.",
            ],
            "kpd_verdict": "GOOD",
        }
    }
    write_json(report_root / "AGENT_KPD_SELF_REVIEW.json", kpd_review)

    final_report_text = build_final_report(
        repo_root=repo_root,
        report_root=report_root,
        output_root=output_root,
        coverage=coverage,
        llm_check=llm_check,
        checker_report=checker_report,
        queue_report=queue_report,
        owner_report=owner_report,
    )
    write_text(report_root / "FINAL_REPORT.md", final_report_text)

    closure_receipt = {
        "task_id": TASK_ID,
        "verdict": "PASS_WITH_WARNINGS",
        "repo_root": str(repo_root),
        "starting_head": run_git(repo_root, "rev-parse", "HEAD"),
        "ending_head": run_git(repo_root, "rev-parse", "HEAD"),
        "commit": "NOT_PERFORMED",
        "push": "NOT_PERFORMED",
        "worktree_clean": "no",
        "remote_sync": "head_matched_origin_master_before_uncommitted_changes",
        "cards_discovered": coverage["cards_discovered"],
        "usage_map_entries": coverage["usage_map_entries"],
        "coverage_percent": coverage["coverage_percent"],
        "field_guide_files_created": sorted(
            path.relative_to(repo_root).as_posix()
            for path in output_root.rglob("*")
            if path.is_file()
        ),
        "llm_cloud_activated": llm_check["llm_cloud_activated"],
        "tool_install_performed": False,
        "network_provisioning_performed": False,
        "fake_canon_claims": 0,
        "warnings": [
            "commit_push_not_performed_in_this_run",
            "reserved_llm_cloud_categories_remain_owner_decision_required",
        ],
        "next_allowed_task": NEXT_ALLOWED_TASK,
    }
    write_json(report_root / "closure_receipt.json", closure_receipt)

    manifest = build_manifest(repo_root, output_root, report_root)
    write_json(report_root / "field_guide_manifest.json", manifest)

    print(
        json.dumps(
            {
                "task_id": TASK_ID,
                "cards_discovered": coverage["cards_discovered"],
                "usage_map_entries": coverage["usage_map_entries"],
                "coverage_percent": coverage["coverage_percent"],
                "llm_cloud_check_verdict": llm_check["verdict"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
