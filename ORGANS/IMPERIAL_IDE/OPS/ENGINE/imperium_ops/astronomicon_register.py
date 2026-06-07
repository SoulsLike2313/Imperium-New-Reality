"""astronomicon_register - register a taskpack into the Astronomicon inbox.

Mirrors the live repo layout:
    ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/<task_id>/EXTRACTED/...
In dry-run mode it writes into a STAGING mirror so the kernel tree is never
touched. Emits admission + resolver receipts.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from typing import List, Optional

from . import receipts
from . import taskpack_builder as tpb
from .task_console import TaskIntent

REGISTERED_REL = os.path.join("ORGANS", "ASTRONOMICON", "TASK_INBOX", "REGISTERED")
OPS_STAGING_REL = os.path.join("ORGANS", "IMPERIAL_IDE", "OPS", "STAGING")


def registered_root(repo_root: str, dry_run: bool) -> str:
    """Real inbox, or a STAGING mirror when dry_run."""
    if dry_run:
        return os.path.normpath(os.path.join(repo_root, OPS_STAGING_REL, REGISTERED_REL))
    return os.path.normpath(os.path.join(repo_root, REGISTERED_REL))


@dataclass
class RegistrationResult:
    task_id: str
    admitted: bool
    registered_path: str
    blockers: List[str] = field(default_factory=list)
    sha256: str = ""
    admission_receipt: dict = field(default_factory=dict)
    resolver_receipt: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "admitted": self.admitted,
            "registered_path": self.registered_path,
            "blockers": self.blockers,
            "sha256": self.sha256,
            "admission_receipt": self.admission_receipt,
            "resolver_receipt": self.resolver_receipt,
        }


def register(
    repo_root: str,
    extracted: str,
    intent: TaskIntent,
    dry_run: bool = True,
    live_registration_enabled: bool = False,
) -> RegistrationResult:
    """Run admission precheck, copy the taskpack into the inbox, emit receipts."""
    blockers = tpb.admission_precheck(extracted)
    root = registered_root(repo_root, dry_run)
    dest = os.path.join(root, intent.task_id, "EXTRACTED")
    searched = [root, dest]

    if not dry_run and not live_registration_enabled:
        blockers.append(
            "live registration gated: target is ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED "
            "and requires controlled mode plus receipt"
        )

    sha = ""
    if not blockers:
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copytree(extracted, dest)
        zip_path = os.path.join(os.path.dirname(dest), "TASKPACK.zip")
        sha = tpb.build_zip(dest, zip_path)["sha256"]

    admission_receipt = receipts.make_receipt(
        "taskpack_admission_receipt",
        task_id=intent.task_id,
        admitted=not blockers,
        blockers=blockers,
        sha256=sha,
        dry_run=dry_run,
        live_registration_enabled=live_registration_enabled,
        live_target=registered_root(repo_root, False),
    )
    resolver_receipt = receipts.make_receipt(
        "resolver_receipt",
        task_id=intent.task_id,
        resolved_path=dest if not blockers else "",
        searched_paths=searched,
        dry_run=dry_run,
    )
    return RegistrationResult(
        task_id=intent.task_id,
        admitted=not blockers,
        registered_path=dest if not blockers else "",
        blockers=blockers,
        sha256=sha,
        admission_receipt=admission_receipt,
        resolver_receipt=resolver_receipt,
    )


def list_registered(repo_root: str) -> List[str]:
    """List task ids registered in real and staging inboxes."""
    found: List[str] = []
    for dry in (False, True):
        root = registered_root(repo_root, dry)
        if os.path.isdir(root):
            for name in sorted(os.listdir(root)):
                if os.path.isdir(os.path.join(root, name)) and name not in found:
                    found.append(name)
    return found


def find_task(repo_root: str, task_id: str) -> Optional[str]:
    for dry in (False, True):
        path = os.path.join(registered_root(repo_root, dry), task_id, "EXTRACTED")
        if os.path.isdir(path):
            return path
    return None
