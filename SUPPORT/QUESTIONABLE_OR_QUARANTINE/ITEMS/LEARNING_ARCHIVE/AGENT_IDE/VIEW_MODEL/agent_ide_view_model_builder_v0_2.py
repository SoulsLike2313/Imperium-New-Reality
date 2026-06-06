from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sys


TASK_ID = "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
VIEW_MODEL_SCHEMA_VERSION = "imperium.agent_ide.view_model.v0_2"
DASHBOARD_SCHEMA_VERSION = "imperium.agent_ide.dashboard_view_model.v0_1"
BLOCK_VIEW_SCHEMA_VERSION = "imperium.agent_ide.block_view_model.v0_1"

APP_DIR = Path(__file__).resolve().parents[1] / "APP"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from agent_ide_data_loader_v0_1 import (  # noqa: E402
    build_view_model_dict as build_view_model_v0_1_dict,
    discover_repo_root,
)


VIEW_MODEL_DIR = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL")
BLOCK_FOUNDATION_DIR = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/BLOCK_FOUNDATION")
SELF_VALIDATOR_SUMMARY_PATH = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1/"
    "self_validation_summary.json"
)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_surface(path: str, file_kind: str, status: str) -> str:
    upper = path.upper()
    if "/PRIVATE/" in upper or "\\PRIVATE\\" in upper:
        return "PRIVATE_CONTEXT"
    if "/LOCAL/" in upper or "\\LOCAL\\" in upper:
        return "LOCAL_CONTEXT"
    if "/RUNTIME/" in upper or "\\RUNTIME\\" in upper:
        return "RUNTIME"
    if "/REPORTS/" in upper or "\\REPORTS\\" in upper:
        return "ARTIFACT"
    if upper.startswith("IMPERIUM_NEW_GENERATION/"):
        if status.upper() in {"DRAFT", "LEGACY", "WARN"} or file_kind.upper() == "UNKNOWN":
            return "CANDIDATE_TO_CANON"
        return "NEWGEN_CANON"
    if upper.startswith("IMPERIUM_TEST_VERSION/"):
        return "REPO_NON_NEWGEN"
    if file_kind.upper() == "UNKNOWN":
        return "UNKNOWN"
    return "REPO_NON_NEWGEN"


def _build_classification_surface(file_passports: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {
        "NEWGEN_CANON": 0,
        "REPO_NON_NEWGEN": 0,
        "LOCAL_CONTEXT": 0,
        "PRIVATE_CONTEXT": 0,
        "RUNTIME": 0,
        "ARTIFACT": 0,
        "UNKNOWN": 0,
        "CANDIDATE_TO_CANON": 0,
    }
    samples: Dict[str, List[str]] = {key: [] for key in counts}
    projected: List[Dict[str, Any]] = []

    for passport in file_passports:
        rel_path = str(passport.get("path", ""))
        file_kind = str(passport.get("file_kind", "UNKNOWN"))
        status = str(passport.get("status", "UNKNOWN"))
        cls = _classify_surface(rel_path, file_kind, status)
        counts[cls] = counts.get(cls, 0) + 1
        if len(samples[cls]) < 8:
            samples[cls].append(rel_path)

        projected.append(
            {
                "path": rel_path,
                "owner_organ": passport.get("owner_organ", "UNKNOWN"),
                "file_kind": file_kind,
                "status": status,
                "related_owner_pains": passport.get("related_owner_pains", []),
                "classification": cls,
                "projection_visibility": "SUMMARY_ONLY"
                if cls in {"PRIVATE_CONTEXT", "LOCAL_CONTEXT"}
                else "FULL",
            }
        )

    return {
        "classification_counts": counts,
        "classification_samples": samples,
        "classified_passports": projected,
    }


def _projection_passport(passport: Dict[str, Any]) -> Dict[str, Any]:
    cls = str(passport.get("classification", "UNKNOWN"))
    if cls in {"PRIVATE_CONTEXT", "LOCAL_CONTEXT"}:
        return {
            "path": "[RESTRICTED]",
            "owner_organ": passport.get("owner_organ", "UNKNOWN"),
            "file_kind": passport.get("file_kind", "UNKNOWN"),
            "status": passport.get("status", "UNKNOWN"),
            "classification": cls,
            "projection_visibility": "SUMMARY_ONLY",
        }
    return passport


def _build_report_receipt_summary(report_surface: Dict[str, Any]) -> Dict[str, Any]:
    report_paths = report_surface.get("report_paths", [])
    receipt_paths = report_surface.get("receipt_paths", [])
    if not isinstance(report_paths, list):
        report_paths = []
    if not isinstance(receipt_paths, list):
        receipt_paths = []

    return {
        "report_paths_count": len(report_paths),
        "receipt_paths_count": len(receipt_paths),
        "report_paths_sample": [str(item) for item in report_paths[:20]],
        "receipt_paths_sample": [str(item) for item in receipt_paths[:20]],
    }


def _build_owner_pain_surface(owner_pain_map: Dict[str, Any]) -> Dict[str, Any]:
    pains = owner_pain_map.get("pains", [])
    if not isinstance(pains, list):
        pains = []
    compact = []
    for pain in pains:
        if not isinstance(pain, dict):
            continue
        compact.append(
            {
                "pain_id": str(pain.get("pain_id", "UNKNOWN")),
                "owner_organ": str(pain.get("owner_organ", "UNKNOWN")),
                "severity": str(pain.get("severity", "UNKNOWN")),
                "current_status": str(pain.get("current_status", "UNKNOWN")),
                "next_task_route": str(pain.get("next_task_route", "")),
            }
        )
    return {"pain_count": len(compact), "pain_items": compact}


def _load_block_foundation_files(repo_root: Path) -> Tuple[Dict[str, Any], List[str]]:
    files = {
        "block_schema": BLOCK_FOUNDATION_DIR / "block_schema_v0_1.json",
        "block_registry_seed": BLOCK_FOUNDATION_DIR / "block_registry_seed_v0_1.json",
        "layout_manifest_schema": BLOCK_FOUNDATION_DIR / "layout_manifest_schema_v0_1.json",
        "theme_tokens": BLOCK_FOUNDATION_DIR / "theme_tokens_v0_1.json",
        "material_registry": BLOCK_FOUNDATION_DIR / "material_registry_v0_1.json",
        "animation_registry": BLOCK_FOUNDATION_DIR / "animation_registry_v0_1.json",
    }
    payload: Dict[str, Any] = {}
    warnings: List[str] = []
    for key, rel_path in files.items():
        abs_path = repo_root / rel_path
        if not abs_path.exists():
            warnings.append(f"MISSING_BLOCK_FOUNDATION::{rel_path.as_posix()}")
            payload[key] = {}
            continue
        try:
            payload[key] = _read_json(abs_path)
        except Exception as exc:  # pragma: no cover
            warnings.append(f"BLOCK_FOUNDATION_PARSE_ERROR::{rel_path.as_posix()}::{exc}")
            payload[key] = {}
    return payload, warnings


def _load_self_validator_surface(repo_root: Path) -> Dict[str, Any]:
    summary_path = repo_root / SELF_VALIDATOR_SUMMARY_PATH
    if not summary_path.exists():
        return {
            "status": "UNPROVEN",
            "summary_receipt_path": SELF_VALIDATOR_SUMMARY_PATH.as_posix(),
            "last_timestamp_utc": "",
        }
    try:
        payload = _read_json(summary_path)
    except Exception:
        return {
            "status": "STALE",
            "summary_receipt_path": SELF_VALIDATOR_SUMMARY_PATH.as_posix(),
            "last_timestamp_utc": "",
            "note": "Self-validator summary exists but is not parseable.",
        }
    return {
        "status": str(payload.get("status", "UNPROVEN")),
        "summary_receipt_path": SELF_VALIDATOR_SUMMARY_PATH.as_posix(),
        "last_timestamp_utc": str(payload.get("timestamp_utc", "")),
    }


def build_models(repo_root: Path | None = None) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    repo = (repo_root or discover_repo_root()).resolve()
    base_model = build_view_model_v0_1_dict(repo)
    classification_surface = _build_classification_surface(base_model.get("file_passports", []))
    report_receipt_summary = _build_report_receipt_summary(base_model.get("report_receipt_surface", {}))
    owner_pain_surface = _build_owner_pain_surface(base_model.get("owner_pain_map", {}))
    block_payload, block_warnings = _load_block_foundation_files(repo)
    self_validator_surface = _load_self_validator_surface(repo)

    generated_at_utc = _utc_now()
    guarded_projection = [
        _projection_passport(item) for item in classification_surface.get("classified_passports", [])
    ]
    restricted_count = sum(
        1 for item in guarded_projection if item.get("projection_visibility") == "SUMMARY_ONLY"
    )

    full_model = dict(base_model)
    full_model.update(
        {
            "task_id": TASK_ID,
            "schema_version": VIEW_MODEL_SCHEMA_VERSION,
            "generated_at_utc": generated_at_utc,
            "source_task_id": base_model.get("task_id", ""),
            "classification_surface": classification_surface,
            "report_receipt_summary": report_receipt_summary,
            "owner_pain_surface": owner_pain_surface,
            "projection_guard": {
                "private_local_restricted_count": restricted_count,
                "policy": "LOCAL_PRIVATE_REDACTED_IN_WEB_PROJECTION",
            },
            "block_foundation_preview": {
                "block_levels": ["L0_SYSTEM", "L1_ORGAN", "L2_MACRO", "L3_MICRO", "L4_LEAF_GROUP"],
                "registry_items_count": len(block_payload.get("block_registry_seed", {}).get("blocks", []))
                if isinstance(block_payload.get("block_registry_seed", {}), dict)
                else 0,
            },
            "self_validator_surface": {
                **self_validator_surface,
            },
        }
    )
    full_model["warnings"] = list(full_model.get("warnings", [])) + block_warnings

    dashboard_model = {
        "schema_version": DASHBOARD_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc,
        "task_id": TASK_ID,
        "truth": {
            "repo_root": full_model.get("truth", {}).get("repo_root", ""),
            "git": full_model.get("truth", {}).get("git", {}),
            "required_route_alias": full_model.get("truth", {}).get("required_alias", "imperium-vm3"),
        },
        "organs": full_model.get("organs", []),
        "atlas_summary": {
            "passport_count": len(full_model.get("file_passports", [])),
            "unknown_file_kind_count": full_model.get("unknown_file_kind_count", 0),
        },
        "language_gate_surface": full_model.get("language_gate_surface", {}),
        "route_surface": full_model.get("route_surface", {}),
        "report_receipt_summary": report_receipt_summary,
        "owner_pain_surface": owner_pain_surface,
        "warnings": full_model.get("warnings", []),
        "classification_counts": classification_surface.get("classification_counts", {}),
        "projection_guard": full_model.get("projection_guard", {}),
        "self_validator_surface": self_validator_surface,
        "file_passports_projection": guarded_projection[:400],
        "block_foundation_preview": full_model.get("block_foundation_preview", {}),
    }

    block_model = {
        "schema_version": BLOCK_VIEW_SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc,
        "task_id": TASK_ID,
        "block_schema": block_payload.get("block_schema", {}),
        "block_registry_seed": block_payload.get("block_registry_seed", {}),
        "layout_manifest_schema": block_payload.get("layout_manifest_schema", {}),
        "theme_tokens": block_payload.get("theme_tokens", {}),
        "material_registry": block_payload.get("material_registry", {}),
        "animation_registry": block_payload.get("animation_registry", {}),
        "warnings": block_warnings,
    }
    return full_model, dashboard_model, block_model


def build_and_persist_models(repo_root: Path | None = None) -> Dict[str, Any]:
    repo = (repo_root or discover_repo_root()).resolve()
    full_model, dashboard_model, block_model = build_models(repo)

    full_path = repo / VIEW_MODEL_DIR / "ide_view_model_v0_2.json"
    dashboard_path = repo / VIEW_MODEL_DIR / "dashboard_view_model_v0_1.json"
    block_path = repo / VIEW_MODEL_DIR / "block_view_model_v0_1.json"

    _write_json(full_path, full_model)
    _write_json(dashboard_path, dashboard_model)
    _write_json(block_path, block_model)

    return {
        "task_id": TASK_ID,
        "generated_at_utc": full_model.get("generated_at_utc", ""),
        "full_model_path": full_path.as_posix(),
        "dashboard_model_path": dashboard_path.as_posix(),
        "block_model_path": block_path.as_posix(),
        "passport_count": len(full_model.get("file_passports", [])),
        "warnings_count": len(full_model.get("warnings", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build shared Agent IDE V0.2 view models.")
    parser.add_argument("--repo-root", default="", help="Optional repository root override.")
    parser.add_argument("--no-write", action="store_true", help="Build models only without writing files.")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()
    if args.no_write:
        full_model, dashboard_model, block_model = build_models(repo)
        summary = {
            "task_id": TASK_ID,
            "generated_at_utc": full_model.get("generated_at_utc", ""),
            "passport_count": len(full_model.get("file_passports", [])),
            "dashboard_keys": sorted(dashboard_model.keys()),
            "block_keys": sorted(block_model.keys()),
            "warnings_count": len(full_model.get("warnings", [])),
        }
    else:
        summary = build_and_persist_models(repo)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
