from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root, resolve_output_path  # noqa: E402


TASK_ID = "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC"
ALLOWED_PREFIX = "AGENT_IDE/"


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
    parser = argparse.ArgumentParser(description="Scope checker for Agent IDE task")
    parser.add_argument("--repo-root", default="", help="Optional New Reality repo root override.")
    parser.add_argument(
        "--receipt-out",
        default=(
            "AGENT_IDE/REPORTS/"
            "TASK-NEWGEN-READONLY-AGENT-IDE-V0_1-PC/receipts/scope_boundary_receipt.json"
        ),
    )
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    changed_paths = _collect_changed_paths(repo_root)
    out_of_scope = [path for path in changed_paths if not path.replace("\\", "/").startswith(ALLOWED_PREFIX)]
    status = "PASS" if not out_of_scope else "FAIL"

    receipt: Dict[str, Any] = {
        "task_id": TASK_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "allowed_prefix": ALLOWED_PREFIX,
        "changed_paths": changed_paths,
        "out_of_scope_paths": out_of_scope,
    }

    receipt_path = resolve_output_path(args.receipt_out, repo_root)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
