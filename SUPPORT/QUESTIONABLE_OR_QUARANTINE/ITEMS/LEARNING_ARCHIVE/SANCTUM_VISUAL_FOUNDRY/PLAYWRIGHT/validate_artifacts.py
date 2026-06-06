from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "SCHEMAS"
REPORTS = ROOT / "REPORTS"
LAB_INDEX = ROOT / "LAB" / "index.html"
LAB_STYLES = ROOT / "LAB" / "styles.css"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_fields(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"missing required field: {field}")
    return errors


def build_report() -> dict[str, Any]:
    token_json_path = ROOT / "TOKENS" / "design_tokens_mechanicus_console_v0_2.json"
    token_css_path = ROOT / "TOKENS" / "design_tokens_mechanicus_console_v0_2.css"
    token_usage_path = ROOT / "TOKENS" / "token_usage_report.md"
    screenshot_index_path = ROOT / "SCREENSHOTS" / "screenshot_index.json"
    before_after_path = ROOT / "REPORTS" / "before_after_review.md"

    schema_path = SCHEMAS / "design_tokens_min.schema.json"
    token_schema = load_json(schema_path)
    token_data = load_json(token_json_path)
    screenshot_index = load_json(screenshot_index_path)

    checks: list[dict[str, Any]] = []

    token_errors = validate_required_fields(token_data, token_schema)
    checks.append(
        {
            "name": "tokens_v0_2_schema_min",
            "path": str(token_json_path),
            "ok": not token_errors,
            "errors": token_errors,
        }
    )

    css_ok = token_css_path.exists() and token_css_path.stat().st_size > 100
    checks.append(
        {
            "name": "tokens_v0_2_css_export",
            "path": str(token_css_path),
            "ok": css_ok,
            "errors": [] if css_ok else ["design_tokens_mechanicus_console_v0_2.css missing or empty"],
        }
    )

    usage_ok = token_usage_path.exists() and token_usage_path.stat().st_size > 120
    checks.append(
        {
            "name": "token_usage_report_exists",
            "path": str(token_usage_path),
            "ok": usage_ok,
            "errors": [] if usage_ok else ["token_usage_report.md missing or too short"],
        }
    )

    lab_index_text = LAB_INDEX.read_text(encoding="utf-8")
    lab_styles_text = LAB_STYLES.read_text(encoding="utf-8")

    token_link_ok = "design_tokens_mechanicus_console_v0_2.css" in lab_index_text
    checks.append(
        {
            "name": "lab_links_tokens_v0_2",
            "path": str(LAB_INDEX),
            "ok": token_link_ok,
            "errors": [] if token_link_ok else ["LAB/index.html does not link token css v0_2"],
        }
    )

    token_vars_ok = "--vf2-" in lab_styles_text
    checks.append(
        {
            "name": "lab_consumes_token_variables",
            "path": str(LAB_STYLES),
            "ok": token_vars_ok,
            "errors": [] if token_vars_ok else ["LAB/styles.css does not consume vf2 token variables"],
        }
    )

    required_shots = {
        "brain_forge_iter_full_1366x768.png",
        "brain_forge_iter_full_1920x1080.png",
        "brain_forge_iter_brain_focus.png",
        "brain_forge_iter_right_panel_focus.png",
        "brain_forge_iter_raw_secondary.png",
    }
    files = screenshot_index.get("files", [])
    shot_ok = isinstance(files, list) and required_shots.issubset(set(files))
    checks.append(
        {
            "name": "required_screenshot_evidence",
            "path": str(screenshot_index_path),
            "ok": shot_ok,
            "errors": [] if shot_ok else ["required screenshot set missing in screenshot_index"],
        }
    )

    before_after_ok = before_after_path.exists() and before_after_path.stat().st_size > 140
    checks.append(
        {
            "name": "before_after_review_exists",
            "path": str(before_after_path),
            "ok": before_after_ok,
            "errors": [] if before_after_ok else ["before_after_review.md missing or too short"],
        }
    )

    verdict = "PASS" if all(item["ok"] for item in checks) else "BLOCK"
    return {
        "task_id": "TASK-20260520-NEWGEN-VISUAL-FOUNDRY-BRAIN-FORGE-ITERATION-TOKEN-REPAIR-PC-V0_1",
        "generated_at_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "validator": "validate_artifacts.py",
        "checks": checks,
        "verdict": verdict,
    }


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = build_report()
    out_path = REPORTS / "validation_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path)
    print(report["verdict"])


if __name__ == "__main__":
    main()
