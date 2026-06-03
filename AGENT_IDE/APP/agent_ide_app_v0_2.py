from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import sys

APP_DIR = Path(__file__).resolve().parent
VIEW_MODEL_DIR = APP_DIR.parent / "VIEW_MODEL"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(VIEW_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(VIEW_MODEL_DIR))

from agent_ide_app_v0_1 import AgentIdeApp, I18N  # noqa: E402
from agent_ide_view_model_builder_v0_2 import (  # noqa: E402
    TASK_ID,
    build_and_persist_models,
    build_models,
    discover_repo_root,
)


I18N["en"]["app_title"] = "IMPERIUM Agent IDE V0.2 (Dual Surface Read-only)"
I18N["ru"]["app_title"] = "IMPERIUM Agent IDE V0.2 (Dual Surface, только чтение)"


def run_smoke(repo_root: Path | None = None) -> Dict[str, Any]:
    full_model, dashboard_model, _block_model = build_models(repo_root)
    route_surface = full_model.get("route_surface", {})
    summary = {
        "task_id": TASK_ID,
        "organs_visible": len(full_model.get("organs", [])),
        "passports": len(full_model.get("file_passports", [])),
        "warnings": len(full_model.get("warnings", [])),
        "unknown_file_kind_count": full_model.get("unknown_file_kind_count", 0),
        "route_alias_required": route_surface.get("required_alias", ""),
        "route_alias_visible": route_surface.get("imperium_vm3_visible", False),
        "owner_pain_count": dashboard_model.get("owner_pain_surface", {}).get("pain_count", 0),
        "projection_restricted_count": dashboard_model.get("projection_guard", {}).get(
            "private_local_restricted_count", 0
        ),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM Agent IDE V0.2 dual-surface desktop app")
    parser.add_argument("--lang", choices=["en", "ru"], default="en")
    parser.add_argument("--smoke", action="store_true", help="Run smoke mode without GUI.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()

    if args.smoke:
        summary = run_smoke(repo_root)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    build_and_persist_models(repo_root)
    full_model, _dashboard_model, _block_model = build_models(repo_root)
    app = AgentIdeApp(model=full_model, language=args.lang)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
