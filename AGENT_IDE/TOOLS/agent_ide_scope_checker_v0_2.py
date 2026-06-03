from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set


TASK_ID = "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
ALLOWED_PREFIXES = [
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1/",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_git(repo_root: Path, args: List[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def _collect_changed_paths(repo_root: Path) -> List[str]:
    unstaged = _run_git(repo_root, ["diff", "--name-only"]).splitlines()
    staged = _run_git(repo_root, ["diff", "--name-only", "--cached"]).splitlines()
    status_lines = _run_git(repo_root, ["status", "--short"]).splitlines()
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    combined: Set[str] = {path.strip() for path in [*unstaged, *staged, *untracked] if path.strip()}
    return sorted(combined)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scope checker for Agent IDE dual-surface task.")
    parser.add_argument("--repo-root", default="E:/IMPERIUM")
    parser.add_argument(
        "--receipt-out",
        default=(
            "E:/IMPERIUM/IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
            "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1/"
            "receipts/scope_boundary_receipt.json"
        ),
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    changed_paths = _collect_changed_paths(repo_root)
    normalized = [path.replace("\\", "/") for path in changed_paths]
    out_of_scope = []
    for path in normalized:
        if not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            out_of_scope.append(path)

    status = "PASS" if not out_of_scope else "FAIL"
    receipt: Dict[str, Any] = {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "allowed_prefixes": ALLOWED_PREFIXES,
        "changed_paths": normalized,
        "out_of_scope_paths": out_of_scope,
    }

    receipt_path = Path(args.receipt_out).resolve()
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
