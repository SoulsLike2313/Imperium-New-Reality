from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"

PROBE_COMMANDS = [
    ("node", ["node", "--version"]),
    ("npm", ["npm.cmd", "--version"]),
    ("npx_playwright", ["npx.cmd", "playwright", "--version"]),
    ("rustc", ["rustc", "--version"]),
    ("cargo", ["cargo", "--version"]),
    ("cargo_tauri", ["cargo", "tauri", "--version"]),
    ("tauri_cmd", ["tauri", "--version"]),
    ("electron", ["electron", "--version"]),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_probe(name: str, command: List[str]) -> Dict[str, Any]:
    executable = command[0]
    available = shutil.which(executable) is not None
    if not available:
        return {
            "name": name,
            "command": " ".join(command),
            "available": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
        }

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return {
            "name": name,
            "command": " ".join(command),
            "available": True,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(exc),
        }

    return {
        "name": name,
        "command": " ".join(command),
        "available": True,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build_decision(probes: List[Dict[str, Any]]) -> Dict[str, Any]:
    probe_by_name = {item["name"]: item for item in probes}
    tauri_ok = False
    tauri_reasons: List[str] = []

    for key in ("cargo_tauri", "tauri_cmd"):
        item = probe_by_name.get(key, {})
        if item.get("available") and item.get("exit_code") == 0:
            tauri_ok = True
            tauri_reasons.append(f"{key} ready")

    electron_item = probe_by_name.get("electron", {})
    electron_ok = bool(electron_item.get("available") and electron_item.get("exit_code") == 0)

    if tauri_ok:
        status = "PASS"
        decision = "TAURI_PREFERRED"
        note = "Tauri toolchain appears callable from current environment."
        prerequisites_missing: List[str] = []
    elif electron_ok:
        status = "PASS_WITH_WARNINGS"
        decision = "ELECTRON_FALLBACK"
        note = "Tauri is unavailable; Electron fallback binary exists."
        prerequisites_missing = ["TAURI_TOOLCHAIN"]
    else:
        status = "PASS_WITH_WARNINGS"
        decision = "REACT_WEB_ONLY_SCAFFOLD"
        note = "Neither Tauri nor Electron CLI is available. Keep web projection as primary runnable surface."
        prerequisites_missing = ["TAURI_TOOLCHAIN", "ELECTRON_BINARY"]

    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "decision": decision,
        "note": note,
        "tauri_reasons": tauri_reasons,
        "prerequisites_missing": prerequisites_missing,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe desktop shell toolchain for Agent IDE web-shell task.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[3]
    desktop_shell_dir = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/DESKTOP_SHELL"
    probe_path = desktop_shell_dir / "tauri_probe_receipt.json"
    decision_path = desktop_shell_dir / "tauri_or_electron_decision_v0_1.json"

    probes = [run_probe(name, command) for name, command in PROBE_COMMANDS]
    probe_payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": "PASS",
        "probes": probes,
    }
    decision_payload = build_decision(probes)

    write_json(probe_path, probe_payload)
    write_json(decision_path, decision_payload)

    print(
        json.dumps(
            {
                "probe_receipt_path": probe_path.as_posix(),
                "decision_receipt_path": decision_path.as_posix(),
                "decision": decision_payload,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
