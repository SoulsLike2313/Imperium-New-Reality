from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]


def _labels(lang: str) -> dict[str, str]:
    if lang == "ru":
        return {
            "title": "ADMINISTRATUM READ-ONLY INSPECTOR V0.1",
            "current_head": "Tekushchiy accepted HEAD",
            "accepted_points": "Accepted points",
            "active_organs": "Aktivnye organy",
            "pending_tasks": "Sleduyushchie zadachi",
            "organ_cards": "Registratsionnye kartochki organov",
            "block_seed": "Seed block registry",
            "warnings": "Preduprezhdeniya",
            "future": "Budushchee (future)",
        }
    return {
        "title": "ADMINISTRATUM READ-ONLY INSPECTOR V0.1",
        "current_head": "Current accepted HEAD",
        "accepted_points": "Accepted points",
        "active_organs": "Active organs",
        "pending_tasks": "Pending next tasks",
        "organ_cards": "Organ registration cards",
        "block_seed": "Seed block registry",
        "warnings": "Warnings",
        "future": "Future",
    }


def _required_paths() -> dict[str, Path]:
    return {
        "current_head": ADMIN_ROOT / "CURRENT_TRUTH" / "current_head_card_v0_1.json",
        "accepted_points": ADMIN_ROOT / "CURRENT_TRUTH" / "accepted_points_index_v0_1.json",
        "active_organs": ADMIN_ROOT / "CURRENT_TRUTH" / "active_organs_index_v0_1.json",
        "pending_tasks": ADMIN_ROOT / "CURRENT_TRUTH" / "pending_next_tasks_index_v0_1.json",
        "legacy_warn": ADMIN_ROOT / "CURRENT_TRUTH" / "legacy_warn_index_v0_1.json",
        "mechanicus_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "mechanicus_organ_card_v0_1.json",
        "officio_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "officio_agentis_organ_card_v0_1.json",
        "block_seed": ADMIN_ROOT / "BLOCKS" / "block_registry_seed_v0_1.json",
    }


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"invalid_json: {exc}"


def build_bundle() -> tuple[dict[str, Any], list[str]]:
    bundle: dict[str, Any] = {}
    issues: list[str] = []
    for key, path in _required_paths().items():
        data, error = _load_json(path)
        bundle[key] = data
        if error:
            issues.append(f"{key}: {error} ({path.as_posix()})")
    return bundle, issues


def render_text(bundle: dict[str, Any], issues: list[str], lang: str) -> None:
    l = _labels(lang)
    print(l["title"])
    print("=" * len(l["title"]))

    current_head = (bundle.get("current_head") or {}).get("current_head", "UNKNOWN")
    print(f"{l['current_head']}: {current_head}")

    print(f"\n[{l['accepted_points']}]")
    for point in (bundle.get("accepted_points") or {}).get("points", []):
        if isinstance(point, dict):
            organ = point.get("organ_id", "UNKNOWN")
            task_id = point.get("task_id", "UNKNOWN")
            head = point.get("accepted_head", "UNKNOWN")
            status = point.get("status", "UNKNOWN")
            print(f"- {organ}: {task_id} -> {head} ({status})")

    print(f"\n[{l['active_organs']}]")
    for organ in (bundle.get("active_organs") or {}).get("organs", []):
        if isinstance(organ, dict):
            print(f"- {organ.get('organ_id', 'UNKNOWN')}: {organ.get('registration_status', 'UNKNOWN')}")

    print(f"\n[{l['pending_tasks']}]")
    for task in (bundle.get("pending_tasks") or {}).get("pending_next_tasks", []):
        if isinstance(task, dict):
            print(f"- {task.get('task_id', 'UNKNOWN')} ({task.get('status', 'UNKNOWN')})")

    print(f"\n[{l['organ_cards']}]")
    for key in ("mechanicus_card", "officio_card"):
        card = bundle.get(key) or {}
        print(f"- {card.get('organ_id', 'UNKNOWN')}: {card.get('status', 'UNKNOWN')}")

    block_count = len((bundle.get("block_seed") or {}).get("blocks", []))
    print(f"\n[{l['block_seed']}]")
    print(f"- blocks: {block_count}")
    print(f"- {l['future']}: WARP/CLI schemas are seed-only")

    print(f"\n[{l['warnings']}]")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        for entry in (bundle.get("legacy_warn") or {}).get("warn_entries", []):
            if isinstance(entry, dict):
                print(f"- {entry.get('warn_id', 'WARN')}: {entry.get('summary', '')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only inspector for Administratum cards and current truth indexes.")
    parser.add_argument("--lang", choices=["en", "ru"], default="en")
    parser.add_argument("--json", action="store_true", help="Print bundle as JSON.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if required files are missing/invalid.")
    parser.add_argument("--smoke", action="store_true", help="Print smoke marker.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle, issues = build_bundle()
    status = "PASS" if not issues else "WARN"

    if args.json:
        print(
            json.dumps(
                {
                    "organ_id": "ADMINISTRATUM",
                    "status": status,
                    "issues": issues,
                    "bundle": bundle,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        render_text(bundle, issues, args.lang)

    if args.smoke:
        print("SMOKE_OK_ADMINISTRATUM_TUI_V0_1")

    if args.strict and issues:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
