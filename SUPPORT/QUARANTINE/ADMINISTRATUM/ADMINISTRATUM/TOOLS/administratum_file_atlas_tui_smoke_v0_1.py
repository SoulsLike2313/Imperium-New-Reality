from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-ADMINISTRATUM-FILE-ATLAS-PASSPORT-INDEX-VM3-V0_1"
HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
REPORT_ROOT = ADMIN_ROOT / "REPORTS" / TASK_ID
DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "tui_smoke_receipt.json"
TUI_PATH = ADMIN_ROOT / "TUI" / "administratum_file_atlas_tui_v0_1.py"


def _enforce_output_path(path: Path, allow_external: bool) -> None:
    if allow_external:
        return
    resolved_report = REPORT_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_report not in resolved_path.parents and resolved_path != resolved_report:
        raise SystemExit(f"Output path must stay under {resolved_report} unless --allow-external-output is used.")


def run_smoke(lang: str) -> dict[str, Any]:
    cmd = [sys.executable, str(TUI_PATH), "--strict", "--smoke", "--lang", lang]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    marker = "SMOKE_OK_ADMINISTRATUM_FILE_ATLAS_TUI_V0_1"
    marker_found = marker in proc.stdout
    status = "PASS" if proc.returncode == 0 and marker_found else "FAIL"
    return {
        "task_id": TASK_ID,
        "checker": "administratum_file_atlas_tui_smoke_v0_1.py",
        "status": status,
        "command": cmd,
        "returncode": proc.returncode,
        "marker_expected": marker,
        "marker_found": marker_found,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run read-only smoke for Administratum File Atlas TUI.")
    parser.add_argument("--lang", choices=["en", "ru"], default="en")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--allow-external-output", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    _enforce_output_path(output_path, allow_external=args.allow_external_output)
    report = run_smoke(lang=str(args.lang))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
