#!/usr/bin/env python3
"""Dry-run classifier for Imperium core shape drift cleanup V0.2."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
REGISTRY = Path("ORGANS/_CORE_GOVERNANCE/REQUIRED_9_ORGANS_V0_1.json")
TASK_REGISTRY_PATHS = {
    "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
    "ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
}
CURRENT_TASK_PREFIX = "TASK-20260605-PC-CORE-SHAPE-DRIFT-CLEANUP-MIGRATION-QUEUE-QUARANTINE-GATE-V0_1"
POST_WORK_PREFIX = "TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-"

QUEUE_CLASSIFICATIONS = {
    "ORGAN_HOME",
    "COMMON_SUPPORT",
    "QUARANTINE_CANDIDATE",
    "LEGACY_ACCEPTED",
    "UNKNOWN_OWNER",
    "FUTURE_SCOPE",
}
RECOMMENDED_ACTIONS = {
    "KEEP",
    "MOVE_TO_ORGAN",
    "MOVE_TO_SUPPORT",
    "MOVE_TO_QUARANTINE",
    "INVESTIGATE",
    "FUTURE_SCOPE_HOLD",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def rel_to_root(path: Path, repo_root: Path) -> str:
    return to_posix(path.resolve().relative_to(repo_root.resolve()))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def load_required_organs(repo_root: Path) -> dict[str, dict[str, Any]]:
    registry = read_json(repo_root / REGISTRY)
    organs: dict[str, dict[str, Any]] = {}
    for entry in registry.get("required_organs", []):
        organ_id = entry.get("organ_id")
        if organ_id:
            organs[organ_id] = entry
    return organs


def git_status_map(repo_root: Path) -> dict[str, str]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError:
        return {}
    status: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line:
            continue
        code = line[:2]
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            status[path.replace("\\", "/")] = code
    return status


def base_entry(
    rel_path: str,
    kind: str,
    classification: str,
    owner_organ: str,
    recommended_action: str,
    active_use_allowed: bool,
    reason: str,
    risk: str,
    drift_type: str,
    confidence: str = "HIGH",
    evidence: list[str] | None = None,
    git_status: str = "",
) -> dict[str, Any]:
    if classification not in QUEUE_CLASSIFICATIONS:
        raise ValueError(f"invalid classification: {classification}")
    if recommended_action not in RECOMMENDED_ACTIONS:
        raise ValueError(f"invalid recommended_action: {recommended_action}")
    return {
        "schema_version": "imperium.core_file_ownership_entry.v0_2",
        "path": rel_path,
        "kind": kind,
        "classification": classification,
        "owner_organ": owner_organ,
        "recommended_action": recommended_action,
        "active_use_allowed": active_use_allowed,
        "reason": reason,
        "risk": risk,
        "drift_type": drift_type,
        "confidence": confidence,
        "evidence": evidence or [],
        "git_status": git_status,
        "dry_run_only": True,
        "move_or_delete_performed": False,
    }


def classify_path(rel_path: str, kind: str, required_organs: dict[str, dict[str, Any]], git_status: str = "") -> dict[str, Any]:
    rel_path = rel_path.replace("\\", "/").strip("/")
    parts = rel_path.split("/") if rel_path else []
    top = parts[0] if parts else ""

    if rel_path in TASK_REGISTRY_PATHS:
        return base_entry(
            rel_path,
            kind,
            "ORGAN_HOME",
            "ASTRONOMICON",
            "KEEP",
            True,
            "Astronomicon registry path; dirty status is classified as admission registry drift until closure commit.",
            "MEDIUM" if git_status else "LOW",
            "REGISTRY_DRIFT" if git_status else "ORGAN_REGISTRY",
            evidence=["tracked registry file", "git status" if git_status else "clean status"],
            git_status=git_status,
        )

    if top == "ORGANS" and len(parts) == 1:
        return base_entry(
            rel_path,
            kind,
            "COMMON_SUPPORT",
            "ADMINISTRATUM",
            "KEEP",
            True,
            "Container for required organs and core governance.",
            "LOW",
            "CORE_CONTAINER",
            evidence=["core shape contract"],
            git_status=git_status,
        )

    if top == "ORGANS" and len(parts) > 1:
        organ = parts[1]
        if organ in required_organs:
            if len(parts) >= 5 and parts[2:4] == ["TASK_INBOX", "REGISTERED"]:
                task_dir = parts[4]
                drift_type = "TASK_INBOX_ACTIVE_ADMISSION" if task_dir.startswith(CURRENT_TASK_PREFIX) else "TASK_INBOX_RESIDUE"
                classification = "COMMON_SUPPORT"
                action = "KEEP"
                active_use = task_dir.startswith(CURRENT_TASK_PREFIX)
                risk = "LOW" if active_use else "MEDIUM"
                reason = "Registered taskpack under Astronomicon task inbox."
                if task_dir.startswith(POST_WORK_PREFIX):
                    drift_type = "POST_WORK_RESIDUE"
                    active_use = False
                    reason = "Registered post-work admission residue; preserve as admission evidence and close in current bundle."
                return base_entry(
                    rel_path,
                    kind,
                    classification,
                    "ASTRONOMICON",
                    action,
                    active_use,
                    reason,
                    risk,
                    drift_type,
                    evidence=["registered taskpack path"],
                    git_status=git_status,
                )
            return base_entry(
                rel_path,
                kind,
                "ORGAN_HOME",
                organ,
                "KEEP",
                True,
                "Path is inside one of the exact required nine organ homes.",
                "LOW",
                "ACTIVE_ORGAN",
                evidence=["required 9-organ registry"],
                git_status=git_status,
            )
        if organ == "_CORE_GOVERNANCE":
            return base_entry(
                rel_path,
                kind,
                "COMMON_SUPPORT",
                "ADMINISTRATUM",
                "KEEP",
                True,
                "Core governance support zone for contracts, schemas, validators, and matrices.",
                "LOW",
                "CORE_GOVERNANCE_SUPPORT",
                evidence=["core shape contract"],
                git_status=git_status,
            )
        if organ == "_POST_WORK_RING":
            return base_entry(
                rel_path,
                kind,
                "LEGACY_ACCEPTED",
                "ADMINISTRATUM",
                "FUTURE_SCOPE_HOLD",
                False,
                "Legacy post-work ring area retained until post-work authority migration is separately scoped.",
                "MEDIUM",
                "POST_WORK_RESIDUE",
                confidence="MEDIUM",
                evidence=["accepted legacy support"],
                git_status=git_status,
            )
        if organ == "SPECULUM":
            return base_entry(
                rel_path,
                kind,
                "FUTURE_SCOPE",
                "CUSTODES",
                "FUTURE_SCOPE_HOLD",
                False,
                "Speculum is present but not part of the exact nine-organ core for this cleanup.",
                "MEDIUM",
                "FUTURE_SCOPE",
                confidence="MEDIUM",
                evidence=["core scope excludes non-required organ homes"],
                git_status=git_status,
            )
        return base_entry(
            rel_path,
            kind,
            "UNKNOWN_OWNER",
            "ADMINISTRATUM",
            "INVESTIGATE",
            False,
            "ORGANS child is not one of the exact required nine organs or accepted support zones.",
            "HIGH",
            "UNKNOWN_OWNER",
            confidence="UNKNOWN_WITH_REASON",
            evidence=["required 9-organ registry"],
            git_status=git_status,
        )

    if top == "SUPPORT":
        if len(parts) == 1:
            return base_entry(rel_path, kind, "COMMON_SUPPORT", "ADMINISTRATUM", "KEEP", True, "Support container.", "LOW", "SUPPORT_CONTAINER", evidence=["support contract"], git_status=git_status)
        if parts[1] == "COMMON_IMPERIUM_SUPPORT":
            return base_entry(rel_path, kind, "COMMON_SUPPORT", "ADMINISTRATUM", "KEEP", True, "Accepted common support zone.", "LOW", "COMMON_SUPPORT", evidence=["support contract"], git_status=git_status)
        if parts[1] == "QUESTIONABLE_OR_QUARANTINE":
            return base_entry(rel_path, kind, "QUARANTINE_CANDIDATE", "INQUISITION", "KEEP", False, "Quarantine support zone; active use is blocked unless admitted by explicit receipt.", "HIGH", "QUARANTINE_ZONE", evidence=["quarantine ban contract"], git_status=git_status)
        return base_entry(rel_path, kind, "UNKNOWN_OWNER", "ADMINISTRATUM", "INVESTIGATE", False, "Support child is not in the accepted support map.", "MEDIUM", "UNKNOWN_OWNER", confidence="UNKNOWN_WITH_REASON", evidence=["support contract"], git_status=git_status)

    if top == "REPORTS":
        return base_entry(rel_path, kind, "COMMON_SUPPORT", "ADMINISTRATUM", "KEEP", False, "Closure evidence history; not an organ authority source.", "LOW", "REPORT_EVIDENCE", confidence="MEDIUM", evidence=["post-work bundle contract"], git_status=git_status)

    if top == "MATRIX_SPINE":
        return base_entry(rel_path, kind, "LEGACY_ACCEPTED", "DOCTRINARIUM", "FUTURE_SCOPE_HOLD", False, "Legacy matrix spine retained as candidate-not-canon reference until mapped into organ homes.", "MEDIUM", "ACCEPTED_LEGACY", confidence="MEDIUM", evidence=["matrix spine status"], git_status=git_status)

    if top == "AGENTS.md":
        return base_entry(rel_path, kind, "LEGACY_ACCEPTED", "ADMINISTRATUM", "KEEP", True, "Root contract remains active entry routing authority.", "LOW", "ACCEPTED_LEGACY", confidence="HIGH", evidence=["root AGENTS contract"], git_status=git_status)

    if top in {"ANCIENT_EMPIRE_REFERENCE.md", "IMPERIUM_NEW_GENERATION", "QUARANTINE"}:
        return base_entry(rel_path, kind, "QUARANTINE_CANDIDATE", "INQUISITION", "MOVE_TO_QUARANTINE", False, "Name is legacy/questionable and requires salvage admission before active use.", "HIGH", "QUARANTINE_CANDIDATE", confidence="MEDIUM", evidence=["quarantine policy"], git_status=git_status)

    return base_entry(
        rel_path,
        kind,
        "UNKNOWN_OWNER",
        "ADMINISTRATUM",
        "INVESTIGATE",
        False,
        "No V0.2 ownership rule matched this path.",
        "HIGH",
        "UNKNOWN_OWNER",
        confidence="UNKNOWN_WITH_REASON",
        evidence=["classifier fallback"],
        git_status=git_status,
    )


def candidate_paths(repo_root: Path) -> list[Path]:
    paths: set[Path] = set()
    for rel in [
        "AGENTS.md",
        "MATRIX_SPINE",
        "ORGANS",
        "SUPPORT",
        "REPORTS",
        "ANCIENT_EMPIRE_REFERENCE.md",
        "IMPERIUM_NEW_GENERATION",
        "QUARANTINE",
    ]:
        path = repo_root / rel
        if path.exists():
            paths.add(path)

    organs_root = repo_root / "ORGANS"
    if organs_root.is_dir():
        for child in organs_root.iterdir():
            if child.name.startswith("."):
                continue
            paths.add(child)
        for rel in TASK_REGISTRY_PATHS:
            path = repo_root / rel
            if path.exists():
                paths.add(path)
        registered = organs_root / "ASTRONOMICON" / "TASK_INBOX" / "REGISTERED"
        if registered.is_dir():
            for task_dir in registered.iterdir():
                if task_dir.is_dir():
                    paths.add(task_dir)

    support_root = repo_root / "SUPPORT"
    if support_root.is_dir():
        for child in support_root.iterdir():
            if child.name.startswith("."):
                continue
            paths.add(child)

    return sorted(paths, key=lambda p: to_posix(p.relative_to(repo_root)).upper())


def build_report(repo_root: Path, task_id: str, max_entries: int = 1000) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    required_organs = load_required_organs(repo_root)
    status = git_status_map(repo_root)
    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    drift_counts: dict[str, int] = {}

    for path in candidate_paths(repo_root):
        rel = rel_to_root(path, repo_root)
        kind = "directory" if path.is_dir() else "file"
        git_code = status.get(rel, "")
        entry = classify_path(rel, kind, required_organs, git_code)
        counts[entry["classification"]] = counts.get(entry["classification"], 0) + 1
        drift_counts[entry["drift_type"]] = drift_counts.get(entry["drift_type"], 0) + 1
        if len(entries) < max_entries:
            entries.append(entry)

    warnings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    if counts.get("UNKNOWN_OWNER", 0):
        warnings.append({"id": "UNKNOWN_OWNER_PRESENT", "count": counts["UNKNOWN_OWNER"]})
    if drift_counts.get("REGISTRY_DRIFT", 0):
        warnings.append({"id": "REGISTRY_DRIFT_CLASSIFIED", "count": drift_counts["REGISTRY_DRIFT"], "meaning": "Allowed only until closure commit captures admission changes."})
    if drift_counts.get("TASK_INBOX_RESIDUE", 0):
        warnings.append({"id": "TASK_INBOX_RESIDUE_CLASSIFIED", "count": drift_counts["TASK_INBOX_RESIDUE"]})
    if drift_counts.get("POST_WORK_RESIDUE", 0):
        warnings.append({"id": "POST_WORK_RESIDUE_CLASSIFIED", "count": drift_counts["POST_WORK_RESIDUE"]})
    if drift_counts.get("FUTURE_SCOPE", 0):
        warnings.append({"id": "FUTURE_SCOPE_PRESENT", "count": drift_counts["FUTURE_SCOPE"]})

    return {
        "schema_version": "imperium.core_file_classifier_dry_run_report.v0_2",
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "verdict": "BLOCK" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "mode": "DRY_RUN_ONLY",
        "move_or_delete_performed": False,
        "import_rewrite_performed": False,
        "required_organ_count": len(required_organs),
        "scanned_entry_count": len(candidate_paths(repo_root)),
        "reported_entry_limit": max_entries,
        "classification_counts": counts,
        "drift_type_counts": drift_counts,
        "queue_classifications": sorted(QUEUE_CLASSIFICATIONS),
        "recommended_actions": sorted(RECOMMENDED_ACTIONS),
        "entries": entries,
        "warnings": warnings,
        "blockers": blockers,
        "next_action": "Feed entries into core_migration_queue_builder_v0_1.py; no physical migration is authorized by this classifier.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify Imperium core files without moving them.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--max-entries", type=int, default=1000)
    parser.add_argument("--output", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.repo_root), args.task_id, args.max_entries)
    if args.output:
        write_json(Path(args.output), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["verdict"] in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
