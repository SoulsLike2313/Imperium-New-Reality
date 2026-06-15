from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_cards(cards_root: Path) -> list[tuple[dict[str, Any], Path]]:
    cards: list[tuple[dict[str, Any], Path]] = []
    for path in sorted(cards_root.rglob("*.json")):
        try:
            payload = load_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if {"capability_id", "status", "category"}.issubset(payload.keys()):
            cards.append((payload, path))
    return cards


def canon_evidence_missing(repo_root: Path, card: dict[str, Any], arsenal_root: Path) -> list[str]:
    missing: list[str] = []
    evidence_paths = card.get("canon_evidence_paths", [])
    if isinstance(evidence_paths, list) and evidence_paths:
        for rel in evidence_paths:
            if not isinstance(rel, str):
                missing.append("<non-string-evidence-path>")
                continue
            if not (repo_root / rel).exists():
                missing.append(rel)
        return missing

    promoted_by = str(card.get("promoted_by_receipt", "")).strip()
    if promoted_by.endswith(".json"):
        candidate_paths = [
            repo_root / promoted_by,
            arsenal_root / "RECEIPTS" / promoted_by,
        ]
        if any(path.exists() for path in candidate_paths):
            return []
        return [promoted_by]
    return ["missing_canon_evidence_paths_or_promoted_by_receipt"]


def run_detection(repo_root: Path, cards_root: Path, task_id: str) -> dict[str, Any]:
    arsenal_root = repo_root / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "ARSENAL"
    cards = discover_cards(cards_root)

    fake_canon_entries: list[dict[str, Any]] = []
    reserved_canon_entries: list[dict[str, Any]] = []
    canon_requires_install: list[dict[str, Any]] = []
    canon_count = 0

    for card, card_path in cards:
        capability_id = str(card.get("capability_id", "UNKNOWN"))
        status = str(card.get("status", ""))
        category = str(card.get("category", ""))
        if status != "CANON":
            continue

        canon_count += 1
        missing = canon_evidence_missing(repo_root, card, arsenal_root)
        if missing:
            fake_canon_entries.append(
                {
                    "capability_id": capability_id,
                    "category": category,
                    "card_path": card_path.relative_to(repo_root).as_posix(),
                    "missing_evidence": missing,
                }
            )

        if category in RESERVED_CATEGORIES:
            reserved_canon_entries.append(
                {
                    "capability_id": capability_id,
                    "category": category,
                    "card_path": card_path.relative_to(repo_root).as_posix(),
                }
            )

        if bool(card.get("install_required", False)):
            canon_requires_install.append(
                {
                    "capability_id": capability_id,
                    "card_path": card_path.relative_to(repo_root).as_posix(),
                }
            )

    verdict = "PASS"
    if fake_canon_entries or reserved_canon_entries:
        verdict = "FAIL"
    elif canon_requires_install:
        verdict = "PASS_WITH_WARNINGS"

    return {
        "task_id": task_id,
        "checker": "mechanicus_fake_canon_detector_v0_2.py",
        "checked_at_utc": utc_now(),
        "verdict": verdict,
        "summary": {
            "cards_scanned": len(cards),
            "canon_count": canon_count,
            "fake_canon_count": len(fake_canon_entries),
            "reserved_canon_count": len(reserved_canon_entries),
            "canon_requires_install_count": len(canon_requires_install),
        },
        "fake_canon_entries": fake_canon_entries,
        "reserved_canon_entries": reserved_canon_entries,
        "canon_requires_install_entries": canon_requires_install,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect fake CANON entries in Mechanicus Arsenal cards.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument(
        "--cards-root",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/CATEGORIES",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    cards_root = (repo_root / args.cards_root).resolve()
    payload = run_detection(repo_root=repo_root, cards_root=cards_root, task_id=args.task_id)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"task_id": args.task_id, "verdict": payload["verdict"]}, ensure_ascii=False))
    return 0 if payload["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
