from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def trim_text(value: Any, limit: int = 260) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...[truncated]"


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=data,
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def collect_sse(base_url: str, timeout_sec: float) -> dict[str, Any]:
    sse_url = f"{base_url}/api/events"
    command_url = f"{base_url}/api/terminal/execute"
    started = time.monotonic()
    command_response: dict[str, Any] = {}
    events: list[dict[str, Any]] = []
    flags = {"heartbeat": False, "state_snapshot": False, "command_event": False}
    command_triggered = False

    def trigger_command() -> None:
        nonlocal command_response
        try:
            command_response = post_json(
                command_url,
                {"organ": "MECHANICUS_AGENT", "command": "status"},
            )
        except Exception as exc:  # noqa: BLE001
            command_response = {"status": "ERROR", "error": str(exc)}

    with urllib.request.urlopen(sse_url, timeout=timeout_sec) as resp:
        current_event = "message"
        while time.monotonic() - started < timeout_sec:
            raw = resp.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            if line.startswith("event:"):
                current_event = line.split(":", 1)[1].strip()
                if not command_triggered and current_event in {"heartbeat", "state_snapshot"}:
                    command_triggered = True
                    threading.Thread(target=trigger_command, daemon=True).start()
                continue
            if line.startswith("data:"):
                payload_text = line.split(":", 1)[1].strip()
                try:
                    payload = json.loads(payload_text)
                except json.JSONDecodeError:
                    payload = {"raw": payload_text}

                events.append({"event_type": current_event, "payload": payload})
                if current_event == "heartbeat":
                    flags["heartbeat"] = True
                if current_event == "state_snapshot":
                    flags["state_snapshot"] = True
                if current_event in {"command_started", "command_finished", "command_failed", "terminal_entry_added"}:
                    if payload.get("command") == "status":
                        flags["command_event"] = True
                if all(flags.values()):
                    break

    compact_events = []
    for row in events[:20]:
        payload = row.get("payload", {})
        details = payload.get("details", {}) if isinstance(payload, dict) else {}
        compact_events.append(
            {
                "event_type": payload.get("event_type"),
                "timestamp_utc": payload.get("timestamp_utc"),
                "source": payload.get("source"),
                "truth_status": payload.get("truth_status"),
                "action_id": payload.get("action_id"),
                "command": payload.get("command"),
                "details": {
                    "status": details.get("status"),
                    "exit_code": details.get("exit_code"),
                    "duration_ms": details.get("duration_ms"),
                    "safety": details.get("safety"),
                    "stdout_summary": trim_text(details.get("stdout_summary")),
                    "stderr_summary": trim_text(details.get("stderr_summary")),
                    "heartbeat_interval_sec": details.get("heartbeat_interval_sec"),
                    "head": details.get("head"),
                    "worktree_state": details.get("worktree_state"),
                },
            }
        )

    return {
        "schema_version": "NEWGEN_SSE_EVENT_PROOF_V0_5",
        "checked_at_utc": utc_now(),
        "timeout_sec": timeout_sec,
        "sse_url": sse_url,
        "flags": flags,
        "command_response": {
            "status": command_response.get("status"),
            "action_id": command_response.get("action_id"),
            "command": command_response.get("command"),
            "source": command_response.get("source"),
            "safety": command_response.get("safety"),
            "exit_code": command_response.get("exit_code"),
            "duration_ms": command_response.get("duration_ms"),
            "stdout_summary": trim_text(command_response.get("stdout_summary")),
            "stderr_summary": trim_text(command_response.get("stderr_summary")),
        },
        "events_sample": compact_events,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="New Generation Sanctum SSE proof checker")
    parser.add_argument("--base-url", default="http://127.0.0.1:18765")
    parser.add_argument("--timeout-sec", type=float, default=35.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = collect_sse(args.base_url, args.timeout_sec)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
