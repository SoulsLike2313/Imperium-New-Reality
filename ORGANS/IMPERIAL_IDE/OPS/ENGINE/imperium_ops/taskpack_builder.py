"""Build Astronomicon-compatible taskpacks from a TaskIntent.

The builder writes the six root files Astronomicon expects, validates UTF-8
text without BOM, rejects Cyrillic in taskpack root policy files, and produces a
ZIP plus SHA256 for dry-run registration. It never registers live tasks by
itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from typing import Dict, List

from .task_console import TaskIntent

SCHEMA_VERSION = "astronomicon.taskpack.v0_1"

REQUIRED_TASKPACK_FILES = [
    "MANIFEST.json",
    "TASK_SPEC.md",
    "ACCEPTANCE_GATES.md",
    "OUTPUT_REQUIREMENTS.md",
    "TASK_ROUTE_MANIFEST_TEMPLATE.json",
    "TASK_START_ACK_TEMPLATE.json",
]

REQUIRED_ORGANS = [
    "DOCTRINARIUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]

ORGAN_ROUTE = {
    "DOCTRINARIUM": "Doctrine and schema boundary review",
    "OFFICIO_AGENTIS": "Owner-facing summary and launch wording",
    "ASTRONOMICON": "Taskpack admission and registry routing",
    "ADMINISTRATUM": "Receipts, bundle gates, continuity, and closure",
    "MECHANICUS": "Command policy, tool gate, and dry-run validation",
    "INQUISITION": "Fake-green, secret, runtime, and safety checks",
    "STRATEGIUM": "Template selection and next-task ladder",
    "SCHOLA_IMPERIALIS": "Reusable lessons and operator guide",
}

_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_VALIDATED_PUSH_TEXT = (
    "validated push is allowed and expected after validation, scope check, "
    "secret check, and task policy"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _required_organs(intent: TaskIntent) -> list[str]:
    organs = list(REQUIRED_ORGANS)
    for organ in intent.organs_route:
        if organ in ORGAN_ROUTE and organ not in organs:
            organs.append(organ)
    return organs


def _organ_route(intent: TaskIntent) -> dict[str, str]:
    route = dict(ORGAN_ROUTE)
    for organ in intent.organs_route:
        route.setdefault(organ, "Task-specific operational review")
    return route


def _git_push_policy() -> dict:
    return {
        "push_allowed": True,
        "push_required_for_success": True,
        "policy_text": _VALIDATED_PUSH_TEXT,
        "allowed_when": [
            "all required outputs exist",
            "JSON files parse successfully",
            "created or modified Python files compile",
            "scope check passes",
            "secret check passes",
            "runtime paths are not staged",
            "real servitor execution remains blocked",
            "live LLM backend remains disabled",
            "unsafe shell remains blocked",
        ],
        "forbidden_when": [
            "secrets or local configs are staged",
            "runtime paths are staged",
            "out-of-scope changes are staged",
            "unsafe execution is required",
            "validation fails",
        ],
    }


def build_manifest(intent: TaskIntent) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "taskpack_id": intent.task_id,
        "task_id": intent.task_id,
        "title": intent.title,
        "created_from_contour": "PC",
        "target_contour": "PC",
        "registration_mode": "ASTRONOMICON_STAGE2_LOCAL_PC_TASKPACK",
        "execution_mode": "CONTROLLED_WRITE_WITH_VALIDATED_PUSH",
        "status": "CANDIDATE_NOT_CANON",
        "mission_summary": intent.goal,
        "task_type": intent.task_type,
        "scope": intent.scope,
        "risk": intent.risk,
        "required_organs": _required_organs(intent),
        "organ_route": _organ_route(intent),
        "organs_route": intent.organs_route,
        "route_manifest_template": "TASK_ROUTE_MANIFEST_TEMPLATE.json",
        "task_start_ack_template": "TASK_START_ACK_TEMPLATE.json",
        "language_and_encoding_policy": {
            "taskpack_internal_files": "ENGLISH_UTF8_NO_BOM_NO_CYRILLIC",
            "canonical_repo_artifacts": "ENGLISH_UTF8_NO_BOM",
            "cyrillic_in_taskpack": {
                "allowed": False,
                "scope": ", ".join(REQUIRED_TASKPACK_FILES),
            },
        },
        "git_push_policy": _git_push_policy(),
        "push_policy": intent.push_policy,
        "allowed_write_scope": intent.allowed_write_scope,
        "forbidden_actions": intent.forbidden_actions,
        "source_bundles": {},
        "remote_contours": {"VM2": "OUT_OF_SCOPE", "VM3": "OUT_OF_SCOPE"},
    }


def render_task_spec(intent: TaskIntent) -> str:
    return (
        "# TASK_SPEC\n\n"
        f"## Task ID\n{intent.task_id}\n\n"
        f"## Title\n{intent.title}\n\n"
        f"## Goal\n{intent.goal}\n\n"
        "## Mode\nCONTROLLED_WRITE_WITH_VALIDATED_PUSH\n\n"
        f"## Type / Scope / Risk\n{intent.task_type} / {intent.scope} / {intent.risk}\n\n"
        f"## Organs Route\n{', '.join(intent.organs_route)}\n\n"
        f"## Allowed Write Scope\n{', '.join(intent.allowed_write_scope)}\n\n"
        "## Safety\nReal servitor execution, unrestricted shell, and live LLM backend stay disabled.\n"
    )


def render_acceptance_gates(intent: TaskIntent) -> str:
    return (
        "# ACCEPTANCE_GATES\n\n"
        "## Gate 1: Root Files\nAll six required Astronomicon root files exist.\n\n"
        "## Gate 2: Encoding\nRoot files are UTF-8 without BOM and contain no Cyrillic text.\n\n"
        "## Gate 3: JSON\nAll JSON root files parse.\n\n"
        "## Gate 4: Safety\nReal execution, live LLM, and unrestricted shell remain disabled.\n\n"
        "## Gate 5: Receipts\nNo PASS claim is accepted without receipts and evidence.\n\n"
        "## Gate 6: Push Policy\n"
        f"{_VALIDATED_PUSH_TEXT}.\n\n"
        "## Gate 7: Scope\n"
        f"Diff must remain within: {', '.join(intent.allowed_write_scope)}\n"
    )


def render_output_requirements(intent: TaskIntent) -> str:
    return (
        "# OUTPUT_REQUIREMENTS\n\n"
        "Required final evidence: task_id, result_summary, artifacts, receipts, "
        "validation summary, evidence_level >= E3, metrics, and next task recommendation.\n\n"
        f"Git policy: {_VALIDATED_PUSH_TEXT}.\n\n"
        "No fake-green closure. No runtime paths, local configs, or secrets may be staged.\n"
    )


def render_route_manifest_template(intent: TaskIntent) -> dict:
    return {
        "schema_version": "astronomicon.task_route_manifest_template.v0_1",
        "template_id": "TASK_ROUTE_MANIFEST_TEMPLATE_V0_1",
        "task_id": intent.task_id,
        "taskpack_id": intent.task_id,
        "required_organs": _required_organs(intent),
        "organ_route": _organ_route(intent),
        "route": [
            {"step": i + 1, "organ": organ, "action": "process", "mode": "dry_run"}
            for i, organ in enumerate(intent.organs_route)
        ],
        "entry_ack_required": True,
        "resolver_receipt_required": True,
        "target_contour": "PC",
    }


def render_start_ack_template(intent: TaskIntent) -> dict:
    return {
        "schema_version": "astronomicon.task_start_ack_template.v0_1",
        "task_id": intent.task_id,
        "taskpack_id": intent.task_id,
        "acknowledged_by": "FILL_EXECUTOR_ID",
        "acknowledged_at": "FILL_ISO8601",
        "contour": "PC",
        "scope_confirmed": intent.allowed_write_scope,
        "forbidden_confirmed": intent.forbidden_actions,
        "start_message": "SERVITOR START: scope and forbidden actions acknowledged; dry-run only.",
    }


def no_bom_check(text: str) -> bool:
    return not text.startswith("\ufeff")


def no_cyrillic_check(text: str) -> bool:
    return _CYRILLIC_RE.search(text) is None


def language_gate_check(text: str) -> bool:
    return bool(text and text.strip())


def json_parse_check(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except (ValueError, json.JSONDecodeError):
        return False


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_taskpack(out_root: str, intent: TaskIntent) -> str:
    """Write the EXTRACTED taskpack tree and return its directory."""
    extracted = os.path.join(out_root, intent.task_id, "EXTRACTED")
    os.makedirs(extracted, exist_ok=True)
    _write(
        os.path.join(extracted, "MANIFEST.json"),
        json.dumps(build_manifest(intent), ensure_ascii=False, indent=2) + "\n",
    )
    _write(os.path.join(extracted, "TASK_SPEC.md"), render_task_spec(intent))
    _write(os.path.join(extracted, "ACCEPTANCE_GATES.md"), render_acceptance_gates(intent))
    _write(os.path.join(extracted, "OUTPUT_REQUIREMENTS.md"), render_output_requirements(intent))
    _write(
        os.path.join(extracted, "TASK_ROUTE_MANIFEST_TEMPLATE.json"),
        json.dumps(render_route_manifest_template(intent), ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        os.path.join(extracted, "TASK_START_ACK_TEMPLATE.json"),
        json.dumps(render_start_ack_template(intent), ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        os.path.join(extracted, "README.md"),
        f"# {intent.task_id}\n\n{intent.title}\n\nStatus: CANDIDATE_NOT_CANON\n",
    )
    return extracted


def build_zip(extracted: str, zip_path: str) -> Dict:
    """Zip the extracted tree, excluding pycache/pyc, and return file/byte/sha."""
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    files = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dirs, fs in os.walk(extracted):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in sorted(fs):
                if f.endswith(".pyc"):
                    continue
                full = os.path.join(dp, f)
                arc = os.path.relpath(full, extracted)
                z.write(full, arc)
                files += 1
    data = open(zip_path, "rb").read()
    return {"files": files, "bytes": len(data), "sha256": sha256_bytes(data)}


def admission_precheck(extracted: str) -> List[str]:
    """Return blockers that would stop Astronomicon admission. Empty == clean."""
    blockers: List[str] = []
    manifest = None
    for name in REQUIRED_TASKPACK_FILES:
        path = os.path.join(extracted, name)
        if not os.path.isfile(path):
            blockers.append(f"missing required file: {name}")
            continue
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        if not no_bom_check(text):
            blockers.append(f"BOM detected in {name}")
        if not language_gate_check(text):
            blockers.append(f"empty/placeholder content in {name}")
        if not no_cyrillic_check(text):
            blockers.append(f"Cyrillic detected in taskpack root file: {name}")
        if name.endswith(".json"):
            try:
                data = json.loads(text)
            except (ValueError, json.JSONDecodeError):
                blockers.append(f"invalid JSON in {name}")
                continue
            if name == "MANIFEST.json":
                manifest = data
    if isinstance(manifest, dict):
        required_fields = [
            "schema_version",
            "task_id",
            "taskpack_id",
            "required_organs",
            "organ_route",
            "route_manifest_template",
            "task_start_ack_template",
            "language_and_encoding_policy",
            "git_push_policy",
            "allowed_write_scope",
            "forbidden_actions",
        ]
        for field in required_fields:
            if field not in manifest:
                blockers.append(f"manifest missing field: {field}")
        if manifest.get("schema_version") != SCHEMA_VERSION:
            blockers.append(f"manifest schema_version is not {SCHEMA_VERSION}")
        policy = manifest.get("git_push_policy") or {}
        if _VALIDATED_PUSH_TEXT not in json.dumps(policy):
            blockers.append("validated push policy wording missing")
        lang = manifest.get("language_and_encoding_policy") or {}
        if "cyrillic_in_taskpack" not in lang:
            blockers.append("language policy missing cyrillic_in_taskpack")
    return blockers
