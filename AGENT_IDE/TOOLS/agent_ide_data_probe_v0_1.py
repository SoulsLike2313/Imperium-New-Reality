from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import sys

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root, resolve_output_path  # noqa: E402

APP_DIR = Path(__file__).resolve().parents[1] / "APP"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from agent_ide_data_loader_v0_1 import build_view_model  # noqa: E402


TASK_ID = "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC"
REQUIRED_SOURCE_KEYS = {"file_passports", "file_atlas_index", "organ_file_map"}


def run_probe(repo_root: Path | None = None) -> Dict[str, Any]:
    model = build_view_model(repo_root).to_dict()
    truth = model.get("truth", {})
    loaded_sources = set(truth.get("loaded_sources", {}).keys())
    missing_required = sorted(REQUIRED_SOURCE_KEYS - loaded_sources)

    warnings: List[str] = [str(x) for x in model.get("warnings", [])]
    unknown_count = int(model.get("unknown_file_kind_count", 0))
    organs_visible = len(model.get("organs", []))
    passport_count = len(model.get("file_passports", []))

    status = "PASS"
    if missing_required:
        status = "FAIL"
    elif warnings:
        status = "WARN_ACCEPTED"

    return {
        "task_id": TASK_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "organs_visible": organs_visible,
        "passport_count": passport_count,
        "unknown_file_kind_count": unknown_count,
        "loaded_source_keys": sorted(loaded_sources),
        "missing_required_sources": missing_required,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Agent IDE data probe")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument(
        "--receipt-out",
        default=(
            "AGENT_IDE/REPORTS/"
            "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC/ide_data_probe_receipt.json"
        ),
    )
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    receipt_path = resolve_output_path(args.receipt_out, repo_root)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    probe = run_probe(repo_root)
    receipt_path.write_text(json.dumps(probe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(probe, indent=2, ensure_ascii=False))

    return 0 if probe["status"] in {"PASS", "WARN_ACCEPTED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
