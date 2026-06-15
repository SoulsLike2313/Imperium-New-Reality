from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
ASTRONOMICON_ROOT = HERE.parents[1]
DEFAULT_TUI_PATH = ASTRONOMICON_ROOT / "TUI" / "astronomicon_tui_v0_1.py"


def run_smoke(tui_path: Path) -> dict[str, Any]:
    command = [sys.executable, str(tui_path), "--smoke", "--plain-json"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    smoke_ok = "SMOKE_OK_ASTRONOMICON_TUI_V0_1" in stdout and completed.returncode == 0
    verdict = "PASS" if smoke_ok else "BLOCK"

    return {
        "schema_version": "astronomicon.tui_smoke_report.v0_1",
        "checker": "astronomicon_tui_smoke_v0_1.py",
        "tui_path": str(tui_path),
        "command": command,
        "returncode": completed.returncode,
        "verdict": verdict,
        "smoke_marker_found": "SMOKE_OK_ASTRONOMICON_TUI_V0_1" in stdout,
        "stdout": stdout,
        "stderr": stderr,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Astronomicon TUI smoke check.")
    parser.add_argument("--tui", default=str(DEFAULT_TUI_PATH))
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_smoke(Path(args.tui))

    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
