from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
ATLAS_ROOT = ADMIN_ROOT / "FILE_ATLAS"


def _labels(lang: str) -> dict[str, str]:
    if lang == "ru":
        return {
            "title": "ADMINISTRATUM FILE ATLAS INSPECTOR V0.1",
            "organs": "Органы и объем файлов",
            "edits": "Высокий приоритет редактирования",
            "language": "Поверхности language gate",
            "route": "Маршрутные/connection поверхности",
            "gaps": "Пробелы и блокеры",
            "successes": "Успехи",
            "next": "Следующая задача",
            "issues": "Проблемы чтения данных",
        }
    return {
        "title": "ADMINISTRATUM FILE ATLAS INSPECTOR V0.1",
        "organs": "Organs and file volume",
        "edits": "High-priority edit surfaces",
        "language": "Language gate surfaces",
        "route": "Route/connection surfaces",
        "gaps": "Gaps and blockers",
        "successes": "Successes",
        "next": "Next task",
        "issues": "Data loading issues",
    }


def _required_paths() -> dict[str, Path]:
    return {
        "index": ATLAS_ROOT / "file_atlas_index_v0_1.json",
        "passports": ATLAS_ROOT / "file_passports_v0_1.jsonl",
        "language": ATLAS_ROOT / "language_gate_surface_index_v0_1.json",
        "route": ATLAS_ROOT / "route_connection_surface_index_v0_1.json",
        "pain": ATLAS_ROOT / "owner_pain_to_file_map_v0_1.json",
        "gap": ATLAS_ROOT / "gap_success_index_v0_1.json",
    }


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json: {exc}"


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
    if not path.exists():
        return None, "missing"
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            item = json.loads(stripped)
            if isinstance(item, dict):
                rows.append(item)
        return rows, None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_jsonl: {exc}"


def build_bundle() -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    bundle: dict[str, Any] = {}
    for key, path in _required_paths().items():
        if key == "passports":
            data, error = _read_jsonl(path)
        else:
            data, error = _read_json(path)
        bundle[key] = data
        if error:
            issues.append(f"{key}: {error} ({path.as_posix()})")
    return bundle, issues


def render_text(bundle: dict[str, Any], issues: list[str], lang: str) -> None:
    labels = _labels(lang)
    index = bundle.get("index") or {}
    passports = bundle.get("passports") or []
    language = bundle.get("language") or {}
    route = bundle.get("route") or {}
    gap = bundle.get("gap") or {}

    print(labels["title"])
    print("=" * len(labels["title"]))

    print(f"\n[{labels['organs']}]")
    for organ_id, count in sorted((index.get("counts_by_organ") or {}).items()):
        print(f"- {organ_id}: {count}")
    print(f"- total_files: {index.get('total_files_indexed', 0)}")

    print(f"\n[{labels['edits']}]")
    high_edit_paths = [
        p.get("path")
        for p in passports
        if isinstance(p, dict) and p.get("drilldown_priority") == "HIGH" and p.get("edit_surface") in {"YES", "CAUTION"}
    ][:20]
    for path in high_edit_paths:
        print(f"- {path}")

    print(f"\n[{labels['language']}]")
    for path in (language.get("owner_facing_language_rules") or [])[:12]:
        print(f"- {path}")
    for path in (language.get("stop_warn_pass_files") or [])[:6]:
        print(f"- {path}")

    print(f"\n[{labels['route']}]")
    print(f"- required_alias: {route.get('required_alias', 'N/A')}")
    print(f"- alias_detected: {route.get('alias_detected', False)}")
    for path in (route.get("alias_evidence_paths") or [])[:12]:
        print(f"- {path}")

    print(f"\n[{labels['gaps']}]")
    for item in gap.get("gaps", []):
        if isinstance(item, dict):
            print(f"- {item.get('gap_id', 'UNKNOWN')}: {item.get('status', 'UNKNOWN')} :: {item.get('summary', '')}")

    print(f"\n[{labels['successes']}]")
    for item in gap.get("successes", []):
        if isinstance(item, dict):
            print(f"- {item.get('success_id', 'UNKNOWN')}: {item.get('status', 'UNKNOWN')} :: {item.get('summary', '')}")

    print(f"\n[{labels['next']}]")
    print("- TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC")

    print(f"\n[{labels['issues']}]")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("- none")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only inspector for Administratum File Atlas outputs.")
    parser.add_argument("--lang", choices=["en", "ru"], default="en")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if required data files are missing/invalid.")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle, issues = build_bundle()

    if args.json:
        print(
            json.dumps(
                {
                    "organ_id": "ADMINISTRATUM",
                    "surface": "FILE_ATLAS_TUI",
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
        print("SMOKE_OK_ADMINISTRATUM_FILE_ATLAS_TUI_V0_1")

    if args.strict and issues:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
