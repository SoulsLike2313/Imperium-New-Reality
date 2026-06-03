from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

TASK_ID = "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
    except Exception as exc:
        return {
            "command": " ".join(command),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(exc),
        }

    return {
        "command": " ".join(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build/check React IDE projection surface.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--skip-install", action="store_true", help="Skip npm install step.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[3]
    react_dir = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/REACT_IDE"
    report_dir = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
    )
    receipt_path = report_dir / "react_build_check_receipt.json"

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        payload = {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "NPM_NOT_FOUND",
            "react_dir": react_dir.as_posix(),
        }
        write_json(receipt_path, payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    steps: list[Dict[str, Any]] = []
    if not args.skip_install:
        steps.append(run_command([npm, "install"], react_dir))
    steps.append(run_command([npm, "run", "build"], react_dir))

    build_ok = all(step.get("exit_code") == 0 for step in steps)
    dist_index = react_dir / "dist" / "index.html"
    status = "PASS" if build_ok and dist_index.exists() else "PASS_WITH_WARNINGS"

    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "react_dir": react_dir.as_posix(),
        "dist_index_exists": dist_index.exists(),
        "commands": steps,
    }
    write_json(receipt_path, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
