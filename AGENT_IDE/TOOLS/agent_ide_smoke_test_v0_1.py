from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import sys

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
            "E:/IMPERIUM/IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
            "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC/ide_smoke_receipt.json"
        ),
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
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

    receipt_path = Path(args.receipt_out).resolve()
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))

    return 0 if status in {"PASS", "WARN_ACCEPTED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
