from __future__ import annotations

from typing import Any


def _collect_paths(value: Any, found: list[str], limit: int = 12) -> None:
    if len(found) >= limit:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text.endswith("path") or key_text.endswith("root"):
                if isinstance(item, str) and item not in found:
                    found.append(item)
            _collect_paths(item, found, limit)
    elif isinstance(value, list):
        for item in value:
            _collect_paths(item, found, limit)


def _status(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("status", "verdict", "result", "state"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
    return "UNKNOWN"


def _meaning(status: str) -> str:
    upper = status.upper()
    if "BLOCK" in upper:
        return "Action is blocked until the listed reason is handled."
    if "PASS_WITH" in upper or "WARNING" in upper:
        return "Usable with explicit warnings; do not claim clean completion."
    if upper.startswith("PASS") or upper in {"ACTIVE", "LIVE"}:
        return "Available for the scoped station workflow."
    if "DRY_RUN" in upper:
        return "Dry-run state is visible; live execution has not happened."
    return "State is visible but needs operator review."


def _next_action(status: str) -> str:
    upper = status.upper()
    if "BLOCK" in upper:
        return "Read blockers, keep unsafe actions disabled, and resolve the named gate."
    if "WARNING" in upper or "PASS_WITH" in upper:
        return "Use the full JSON view for evidence before staging or promoting."
    return "Proceed through the next validated station command."


def summarize_payload(title: str, payload: Any) -> dict[str, Any]:
    status = _status(payload)
    key_paths: list[str] = []
    _collect_paths(payload, key_paths)
    return {
        "status": status,
        "title": title,
        "human_meaning": _meaning(status),
        "key_paths": key_paths,
        "next_recommended_action": _next_action(status),
        "raw_json_available": True,
        "copy_open_actions_available": bool(key_paths),
    }


def render_summary_text(summary: dict[str, Any]) -> str:
    lines = [
        f"Title: {summary.get('title', '')}",
        f"Status: {summary.get('status', 'UNKNOWN')}",
        f"Meaning: {summary.get('human_meaning', '')}",
        f"Next: {summary.get('next_recommended_action', '')}",
    ]
    paths = summary.get("key_paths") or []
    if paths:
        lines.append("Key paths:")
        lines.extend(f"- {path}" for path in paths)
    return "\n".join(lines)
