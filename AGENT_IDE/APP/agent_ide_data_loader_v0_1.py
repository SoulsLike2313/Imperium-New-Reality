from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from agent_ide_models_v0_1 import FilePassport, IdeViewModel, ProviderDescriptor, TASK_ID


CONFIG_RELATIVE_PATH = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/APP/agent_ide_config_v0_1.json")
PROVIDER_REGISTRY_RELATIVE_PATH = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/PLUGINS/builtin_readonly_providers_v0_1.json"
)


def discover_repo_root(start: Optional[Path] = None) -> Path:
    cursor = (start or Path(__file__).resolve()).resolve()
    for path in [cursor, *cursor.parents]:
        if (path / ".git").exists():
            return path
    raise FileNotFoundError("Could not discover repo root (.git not found).")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(_read_text(path))


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in _read_text(path).splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _load_config(repo_root: Path) -> Dict[str, Any]:
    config_path = repo_root / CONFIG_RELATIVE_PATH
    return _read_json(config_path)


def _load_provider_descriptors(repo_root: Path) -> List[ProviderDescriptor]:
    raw_manifest = _read_json(repo_root / PROVIDER_REGISTRY_RELATIVE_PATH)
    providers = raw_manifest.get("providers", [])
    return [ProviderDescriptor.from_dict(item) for item in providers]


def _safe_git_truth(repo_root: Path) -> Dict[str, str]:
    git_dir = repo_root / ".git"
    head_file = git_dir / "HEAD"
    if not head_file.exists():
        return {"branch": "UNKNOWN", "head": "UNKNOWN"}

    head_value = _read_text(head_file).strip()
    if head_value.startswith("ref: "):
        ref = head_value.replace("ref: ", "", 1).strip()
        ref_path = git_dir / ref
        if ref_path.exists():
            return {"branch": Path(ref).name, "head": _read_text(ref_path).strip()}
        return {"branch": Path(ref).name, "head": "UNKNOWN"}
    return {"branch": "DETACHED", "head": head_value}


def _flatten_string_lists(payload: Dict[str, Any], keys: Iterable[str]) -> List[str]:
    out: List[str] = []
    for key in keys:
        value = payload.get(key, [])
        if isinstance(value, list):
            out.extend(str(x) for x in value)
    return out


def _find_canonical_command_file(route_surface: Dict[str, Any]) -> Optional[str]:
    candidates = []
    for key in ("alias_evidence_paths", "route_connection_surface_paths", "notable_route_cards"):
        value = route_surface.get(key, [])
        if isinstance(value, list):
            candidates.extend(str(x) for x in value)
    for rel_path in candidates:
        if rel_path.lower().endswith("canonical_transfer_commands.md"):
            return rel_path
    return None


def _compute_organs(required_organs: List[str], file_passports: List[FilePassport], atlas_index: Dict[str, Any]) -> List[Dict[str, Any]]:
    counts_from_index = atlas_index.get("counts_by_organ", {})
    computed_counts: Dict[str, int] = {}
    for passport in file_passports:
        organ = passport.owner_organ.upper()
        computed_counts[organ] = computed_counts.get(organ, 0) + 1

    organs: List[Dict[str, Any]] = []
    for organ in required_organs:
        count = int(counts_from_index.get(organ, computed_counts.get(organ, 0)))
        status = "VISIBLE" if count > 0 else "MISSING_OR_ZERO"
        organs.append({"organ": organ, "file_count": count, "status": status})
    return organs


def build_view_model(repo_root: Optional[Path] = None) -> IdeViewModel:
    repo = (repo_root or discover_repo_root()).resolve()
    config = _load_config(repo)
    required_organs = [str(x).upper() for x in config.get("required_organs", [])]
    required_alias = str(config.get("required_route_alias", "imperium-vm3"))

    providers = _load_provider_descriptors(repo)
    payloads: Dict[str, Any] = {}
    warnings: List[str] = []
    loaded_sources: Dict[str, str] = {}
    missing_sources: List[str] = []

    for descriptor in providers:
        if not descriptor.enabled:
            continue
        source_path = (repo / descriptor.relative_path).resolve()
        if not source_path.exists():
            message = f"MISSING_SOURCE::{descriptor.source_key}::{descriptor.relative_path}"
            if descriptor.required:
                warnings.append(message)
            else:
                warnings.append(f"WARN_{message}")
            missing_sources.append(descriptor.source_key)
            continue

        try:
            if descriptor.parse_mode == "jsonl":
                payloads[descriptor.source_key] = _read_jsonl(source_path)
            else:
                payloads[descriptor.source_key] = _read_json(source_path)
            loaded_sources[descriptor.source_key] = descriptor.relative_path
        except Exception as exc:  # pragma: no cover - defensive for malformed input
            warnings.append(f"PARSE_ERROR::{descriptor.source_key}::{exc}")

    raw_passports = payloads.get("file_passports", [])
    passports = [FilePassport.from_dict(item) for item in raw_passports if isinstance(item, dict)]
    atlas_index = payloads.get("file_atlas_index", {})

    unknown_from_index = atlas_index.get("unknown_file_kind_count")
    if isinstance(unknown_from_index, int):
        unknown_count = unknown_from_index
    else:
        unknown_count = sum(1 for item in passports if item.file_kind.upper() == "UNKNOWN")

    unknown_sample = [p.path for p in passports if p.file_kind.upper() == "UNKNOWN"][:25]
    if unknown_count > 0:
        warnings.append(f"UNKNOWN_FILE_KIND_COUNT::{unknown_count}")

    role_rule = payloads.get("role_rule_surface_index", {})
    language_gate = payloads.get("language_gate_surface_index", {})
    checker_tool = payloads.get("checker_tool_index", {})
    tui_surface = payloads.get("tui_surface_index", {})
    report_surface = payloads.get("report_receipt_index", {})
    route_surface = payloads.get("route_connection_surface_index", {})
    owner_pain = payloads.get("owner_pain_to_file_map", {})
    gap_success = payloads.get("gap_success_index", {})

    route_paths_concat = " ".join(
        _flatten_string_lists(
            route_surface,
            ("alias_evidence_paths", "route_connection_surface_paths", "notable_route_cards"),
        )
    ).lower()
    alias_detected = bool(route_surface.get("alias_detected", False))
    alias_required = str(route_surface.get("required_alias", required_alias))
    alias_visible = alias_detected or required_alias.lower() in route_paths_concat

    canonical_commands_rel = _find_canonical_command_file(route_surface)
    canonical_commands_preview = ""
    if canonical_commands_rel:
        candidate_path = repo / canonical_commands_rel
        if candidate_path.exists():
            lines = _read_text(candidate_path).splitlines()
            canonical_commands_preview = "\n".join(lines[:80])

    route_surface_enriched = dict(route_surface)
    route_surface_enriched["required_alias"] = alias_required
    route_surface_enriched["imperium_vm3_visible"] = alias_visible
    route_surface_enriched["canonical_commands_file"] = canonical_commands_rel or ""
    route_surface_enriched["canonical_commands_preview"] = canonical_commands_preview

    truth = {
        "repo_root": str(repo),
        "loaded_sources": loaded_sources,
        "missing_sources": missing_sources,
        "required_alias": required_alias,
        "git": _safe_git_truth(repo),
    }

    view_model = IdeViewModel(
        task_id=TASK_ID,
        truth=truth,
        warnings=warnings,
        organs=_compute_organs(required_organs, passports, atlas_index),
        file_passports=[item.to_dict() for item in passports],
        unknown_file_kind_count=unknown_count,
        role_rule_surface=role_rule,
        language_gate_surface=language_gate,
        checker_tool_surface=checker_tool,
        tui_surface=tui_surface,
        report_receipt_surface=report_surface,
        route_surface=route_surface_enriched,
        owner_pain_map=owner_pain,
        gap_success=gap_success,
        selected_file=passports[0].to_dict() if passports else {},
    )

    view_model.route_surface["unknown_file_kind_paths_sample"] = unknown_sample
    return view_model


def build_view_model_dict(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    return build_view_model(repo_root).to_dict()

