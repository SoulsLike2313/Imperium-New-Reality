"""Machine inventory for the real Rust Tauri invoke surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context


TASK_ID = "IMPERIUM_CORE_TRUTH_HARDENING_0002"
REPORT_RELATIVE = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002")
MAIN_RELATIVE = Path("SUPPORT/APP_TAURI/src-tauri/src/main.rs")
RUST_RELATIVE = Path("SUPPORT/APP_TAURI/src-tauri/src")
API_RELATIVE = Path("SUPPORT/APP_TAURI/src/corridor/api.js")
SERVICE_RELATIVE = Path("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/service.py")
REGISTRY_RELATIVE = Path("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/registry.py")
BRIDGE_RELATIVE = Path("SUPPORT/APP_TAURI/src-tauri/src/corridor/bridge.rs")

REQUIRED_LEGACY = (
    "register_patch_pack",
    "register_patch_pack_with_organs",
    "record_runtime_fps_proof",
    "initialize_imperium_core_update",
)
LEGACY_DEFINITIONS = (
    "get_imperium_core_version_state",
    "initialize_imperium_core_update",
    "list_patch_packs",
    "register_patch_pack",
    "get_mechanicus_language_codex",
    "analyze_patch_pack_organ_summary",
    "register_patch_pack_with_organs",
    "record_runtime_fps_proof",
)
CANONICAL_COMMANDS = {
    "corridor_ui_snapshot": "READ_ONLY",
    "corridor_ui_action": "MUTATING",
}
MUTATION_PATTERNS = (
    r"fs::write\s*\(",
    r"fs::create_dir",
    r"write_registry\s*\(",
    r"write_receipt\s*\(",
    r"File::create\s*\(",
    r"remove_(?:file|dir)",
    r"Command::new\s*\(",
    r"analyze_patch_pack_core\([^;]*true\)",
)
READ_PATTERNS = (
    r"fs::read",
    r"read_to_string",
    r"read_registry\s*\(",
    r"analyze_patch_pack_core\([^;]*false\)",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_hash(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("receipt_hash", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_invoke_handler(source: str) -> list[str]:
    matches = re.findall(r"invoke_handler\s*\(\s*tauri::generate_handler!\s*\[([\s\S]*?)\]\s*\)", source)
    if len(matches) != 1:
        raise ValueError(f"expected one Rust invoke_handler, found {len(matches)}")
    commands = []
    for raw in matches[0].split(","):
        value = re.sub(r"//.*", "", raw).strip()
        if value:
            commands.append(value)
    if not commands or len(commands) != len(set(commands)):
        raise ValueError("Rust invoke_handler is empty or contains duplicates")
    return commands


def parse_frontend_commands(source: str) -> list[str]:
    block = re.search(r"CORRIDOR_BRIDGE_COMMANDS\s*=\s*Object\.freeze\s*\(\s*\{([\s\S]*?)\}\s*\)", source)
    if not block:
        raise ValueError("frontend corridor command contract is missing")
    return re.findall(r"\w+\s*:\s*[\"']([^\"']+)[\"']", block.group(1))


def _extract_function(source: str, name: str) -> str | None:
    match = re.search(rf"(?:pub\s+)?fn\s+{re.escape(name)}\s*\([^)]*\)[^{{]*\{{", source)
    if not match:
        return None
    start = source.find("{", match.start())
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[match.start() : index + 1]
    return None


def classify_effect(function_body: str | None) -> str:
    if not function_body:
        return "UNKNOWN"
    if any(re.search(pattern, function_body) for pattern in MUTATION_PATTERNS):
        return "MUTATING"
    if any(re.search(pattern, function_body) for pattern in READ_PATTERNS):
        return "READ_ONLY"
    return "UNKNOWN"


def evaluate_surface(records: list[dict[str, Any]], legacy: list[dict[str, Any]], frontend_unknown: list[str]) -> dict[str, Any]:
    unknown = [row["command"] for row in records if row["effect"] == "UNKNOWN"]
    unregistered = [
        row["command"]
        for row in records
        if row["effect"] == "MUTATING"
        and not row.get("canonical_capability_registry_routed", False)
    ]
    unrouted = [row["command"] for row in records if row["effect"] == "MUTATING" and not row["typed_executor_routed"]]
    ungated = [row["command"] for row in records if row["effect"] == "MUTATING" and not row["owner_gate_required"]]
    legacy_reachable = [row["command"] for row in legacy if row["effect"] == "MUTATING" and row["corridor_reachable"]]
    checks = {
        "unknown_effects_absent": not unknown,
        "mutating_commands_capability_registry_routed": not unregistered,
        "mutating_commands_typed_executor_routed": not unrouted,
        "mutating_commands_owner_gated": not ungated,
        "legacy_mutating_commands_unreachable": not legacy_reachable,
        "frontend_unknown_commands_absent": not frontend_unknown,
    }
    return {
        "checks": checks,
        "unknown_commands": unknown,
        "unregistered_mutating_commands": unregistered,
        "unrouted_mutating_commands": unrouted,
        "ungated_mutating_commands": ungated,
        "reachable_legacy_mutations": legacy_reachable,
        "frontend_unknown_commands": frontend_unknown,
        "surface_verdict": "LEGACY_MUTATION_SURFACE_CLOSED" if all(checks.values()) else "PHASE_3_BLOCKED",
    }


def _rust_sources(root: Path) -> tuple[dict[Path, str], dict[str, tuple[Path, str]]]:
    sources: dict[Path, str] = {}
    functions: dict[str, tuple[Path, str]] = {}
    for path in sorted((root / RUST_RELATIVE).rglob("*.rs")):
        source = path.read_text(encoding="utf-8")
        sources[path] = source
        for name in set([*LEGACY_DEFINITIONS, *CANONICAL_COMMANDS]):
            body = _extract_function(source, name)
            if body:
                functions[name] = (path, body)
    return sources, functions


def build_inventory(root: Path) -> dict[str, Any]:
    main_path = root / MAIN_RELATIVE
    api_path = root / API_RELATIVE
    service_path = root / SERVICE_RELATIVE
    registry_path = root / REGISTRY_RELATIVE
    bridge_path = root / BRIDGE_RELATIVE
    main_source = main_path.read_text(encoding="utf-8")
    api_source = api_path.read_text(encoding="utf-8")
    service_source = service_path.read_text(encoding="utf-8")
    registry_source = registry_path.read_text(encoding="utf-8")
    bridge_source = bridge_path.read_text(encoding="utf-8")
    full_commands = parse_invoke_handler(main_source)
    registered = [item.split("::")[-1] for item in full_commands]
    frontend = parse_frontend_commands(api_source)
    sources, functions = _rust_sources(root)
    route_evidence = {
        "fixed_corridor_cli_route": "run_corridor_cli(" in bridge_source and '"ui-action"' in bridge_source,
        "canonical_registry_lookup": "self.registry.action(action_id)" in service_source,
        "typed_executor_dispatch": "execute_capability(" in service_source and "return self.execute_demo()" in service_source,
        "owner_gate_dispatch": "self.owner_gate.record_decision(" in service_source and "self.owner_gate.check(" in service_source,
        "registry_default_deny": '"default_policy": "DENY"' in registry_source,
    }
    route_proven = all(route_evidence.values())
    records: list[dict[str, Any]] = []
    for full, command in zip(full_commands, registered):
        function_path, body = functions.get(command, (main_path, None))
        effect = CANONICAL_COMMANDS.get(command, classify_effect(body))
        canonical_action = command == "corridor_ui_action"
        records.append(
            {
                "command": command,
                "rust_handler_entry": full,
                "effect": effect,
                "corridor_reachable": True,
                "canonical_capability_registry_routed": route_proven if canonical_action else False,
                "typed_executor_routed": route_proven if canonical_action else False,
                "owner_gate_required": route_proven if canonical_action else False,
                "legacy_command": command in LEGACY_DEFINITIONS,
                "definition_path": function_path.relative_to(root).as_posix(),
                "direct_invocation": "ADMITTED_BY_RUST_INVOKE_HANDLER",
            }
        )
    legacy: list[dict[str, Any]] = []
    for command in LEGACY_DEFINITIONS:
        function_path, body = functions.get(command, (main_path, None))
        registered_now = command in registered
        legacy.append(
            {
                "command": command,
                "effect": classify_effect(body),
                "required_attention": command in REQUIRED_LEGACY,
                "rust_command_attribute_present": bool(re.search(rf"#\[tauri::command\]\s*(?:pub\s+)?fn\s+{re.escape(command)}\s*\(", main_source)),
                "registered_in_invoke_handler": registered_now,
                "corridor_reachable": registered_now,
                "definition_path": function_path.relative_to(root).as_posix(),
                "direct_invocation_result": "ADMITTED" if registered_now else "BLOCK_COMMAND_NOT_REGISTERED",
            }
        )
    frontend_unknown = sorted(set(frontend) - set(registered))
    result = evaluate_surface(records, legacy, frontend_unknown)
    inventory: dict[str, Any] = {
        "schema_version": "imperium.core_reference_corridor.tauri_command_inventory.v1",
        "task_id": TASK_ID,
        "generated_at_utc": _utc_now(),
        "inventory_method": "PARSE_REAL_RUST_INVOKE_HANDLER_NOT_FRONTEND_DECLARATIONS",
        "generator": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__))},
        "rust_invoke_source": {"path": MAIN_RELATIVE.as_posix(), "sha256": sha256_file(main_path)},
        "registered_tauri_commands": registered,
        "rust_handler_entries": full_commands,
        "effect_classification": {row["command"]: row["effect"] for row in records},
        "commands": records,
        "legacy_command_probes": legacy,
        "required_legacy_commands": list(REQUIRED_LEGACY),
        "frontend_declared_commands": frontend,
        "route_evidence": route_evidence,
        "source_hashes": {path.relative_to(root).as_posix(): sha256_file(path) for path in sources},
        **result,
        "campaign_verdict": "TRUTH_HARDENING_PARTIAL_NOT_READY",
        "phase_4_started": False,
    }
    inventory["receipt_hash"] = _canonical_hash(inventory)
    return inventory


def write_inventory(root: Path, output: Path, audit: Path) -> dict[str, Any]:
    inventory = build_inventory(root)
    atomic_write_json(output, inventory)
    lines = [
        "# Phase 3 — Tauri Surface Audit",
        "",
        f"- Rust invoke source: `{inventory['rust_invoke_source']['path']}`",
        f"- Registered commands: `{len(inventory['registered_tauri_commands'])}`",
        f"- Surface verdict: `{inventory['surface_verdict']}`",
        "- Inventory source: real Rust `invoke_handler`; frontend declarations are parity evidence only.",
        "- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`",
        "- Phase 4: `NOT_STARTED`",
        "",
        "## Registered surface",
        "",
    ]
    lines.extend(f"- `{row['command']}` — `{row['effect']}`" for row in inventory["commands"])
    lines.extend(["", "## Legacy direct invocation probes", ""])
    lines.extend(f"- `{row['command']}` — `{row['effect']}` — `{row['direct_invocation_result']}`" for row in inventory["legacy_command_probes"])
    audit.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", required=True)
    args = parser.parse_args(argv)
    context = resolve_repository_context(".")
    root = Path(context.worktree_root)
    report = root / REPORT_RELATIVE
    inventory = write_inventory(root, report / "TAURI_COMMAND_INVENTORY.json", report / "TAURI_SURFACE_AUDIT.md")
    print(json.dumps({"verdict": inventory["surface_verdict"], "registered_tauri_commands": inventory["registered_tauri_commands"]}, sort_keys=True))
    return 0 if inventory["surface_verdict"] == "LEGACY_MUTATION_SURFACE_CLOSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
