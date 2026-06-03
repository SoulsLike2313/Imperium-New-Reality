from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_excerpt(value: str, limit: int = 1200) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def make_receipt_id(task_id: str, tool: str, suffix: str) -> str:
    safe_task = task_id.lower().replace(" ", "-")
    safe_tool = tool.lower().replace(" ", "-")
    safe_suffix = suffix.lower().replace(" ", "-")
    return f"{safe_task}:{safe_tool}:{safe_suffix}"


def build_install_receipt(
    *,
    task_id: str,
    tool: str,
    package: str,
    install_command: str,
    started_at_utc: str,
    finished_at_utc: str,
    exit_code: int | None,
    stdout_text: str,
    stderr_text: str,
    network_used: bool,
    install_scope: str,
    install_performed: bool,
    side_effects: list[str],
    post_install_validation_command: str,
    post_install_validation_result: str,
    verdict: str,
) -> dict[str, Any]:
    return {
        "receipt_id": make_receipt_id(task_id, tool, "install"),
        "task_id": task_id,
        "tool": tool,
        "package": package,
        "install_command": install_command,
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "exit_code": exit_code,
        "stdout_excerpt": short_excerpt(stdout_text),
        "stderr_excerpt": short_excerpt(stderr_text),
        "network_used": bool(network_used),
        "install_scope": install_scope,
        "install_performed": bool(install_performed),
        "side_effects": side_effects,
        "post_install_validation_command": post_install_validation_command,
        "post_install_validation_result": post_install_validation_result,
        "verdict": verdict,
    }


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Mechanicus controlled provision install receipt.",
    )
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--install-command", required=True)
    parser.add_argument("--started-at-utc", default=utc_now())
    parser.add_argument("--finished-at-utc", default=utc_now())
    parser.add_argument("--exit-code", type=int, default=0)
    parser.add_argument("--stdout", default="")
    parser.add_argument("--stderr", default="")
    parser.add_argument("--network-used", action="store_true")
    parser.add_argument("--install-scope", default="user")
    parser.add_argument("--install-performed", action="store_true")
    parser.add_argument("--side-effects-json", default="[]")
    parser.add_argument("--post-install-validation-command", default="")
    parser.add_argument("--post-install-validation-result", default="")
    parser.add_argument("--verdict", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = build_install_receipt(
        task_id=args.task_id,
        tool=args.tool,
        package=args.package,
        install_command=args.install_command,
        started_at_utc=args.started_at_utc,
        finished_at_utc=args.finished_at_utc,
        exit_code=args.exit_code,
        stdout_text=args.stdout,
        stderr_text=args.stderr,
        network_used=bool(args.network_used),
        install_scope=args.install_scope,
        install_performed=bool(args.install_performed),
        side_effects=json.loads(args.side_effects_json),
        post_install_validation_command=args.post_install_validation_command,
        post_install_validation_result=args.post_install_validation_result,
        verdict=args.verdict,
    )
    write_receipt(Path(args.output), payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
