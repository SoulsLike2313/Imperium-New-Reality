from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "REPORTS"
SCHEMA_PATH = ROOT / "SCHEMAS" / "concept_card.schema.json"
SCREENSHOT_DIR = ROOT / "SCREENSHOTS"

CONCEPT_DIRS = [
    "CONCEPT_A_NEURAL_THRONE_CORE",
    "CONCEPT_B_MECHANICUS_FORGE_CORTEX",
    "CONCEPT_C_HOLOGRAPH_COMMAND_SPINE",
    "CONCEPT_D_SECOND_MIND_WAR_ROOM",
    "CONCEPT_E_LIVING_ORGAN_MAP",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_concept_card(card_path: Path, required: list[str]) -> list[str]:
    errors: list[str] = []
    try:
        data = load_json(card_path)
    except Exception as exc:  # noqa: BLE001
        return [f"invalid json: {exc}"]

    for field in required:
        if field not in data:
            errors.append(f"missing field: {field}")

    strengths = data.get("strengths")
    risks = data.get("risks")
    if not isinstance(strengths, list) or not strengths:
        errors.append("strengths must be non-empty array")
    if not isinstance(risks, list) or not risks:
        errors.append("risks must be non-empty array")
    return errors


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    required_fields = schema.get("required", [])

    checks: list[dict[str, Any]] = []
    concept_count = 0

    for idx, folder in enumerate(CONCEPT_DIRS):
        concept_id = chr(ord("A") + idx)
        concept_path = ROOT / folder
        html_path = concept_path / "index.html"
        card_path = concept_path / "concept_card.json"
        notes_path = concept_path / "concept_notes.md"
        shot_1366 = SCREENSHOT_DIR / f"{concept_id}_1366x768.png"
        shot_1920 = SCREENSHOT_DIR / f"{concept_id}_1920x1080.png"

        exists_ok = concept_path.exists() and html_path.exists() and card_path.exists() and notes_path.exists()
        checks.append(
            {
                "name": f"{concept_id}_concept_files",
                "path": str(concept_path),
                "ok": exists_ok,
                "errors": [] if exists_ok else ["missing concept folder or required files"],
            }
        )

        card_errors = check_concept_card(card_path, required_fields) if card_path.exists() else ["concept_card.json missing"]
        checks.append(
            {
                "name": f"{concept_id}_concept_card_schema_min",
                "path": str(card_path),
                "ok": not card_errors,
                "errors": card_errors,
            }
        )

        shots_ok = shot_1366.exists() and shot_1920.exists()
        checks.append(
            {
                "name": f"{concept_id}_screenshots_present",
                "path": str(SCREENSHOT_DIR),
                "ok": shots_ok,
                "errors": [] if shots_ok else ["missing 1366x768 or 1920x1080 screenshot"],
            }
        )

        if exists_ok and not card_errors and shots_ok:
            concept_count += 1

    matrix_path = REPORTS / "comparison_matrix.md"
    owner_guide_path = REPORTS / "owner_selection_guide_ru.md"
    baseline_path = REPORTS / "baseline_diagnosis.md"

    checks.append(
        {
            "name": "comparison_matrix_present",
            "path": str(matrix_path),
            "ok": matrix_path.exists(),
            "errors": [] if matrix_path.exists() else ["comparison_matrix.md missing"],
        }
    )

    checks.append(
        {
            "name": "owner_selection_guide_present",
            "path": str(owner_guide_path),
            "ok": owner_guide_path.exists(),
            "errors": [] if owner_guide_path.exists() else ["owner_selection_guide_ru.md missing"],
        }
    )

    checks.append(
        {
            "name": "baseline_diagnosis_present",
            "path": str(baseline_path),
            "ok": baseline_path.exists(),
            "errors": [] if baseline_path.exists() else ["baseline_diagnosis.md missing"],
        }
    )

    pass_ok = concept_count >= 3 and all(check["ok"] for check in checks)
    verdict = "CONCEPT_CANDIDATES_READY" if pass_ok else "BLOCK"

    report = {
        "task_id": "TASK-20260520-NEWGEN-VISUAL-CONCEPT-STRIKE-MULTI-CONCEPT-PC-V0_1",
        "generated_at_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "concept_count": concept_count,
        "validator": "validate_concepts.py",
        "checks": checks,
        "verdict": verdict,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS / "validation_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path)
    print(verdict)


if __name__ == "__main__":
    main()
