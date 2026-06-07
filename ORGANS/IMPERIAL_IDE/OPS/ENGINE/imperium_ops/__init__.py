"""imperium_ops - operational core that closes the owner loop inside Imperial IDE.

idea -> task -> taskpack -> Astronomicon registration -> launch card ->
servitor handoff (dry-run) -> validation -> receipts -> bundle gate ->
git closure -> owner report -> next step.

Status: CANDIDATE_NOT_CANON. Deterministic Python owns orchestration; LLM/
servitor only execute, and only behind explicit safety flags.
"""
from __future__ import annotations

__version__ = "0.1.0"
__status__ = "CANDIDATE_NOT_CANON"

__all__ = [
    "safety_gate",
    "task_console",
    "taskpack_builder",
    "receipts",
    "launch_card",
    "astronomicon_register",
    "git_closure",
    "lifecycle",
]
