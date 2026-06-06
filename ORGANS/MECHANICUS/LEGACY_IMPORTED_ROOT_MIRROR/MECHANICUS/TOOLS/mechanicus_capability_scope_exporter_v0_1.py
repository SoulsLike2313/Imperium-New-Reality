from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_cards(cards_root: Path, repo_root: Path) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for path in sorted(cards_root.rglob("*.json")):
        try:
            payload = load_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if {"capability_id", "status", "category"}.issubset(payload.keys()):
            payload["_card_path"] = path.relative_to(repo_root).as_posix()
            cards.append(payload)
    return cards


def load_validation_index(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_json(path)
    results = payload.get("results", [])
    if not isinstance(results, list):
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    for item in results:
        if not isinstance(item, dict):
            continue
        capability_id = str(item.get("capability_id", "")).strip()
        if capability_id:
            mapped[capability_id] = item
    return mapped


def build_scope_export(
    *,
    task_id: str,
    cards: list[dict[str, Any]],
    validation_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    canon_allowed: list[str] = []
    sandbox_only: list[str] = []
    candidate_context_only: list[str] = []
    owner_decision_required: list[str] = []
    forbidden: list[str] = []

    promoted_this_batch: list[str] = []
    validated_missing: list[str] = []

    category_counts = Counter(str(card.get("category", "")) for card in cards)
    status_counts = Counter(str(card.get("status", "")) for card in cards)

    for card in cards:
        capability_id = str(card.get("capability_id", "")).strip()
        status = str(card.get("status", "")).strip()
        category = str(card.get("category", "")).strip()
        reserved = category in RESERVED_CATEGORIES or bool(card.get("reserved"))

        validation_row = validation_index.get(capability_id, {})
        recommendation = str(validation_row.get("promotion_recommendation", "")).strip()
        verdict = str(validation_row.get("validation_verdict", "")).strip()

        if recommendation == "PROMOTE_SANDBOX":
            promoted_this_batch.append(capability_id)
        if verdict == "MISSING":
            validated_missing.append(capability_id)

        if status in {"QUARANTINE", "REJECTED"}:
            forbidden.append(capability_id)
            continue
        if reserved:
            owner_decision_required.append(capability_id)
            continue
        if status == "CANON":
            canon_allowed.append(capability_id)
            continue
        if status == "SANDBOX":
            sandbox_only.append(capability_id)
            continue
        candidate_context_only.append(capability_id)

    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "exporter": "mechanicus_capability_scope_exporter_v0_1.py",
        "summary": {
            "total_cards": len(cards),
            "category_count": len(category_counts),
            "status_counts": dict(status_counts),
            "canon_allowed_count": len(canon_allowed),
            "sandbox_only_count": len(sandbox_only),
            "candidate_context_only_count": len(candidate_context_only),
            "owner_decision_required_count": len(owner_decision_required),
            "forbidden_count": len(forbidden),
            "promoted_this_batch_count": len(promoted_this_batch),
            "validated_missing_count": len(validated_missing),
        },
        "scope_export": {
            "canon_allowed": sorted(canon_allowed),
            "sandbox_only": sorted(sandbox_only),
            "candidate_context_only": sorted(candidate_context_only),
            "owner_decision_required": sorted(owner_decision_required),
            "forbidden": sorted(forbidden),
        },
        "validation_signals": {
            "promoted_this_batch": sorted(promoted_this_batch),
            "validated_missing": sorted(validated_missing),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export capability scope slices for future Mechanicus tasks.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument(
        "--cards-root",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES",
    )
    parser.add_argument(
        "--validation-results",
        default="",
        help="Optional path to validation_results.json for promotion signals.",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    cards_root = (repo_root / args.cards_root).resolve()
    cards = discover_cards(cards_root=cards_root, repo_root=repo_root)
    validation_index = (
        load_validation_index((repo_root / args.validation_results).resolve())
        if args.validation_results
        else {}
    )

    payload = build_scope_export(
        task_id=args.task_id,
        cards=cards,
        validation_index=validation_index,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "canon_allowed_count": payload["summary"]["canon_allowed_count"],
                "sandbox_only_count": payload["summary"]["sandbox_only_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
