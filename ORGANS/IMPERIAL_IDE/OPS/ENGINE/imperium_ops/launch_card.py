"""launch_card - the card the IDE shows after a taskpack is registered.

It summarises the admitted task and produces the start message a servitor
would acknowledge before any (dry-run) work begins.
"""
from __future__ import annotations

from typing import Dict

from .task_console import TaskIntent


def _start_message(intent: TaskIntent) -> str:
    return (
        f"SERVITOR START: task={intent.task_id} type={intent.task_type} "
        f"scope={intent.scope} risk={intent.risk} push={intent.push_policy}. "
        "Dry-run only; real execution blocked."
    )


def build_launch_card(intent: TaskIntent, registered_path: str, admission_ok: bool, sha256: str) -> Dict:
    return {
        "task_id": intent.task_id,
        "title": intent.title,
        "task_type": intent.task_type,
        "scope": intent.scope,
        "risk": intent.risk,
        "organs_route": intent.organs_route,
        "push_policy": intent.push_policy,
        "registered_path": registered_path,
        "sha256": sha256,
        "admission": "ADMITTED" if admission_ok else "BLOCKED",
        "start_message": _start_message(intent),
        "status": "CANDIDATE_NOT_CANON",
    }


def render_launch_card_text(card: Dict) -> str:
    lines = [
        "+----------------------- LAUNCH CARD -----------------------+",
        f" task_id : {card.get('task_id')}",
        f" title   : {card.get('title')}",
        f" type    : {card.get('task_type')}   scope: {card.get('scope')}   risk: {card.get('risk')}",
        f" route   : {', '.join(card.get('organs_route', []))}",
        f" push    : {card.get('push_policy')}",
        f" sha256  : {card.get('sha256')}",
        f" admission: {card.get('admission')}",
        f" path    : {card.get('registered_path')}",
        "+-----------------------------------------------------------+",
        f" {card.get('start_message')}",
    ]
    return "\n".join(lines)
