from __future__ import annotations

import argparse
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
MATRIX_JSON_DEFAULT = "owner_approval_matrix_v0_1.json"
RECIPE_OUTPUT_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECIPES/tool_validation_recipes_v0_1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Mechanicus tool validation recipes from owner approval matrix.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--matrix-json", default=MATRIX_JSON_DEFAULT)
    parser.add_argument("--recipe-output", default=RECIPE_OUTPUT_DEFAULT)
    return parser.parse_args()


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=path_hint, text=True).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return path_hint


def build_recipe(row: dict[str, Any]) -> dict[str, Any]:
    capability_id = str(row.get("capability_id", "")).strip()
    category = str(row.get("category", "")).strip()
    install_needed = bool(row.get("install_needed", False))
    install_command_candidate = str(row.get("install_command_candidate", "")).strip()
    detect_command = str(row.get("detect_command", "")).strip()
    validation_command = str(row.get("validation_command", "")).strip()
    stress_test_candidate = str(row.get("stress_test_candidate", "")).strip()
    receipt_required = str(row.get("receipt_required", "")).strip()
    notes_for_owner_ru = str(row.get("notes_for_owner_ru", "")).strip()

    install_stage = {
        "needed": install_needed,
        "candidate_command": install_command_candidate,
        "policy": "NOT_EXECUTED_IN_THIS_TASK; owner gate required for any real install action.",
    }
    if not install_needed:
        install_stage["policy"] = "Install stage skipped because install_needed=false for this capability."

    return {
        "capability_id": capability_id,
        "tool_name": str(row.get("name", capability_id)).strip() or capability_id,
        "category": category,
        "platform": "PC_WINDOWS_PRIMARY",
        "detect": {
            "command": detect_command,
            "expected": "Exit code 0 or explicit evidence that capability context exists.",
        },
        "install": install_stage,
        "validate": {
            "command": validation_command,
            "expected_receipt": receipt_required,
            "owner_decision_required": True,
        },
        "stress": {
            "candidate": stress_test_candidate,
            "target": "repeat detect+validate 3x and compare receipt stability",
        },
        "receipt": {
            "required": receipt_required,
            "storage_rule": "Store under IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECEIPTS/<WAVE_OR_TASK>/",
        },
        "rollback_or_cleanup_notes": (
            "No install performed in this task. If installed in future wave, rollback must be documented "
            "in the wave receipt and provision plan."
        ),
        "owner_notes_ru": notes_for_owner_ru,
    }


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    report_root = (repo_root / args.report_root).resolve()

    matrix_json_path = Path(args.matrix_json)
    if not matrix_json_path.is_absolute():
        matrix_json_path = report_root / matrix_json_path
    recipe_output_path = Path(args.recipe_output)
    if not recipe_output_path.is_absolute():
        recipe_output_path = (repo_root / recipe_output_path).resolve()

    matrix_payload = load_json(matrix_json_path)
    rows = matrix_payload.get("rows", [])
    if not isinstance(rows, list):
        raise RuntimeError("Invalid matrix payload: `rows` must be a list.")

    recipes: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    install_needed_count = 0

    for row in rows:
        if not isinstance(row, dict):
            continue
        recipe = build_recipe(row)
        recipes.append(recipe)
        category_counts[str(recipe.get("category", ""))] += 1
        if bool(recipe.get("install", {}).get("needed", False)):
            install_needed_count += 1

    payload = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "schema_version": "v0_1",
        "source_matrix_json": str(matrix_json_path.relative_to(repo_root).as_posix()),
        "recipe_count": len(recipes),
        "summary": {
            "categories": dict(sorted(category_counts.items())),
            "install_needed_count": install_needed_count,
            "detect_only_count": len(recipes) - install_needed_count,
        },
        "recipes": recipes,
    }
    write_json(recipe_output_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
