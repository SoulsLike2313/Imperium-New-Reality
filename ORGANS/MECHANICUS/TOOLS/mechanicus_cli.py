from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ID = "TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1"
ROOT_MARKERS = ("AGENTS.md", "ORGANS")
TOOL_REGISTRY = "ORGANS/MECHANICUS/REGISTRY/tool_registry.json"
CAPABILITY_REGISTRY = "ORGANS/MECHANICUS/REGISTRY/capability_registry.json"
COMMAND_POLICY = "ORGANS/MECHANICUS/REGISTRY/command_policy.json"
JSON_FILES = [
    TOOL_REGISTRY,
    CAPABILITY_REGISTRY,
    COMMAND_POLICY,
    "ORGANS/MECHANICUS/SCHEMAS/tool_card.schema.json",
    "ORGANS/MECHANICUS/SCHEMAS/capability_record.schema.json",
    "ORGANS/MECHANICUS/SCHEMAS/command_receipt.schema.json",
    "ORGANS/MECHANICUS/SCHEMAS/tool_invocation.schema.json",
    "ORGANS/IMPERIAL_IDE/SCHEMAS/ide_extension_manifest.schema.json",
    "ORGANS/IMPERIAL_IDE/SCHEMAS/ide_workspace_state.schema.json",
    "ORGANS/IMPERIAL_IDE/SCHEMAS/ide_tool_invocation.schema.json",
    "ORGANS/IMPERIAL_IDE/SCHEMAS/ide_panel_registry.schema.json",
    "ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json",
    "ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_model.json",
    "ORGANS/IMPERIAL_IDE/SHELL/panel_registry.json",
    "ORGANS/IMPERIAL_IDE/SHELL/command_palette.json",
    "ORGANS/IMPERIAL_IDE/SHELL/shell_command_receipt.schema.json",
    "ORGANS/IMPERIAL_IDE/SHELL/shell_command_history.json",
    "ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json",
    "ORGANS/IMPERIAL_IDE/EXTENSIONS/example_mechanicus_extension.json",
]
PYTHON_FILES = [
    "ORGANS/MECHANICUS/TOOLS/mechanicus_cli.py",
    "ORGANS/MECHANICUS/TOOLS/mechanicus_doctor.py",
    "ORGANS/MECHANICUS/TOOLS/mechanicus_inventory.py",
    "ORGANS/MECHANICUS/TOOLS/mechanicus_validate.py",
    "ORGANS/MECHANICUS/TOOLS/mechanicus_command_gateway.py",
    "ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py",
    "ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_tui.py",
    "ORGANS/IMPERIAL_IDE/SHELL/shell_router.py",
    "ORGANS/IMPERIAL_IDE/SHELL/shell_state.py",
    "ORGANS/IMPERIAL_IDE/SHELL/shell_receipts.py",
    "ORGANS/IMPERIAL_IDE/BRIDGES/mechanicus_shell_bridge.py",
    "ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_loader.py",
    "ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state_manager.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "ORGANS").exists():
            return candidate
    raise SystemExit("repo_root_not_found")


def load_json(repo_root: Path, rel_path: str) -> object:
    with (repo_root / rel_path).open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def emit(data: object) -> int:
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def validate_json_files(repo_root: Path, paths: list[str]) -> dict:
    parsed = []
    missing = []
    invalid = []
    for rel_path in paths:
        path = repo_root / rel_path
        if not path.exists():
            missing.append(rel_path)
            continue
        try:
            load_json(repo_root, rel_path)
            parsed.append(rel_path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            invalid.append({"path": rel_path, "error": str(exc)})
    verdict = "PASS" if not missing and not invalid else "BLOCKED"
    return {"parsed": parsed, "missing": missing, "invalid": invalid, "verdict": verdict}


def command_receipt(tool_id: str, mode: str, verdict: str, **extra: object) -> dict:
    receipt = {
        "receipt_type": "mechanicus_command_receipt",
        "timestamp_utc": utc_now(),
        "task_id": TASK_ID,
        "tool_id": tool_id,
        "mode": mode,
        "dry_run": True,
        "arbitrary_shell_execution": False,
        "verdict": verdict,
    }
    receipt.update(extra)
    return receipt


def cmd_doctor(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    json_result = validate_json_files(repo_root, JSON_FILES)
    missing_py = [rel for rel in PYTHON_FILES if not (repo_root / rel).exists()]
    registry = load_json(repo_root, TOOL_REGISTRY)
    policy = load_json(repo_root, COMMAND_POLICY)
    verdict = "PASS_WITH_WARNINGS" if not missing_py and json_result["verdict"] == "PASS" else "BLOCKED"
    return emit(command_receipt(
        "MECHANICUS_DOCTOR",
        "doctor",
        verdict,
        repo_root=str(repo_root).replace("\\", "/"),
        json_parse=json_result,
        missing_python_files=missing_py,
        tool_count=len(registry.get("tools", [])),
        arbitrary_shell_execution_allowed=policy.get("arbitrary_shell_execution_allowed"),
        dry_run_required_by_default=policy.get("dry_run_required_by_default"),
        warnings=["Full real execution gateway is intentionally blocked."]
    ))


def cmd_inventory(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    registry = load_json(repo_root, TOOL_REGISTRY)
    capabilities = load_json(repo_root, CAPABILITY_REGISTRY)
    return emit({
        "receipt_type": "mechanicus_inventory",
        "timestamp_utc": utc_now(),
        "task_id": TASK_ID,
        "tools": registry.get("tools", []),
        "capabilities": capabilities.get("capabilities", []),
        "verdict": "PASS_WITH_WARNINGS"
    })


def cmd_validate_json(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    paths = args.paths or JSON_FILES
    result = validate_json_files(repo_root, paths)
    return emit(command_receipt("MECHANICUS_VALIDATE", "validate-json", result["verdict"], result=result))


def cmd_policy(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    return emit(load_json(repo_root, COMMAND_POLICY))


def cmd_list_tools(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    registry = load_json(repo_root, TOOL_REGISTRY)
    return emit({"tools": registry.get("tools", []), "verdict": "PASS"})


def cmd_list_capabilities(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    registry = load_json(repo_root, CAPABILITY_REGISTRY)
    return emit({"capabilities": registry.get("capabilities", []), "verdict": "PASS"})


def cmd_emit_receipt(args: argparse.Namespace) -> int:
    return emit(command_receipt(args.tool_id, args.mode, "PASS_WITH_WARNINGS", note="receipt emitted without executing a tool"))


def cmd_dry_run_tool(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    registry = load_json(repo_root, TOOL_REGISTRY)
    policy = load_json(repo_root, COMMAND_POLICY)
    tools = {tool.get("tool_id"): tool for tool in registry.get("tools", [])}
    allowlisted = set(policy.get("allowlisted_tool_ids_for_dry_run", []))
    tool = tools.get(args.tool_id)
    if tool is None:
        return emit(command_receipt("MECHANICUS_COMMAND_GATEWAY", "dry-run-tool", "BLOCKED", requested_tool_id=args.tool_id, reason="tool_not_registered"))
    if args.tool_id not in allowlisted:
        return emit(command_receipt("MECHANICUS_COMMAND_GATEWAY", "dry-run-tool", "BLOCKED", requested_tool_id=args.tool_id, reason="tool_not_allowlisted_for_dry_run"))
    return emit(command_receipt(
        "MECHANICUS_COMMAND_GATEWAY",
        "dry-run-tool",
        "PASS_WITH_WARNINGS",
        requested_tool_id=args.tool_id,
        resolved_tool=tool,
        executed=False,
        reason="dry_run_only"
    ))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mechanicus registry and dry-run gateway")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    sub.add_parser("inventory").set_defaults(func=cmd_inventory)
    validate = sub.add_parser("validate-json")
    validate.add_argument("paths", nargs="*")
    validate.set_defaults(func=cmd_validate_json)
    sub.add_parser("list-tools").set_defaults(func=cmd_list_tools)
    sub.add_parser("list-capabilities").set_defaults(func=cmd_list_capabilities)
    sub.add_parser("policy").set_defaults(func=cmd_policy)
    receipt = sub.add_parser("emit-receipt")
    receipt.add_argument("--tool-id", default="MECHANICUS_CLI")
    receipt.add_argument("--mode", default="emit-receipt")
    receipt.set_defaults(func=cmd_emit_receipt)
    dry = sub.add_parser("dry-run-tool")
    dry.add_argument("tool_id")
    dry.set_defaults(func=cmd_dry_run_tool)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
