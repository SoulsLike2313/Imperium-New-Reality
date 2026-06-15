from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

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

from agent_ide_app_v0_1 import run_smoke  # noqa: E402


TASK_ID = "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Agent IDE smoke test")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument(
        "--receipt-out",
        default=(
            "AGENT_IDE/REPORTS/"
            "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC/ide_smoke_receipt.json"
        ),
    )
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    summary = run_smoke(repo_root)

    status = "PASS"
    notes = []
    if int(summary.get("organs_visible", 0)) < 5:
        status = "FAIL"
        notes.append("Expected at least five organs in view model.")
    if int(summary.get("passports", 0)) == 0:
        status = "FAIL"
        notes.append("No file passports loaded.")
    if not bool(summary.get("route_alias_visible", False)):
        if status != "FAIL":
            status = "WARN_ACCEPTED"
        notes.append("Route alias visibility missing in current data.")

    receipt: Dict[str, Any] = {
        "task_id": TASK_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": summary,
        "notes": notes,
    }

    receipt_path = resolve_output_path(args.receipt_out, repo_root)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))

    return 0 if status in {"PASS", "WARN_ACCEPTED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
