"""In-process SSE event bus for Sanctum Mini."""

from __future__ import annotations

import json
import queue
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any


MAX_RECENT_EVENTS = 200
MAX_SUBSCRIBER_QUEUE = 200

_EVENT_LOCK = threading.Lock()
_SUBSCRIBERS: dict[int, queue.Queue[dict[str, Any]]] = {}
_RECENT_EVENTS: deque[dict[str, Any]] = deque(maxlen=MAX_RECENT_EVENTS)
_EVENT_SEQ = 0
_SUBSCRIBER_SEQ = 0


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _next_event_id() -> int:
    global _EVENT_SEQ
    _EVENT_SEQ += 1
    return _EVENT_SEQ


def _next_subscriber_id() -> int:
    global _SUBSCRIBER_SEQ
    _SUBSCRIBER_SEQ += 1
    return _SUBSCRIBER_SEQ


def _trim_queue(buffer: queue.Queue[dict[str, Any]]) -> None:
    while buffer.qsize() >= MAX_SUBSCRIBER_QUEUE:
        try:
            buffer.get_nowait()
        except queue.Empty:
            return


def make_event(
    *,
    event_type: str,
    source: str,
    truth_status: str,
    action_id: str | None = None,
    command: str | None = None,
    organ: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "event_id": _next_event_id(),
        "event_type": event_type,
        "timestamp_utc": _utc_now(),
        "source": source,
        "truth_status": truth_status,
        "action_id": action_id,
        "command": command,
        "organ": organ,
        "details": details or {},
    }
    return event


def publish_event(
    *,
    event_type: str,
    source: str,
    truth_status: str,
    action_id: str | None = None,
    command: str | None = None,
    organ: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = make_event(
        event_type=event_type,
        source=source,
        truth_status=truth_status,
        action_id=action_id,
        command=command,
        organ=organ,
        details=details,
    )
    with _EVENT_LOCK:
        _RECENT_EVENTS.append(event)
        for buffer in list(_SUBSCRIBERS.values()):
            _trim_queue(buffer)
            try:
                buffer.put_nowait(event)
            except queue.Full:
                try:
                    buffer.get_nowait()
                    buffer.put_nowait(event)
                except (queue.Empty, queue.Full):
                    pass
    return event


def recent_events(limit: int = 40) -> list[dict[str, Any]]:
    with _EVENT_LOCK:
        items = list(_RECENT_EVENTS)
    if limit <= 0:
        return []
    return items[-limit:]


def subscribe_events() -> tuple[int, queue.Queue[dict[str, Any]]]:
    subscriber_id = _next_subscriber_id()
    buffer: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=MAX_SUBSCRIBER_QUEUE)
    with _EVENT_LOCK:
        _SUBSCRIBERS[subscriber_id] = buffer
    return subscriber_id, buffer


def unsubscribe_events(subscriber_id: int) -> None:
    with _EVENT_LOCK:
        _SUBSCRIBERS.pop(subscriber_id, None)


def encode_sse(event: dict[str, Any]) -> bytes:
    payload = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    lines = [
        f"id: {event.get('event_id', '')}",
        f"event: {event.get('event_type', 'message')}",
        f"data: {payload}",
        "",
        "",
    ]
    return "\n".join(lines).encode("utf-8")
