from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import default_runs_path, resolve_repo_path  # noqa: E402

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    Console = None  # type: ignore[assignment]
    Layout = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]

TASK_ID_DEFAULT = "TASK-20260519-COMMON-AGENT-CLI-KILO-LIKE-HERALDRY-V0_1"
STATUS_READY = "FOUNDATION_V0_1_READY_FOR_REVIEW"

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = resolve_repo_path(start=Path(__file__))
DEFAULT_RUNTIME_ROOT = default_runs_path("OFFICIO_AGENTIS", "RUNS", start=Path(__file__))
COMMON_CLI_ROOT = REPO_ROOT / "COMMON_AGENT_CLI"
if str(COMMON_CLI_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_CLI_ROOT))

from tool_registry_reader import build_organ_tool_view, default_tool_index_path

ROLE_REGISTRY = ROOT / "ROLE_REGISTRY"
MODE_REGISTRY = ROOT / "MODE_REGISTRY"
SETTINGS_REGISTRY = ROOT / "SETTINGS_REGISTRY"
RESPONSE_CONTRACTS = ROOT / "RESPONSE_CONTRACTS"
EVIDENCE_POLICY_DIR = ROOT / "EVIDENCE_POLICY"
SCHEMAS_DIR = ROOT / "SCHEMAS"
EXAMPLES_DIR = ROOT / "EXAMPLES"
COMMUNICATION_CONTRACT_MD = SETTINGS_REGISTRY / "communication" / "SERVITOR_COMMUNICATION_CONTRACT.md"
COMMUNICATION_CONTRACT_JSON = SETTINGS_REGISTRY / "communication" / "servitor_communication_contract.json"
BOOTSTRAP_EXECUTION_DIRECTIVE_MD = SETTINGS_REGISTRY / "communication" / "OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE.md"
BOOTSTRAP_EXECUTION_DIRECTIVE_JSON = SETTINGS_REGISTRY / "communication" / "officio_bootstrap_execution_directive.json"
LANGUAGE_EXECUTION_CONTRACT_MD = SETTINGS_REGISTRY / "communication" / "LANGUAGE_EXECUTION_CONTRACT.md"
LANGUAGE_EXECUTION_CONTRACT_JSON = SETTINGS_REGISTRY / "communication" / "language_execution_contract.json"
ROLE_SETTINGS_ACK_PROTOCOL_MD = RESPONSE_CONTRACTS / "ROLE_SETTINGS_ACK_PROTOCOL.md"
ROLE_SETTINGS_ACK_PROTOCOL_JSON = RESPONSE_CONTRACTS / "ROLE_SETTINGS_ACK_PROTOCOL.json"

SHELL_MODES = ["ASK", "ARCHITECT", "IMPLEMENT", "DEBUG", "AUDIT", "ORCHESTRATE"]
DEFAULT_SHELL_MODE = "ASK"
BOUNDARY_MESSAGE = (
    "This is IMPERIUM agent shell, not PowerShell. "
    "Use /exit for PowerShell, or /run <command> only if the current mode permits command execution."
)
RUN_ALLOWED_SHELL_MODES = {"IMPLEMENT", "DEBUG", "ORCHESTRATE"}

ROLE_RESPONSE_CONTRACT_FILE = {
    "SERVITOR": "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md",
    "SERVITOR_PRIME": "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md",
    "SERVITOR_SPECULUM": "SERVITOR_SPECULUM_AUDIT_RESPONSE_CONTRACT.md",
    "LOGOS": "LOGOS_PRIME_RESPONSE_CONTRACT.md",
    "LOGOS_PRIME": "LOGOS_PRIME_RESPONSE_CONTRACT.md",
    "LOGOS_SPECULUM": "LOGOS_SPECULUM_RESPONSE_CONTRACT.md",
}

ROLE_FALLBACK_ALIASES = {
    "SERVITOR": "SERVITOR_PRIME",
    "LOGOS": "LOGOS_PRIME",
}

OFFICIO_ROLE_USAGE = "SERVITOR|SERVITOR_PRIME|SERVITOR_SPECULUM|LOGOS|LOGOS_PRIME|LOGOS_SPECULUM"

OFFICIO_SETTING_REQUIRED_FIELDS = [
    "setting_id",
    "title",
    "version",
    "state",
    "scope",
    "applies_to_roles",
    "applies_to_modes",
    "machine_rule",
    "human_summary",
    "acceptance_tests",
    "evidence_required",
    "dependencies",
    "conflicts_with",
    "supersedes",
    "rollback_plan",
    "owner_approval_required",
]


@dataclass
class CommandContext:
    command: str
    runtime_root: Path
    run_root: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_runtime_root() -> Path:
    runtime_env = None
    for key in ("OFFICIO_RUNTIME_ROOT", "IMPERIUM_OFFICIO_RUNTIME_ROOT"):
        env_value = os.environ.get(key)
        if env_value:
            runtime_env = Path(env_value)
            break
    runtime_root = runtime_env if runtime_env else DEFAULT_RUNTIME_ROOT
    runtime_root.mkdir(parents=True, exist_ok=True)
    return runtime_root


def create_context(command: str) -> CommandContext:
    runtime_root = get_runtime_root()
    run_root = runtime_root / f"run_{utc_stamp()}_{command.replace('-', '_')}"
    run_root.mkdir(parents=True, exist_ok=True)
    return CommandContext(command=command, runtime_root=runtime_root, run_root=run_root)


def emit_receipt(ctx: CommandContext, receipt_name: str, payload: dict[str, Any]) -> Path:
    receipt_path = ctx.run_root / "receipts" / receipt_name
    write_json(receipt_path, payload)
    return receipt_path


def print_artifacts(label_to_path: dict[str, Path]) -> None:
    for label, path in label_to_path.items():
        print(f"{label}: {path}")


def git_info() -> dict[str, str]:
    def run(args: list[str]) -> str:
        try:
            out = subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True)
            return out.strip()
        except Exception:
            return "UNKNOWN"

    head = run(["rev-parse", "HEAD"])
    branch = run(["branch", "--show-current"])
    status = run(["status", "--short"])
    return {
        "head": head,
        "branch": branch,
        "dirty": "yes" if status else "no",
        "status_short": status if status else "<clean>",
    }


def load_role_aliases() -> dict[str, str]:
    aliases: dict[str, str] = dict(ROLE_FALLBACK_ALIASES)
    alias_path = ROLE_REGISTRY / "ROLE_ALIASES.json"
    if alias_path.exists():
        try:
            payload = read_json(alias_path)
            raw_aliases = payload.get("aliases", {}) if isinstance(payload, dict) else {}
            if isinstance(raw_aliases, dict):
                for key, value in raw_aliases.items():
                    aliases[str(key).strip().upper()] = str(value).strip().upper()
        except Exception:
            pass
    return aliases


def available_agents() -> list[str]:
    roles: set[str] = set(ROLE_RESPONSE_CONTRACT_FILE.keys())
    index_path = ROLE_REGISTRY / "ROLE_INDEX.json"
    if index_path.exists():
        try:
            payload = read_json(index_path)
            for item in payload.get("canonical_roles", []):
                if isinstance(item, dict) and item.get("role_id"):
                    roles.add(str(item["role_id"]).strip().upper())
            for key, value in payload.get("legacy_aliases", {}).items():
                roles.add(str(key).strip().upper())
                roles.add(str(value).strip().upper())
        except Exception:
            pass
    for child in ROLE_REGISTRY.iterdir() if ROLE_REGISTRY.exists() else []:
        if child.is_dir() and (child / "role_profile.json").exists():
            roles.add(child.name.upper())
    roles.update(load_role_aliases().keys())
    return sorted(roles)


def resolve_agent_id(value: str) -> str:
    normalized = value.strip().upper()
    aliases = load_role_aliases()
    return aliases.get(normalized, normalized)


def valid_agent(value: str) -> str:
    resolved = resolve_agent_id(value)
    role_json = ROLE_REGISTRY / resolved / "role_profile.json"
    if not role_json.exists():
        allowed = ", ".join(available_agents())
        raise ValueError(f"Unsupported agent '{value}'. Resolved='{resolved}'. Allowed: {allowed}")
    return resolved


def valid_mode(value: str) -> str:
    normalized = value.strip().upper()
    allowed = {"EXECUTOR", "AUDITOR", "ARCHITECT", "REPAIRER"}
    if normalized not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(f"Unsupported mode '{value}'. Allowed: {allowed_text}")
    return normalized


def safe_list(obj: dict[str, Any], key: str) -> list[str]:
    value = obj.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def load_role_profile(agent: str) -> dict[str, Any]:
    canonical = valid_agent(agent)
    return read_json(ROLE_REGISTRY / canonical / "role_profile.json")


def load_mode_profile(mode: str) -> dict[str, Any]:
    return read_json(MODE_REGISTRY / mode / "mode_profile.json")


def load_permissions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "permissions" / "permissions.json")


def load_forbidden_actions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "forbidden_actions" / "forbidden_actions.json")


def load_stop_conditions() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "stop_conditions" / "stop_conditions.json")


def load_evidence_policy() -> dict[str, Any]:
    return read_json(EVIDENCE_POLICY_DIR / "evidence_policy.json")


def load_settings_index() -> dict[str, Any]:
    return read_json(SETTINGS_REGISTRY / "settings_index.json")


def response_contract_path_for(agent: str) -> Path:
    canonical = valid_agent(agent)
    ref_path = ROLE_REGISTRY / canonical / "response_contract_ref.json"
    if ref_path.exists():
        try:
            ref = read_json(ref_path)
            rel = ref.get("response_contract_path")
            if rel:
                candidate = ROOT / str(rel)
                if candidate.exists():
                    return candidate
        except Exception:
            pass
    filename = ROLE_RESPONSE_CONTRACT_FILE.get(canonical)
    if filename:
        return RESPONSE_CONTRACTS / filename
    raise ValueError(f"No response contract mapped for agent '{agent}' resolved as '{canonical}'")


def build_execution_settings(agent: str, mode: str) -> tuple[dict[str, Any], str]:
    role = load_role_profile(agent)
    mode_profile = load_mode_profile(mode)
    permissions = load_permissions()
    forbidden = load_forbidden_actions()
    stops = load_stop_conditions()
    evidence = load_evidence_policy()
    contract_path = response_contract_path_for(agent)

    settings = {
        "task_id_default": TASK_ID_DEFAULT,
        "agent": agent,
        "mode": mode,
        "role_profile": role,
        "mode_profile": mode_profile,
        "permissions": permissions,
        "forbidden_actions": forbidden,
        "stop_conditions": stops.get("stop_conditions", []),
        "response_contract_file": str(contract_path.relative_to(ROOT)),
        "evidence_policy": evidence,
    }

    md = "\n".join(
        [
            f"# Execution Settings: {agent} / {mode}",
            "",
            f"- task_id_default: `{TASK_ID_DEFAULT}`",
            f"- response_contract: `{contract_path.name}`",
            "",
            "## Role Obligations",
            *[f"- {entry}" for entry in safe_list(role, "obligations")],
            "",
            "## Mode Intent",
            f"- {mode_profile.get('intent', 'n/a')}",
            "",
            "## Core Permissions",
            *[f"- {entry}" for entry in safe_list(permissions, "global_permissions")],
            "",
            "## Forbidden Actions",
            *[f"- {entry}" for entry in safe_list(forbidden, "forbidden_actions")],
            "",
            "## Stop Conditions",
            *[f"- {item.get('code', 'UNKNOWN')}" for item in stops.get("stop_conditions", [])],
            "",
            "## Evidence Law",
            "- No evidence = no DONE.",
        ]
    )
    return settings, md


def cmd_status(_args: argparse.Namespace) -> int:
    ctx = create_context("status")
    g = git_info()
    payload = {
        "task_id_default": TASK_ID_DEFAULT,
        "status": STATUS_READY,
        "root": str(ROOT),
        "runtime_root": str(ctx.runtime_root),
        "supported_agents": sorted(ROLE_RESPONSE_CONTRACT_FILE.keys()),
        "supported_modes": ["EXECUTOR", "AUDITOR", "ARCHITECT", "REPAIRER"],
        "git": g,
        "timestamp_utc": utc_now(),
    }
    status_json = ctx.run_root / "status" / "status.json"
    status_md = ctx.run_root / "status" / "STATUS.md"
    write_json(status_json, payload)
    write_text(
        status_md,
        "\n".join(
            [
                "# Officio Status",
                "",
                f"- status: `{STATUS_READY}`",
                f"- root: `{ROOT}`",
                f"- runtime_root: `{ctx.runtime_root}`",
                f"- git_head: `{g['head']}`",
                f"- git_branch: `{g['branch']}`",
                f"- git_dirty: `{g['dirty']}`",
            ]
        )
        + "\n",
    )
    receipt = emit_receipt(
        ctx,
        "status_receipt.json",
        {"command": "status", "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(status_json), str(status_md)]},
    )
    print_artifacts({"STATUS_JSON": status_json, "STATUS_MD": status_md, "RECEIPT": receipt})
    return 0


def cmd_role_get(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    ctx = create_context("role_get")
    source_md = ROLE_REGISTRY / agent / "ROLE_PROFILE.md"
    source_json = ROLE_REGISTRY / agent / "role_profile.json"
    out_dir = ctx.run_root / "role_get" / agent
    out_md = out_dir / "ROLE_PROFILE.md"
    out_json = out_dir / "role_profile.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_md, out_md)
    shutil.copy2(source_json, out_json)

    receipt = emit_receipt(
        ctx,
        f"role_get_{agent}_receipt.json",
        {"command": "role-get", "agent": agent, "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_md), str(out_json)]},
    )
    print_artifacts({"ROLE_PROFILE_MD": out_md, "ROLE_PROFILE_JSON": out_json, "RECEIPT": receipt})
    return 0


def cmd_settings_get(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
        mode = valid_mode(args.mode)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    ctx = create_context("settings_get")
    settings, settings_md = build_execution_settings(agent, mode)
    out_dir = ctx.run_root / "settings_get" / f"{agent}_{mode}"
    out_dir.mkdir(parents=True, exist_ok=True)

    settings_md_path = out_dir / "EXECUTION_SETTINGS.md"
    settings_json_path = out_dir / "execution_settings.json"
    stop_conditions_path = out_dir / "STOP_CONDITIONS.json"
    response_contract_path = out_dir / "RESPONSE_CONTRACT.md"
    evidence_policy_path = out_dir / "EVIDENCE_POLICY.md"
    communication_contract_md_path = out_dir / "COMMUNICATION_CONTRACT.md"
    communication_contract_json_path = out_dir / "communication_contract.json"
    bootstrap_directive_md_path = out_dir / "OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE.md"
    bootstrap_directive_json_path = out_dir / "officio_bootstrap_execution_directive.json"
    language_execution_contract_md_path = out_dir / "LANGUAGE_EXECUTION_CONTRACT.md"
    language_execution_contract_json_path = out_dir / "language_execution_contract.json"
    role_settings_ack_protocol_md_path = out_dir / "ROLE_SETTINGS_ACK_PROTOCOL.md"
    role_settings_ack_protocol_json_path = out_dir / "ROLE_SETTINGS_ACK_PROTOCOL.json"

    write_text(settings_md_path, settings_md + "\n")
    write_json(settings_json_path, settings)
    write_json(stop_conditions_path, load_stop_conditions())
    write_text(response_contract_path, read_text(response_contract_path_for(agent)))
    write_text(evidence_policy_path, read_text(EVIDENCE_POLICY_DIR / "EVIDENCE_POLICY.md"))
    write_text(communication_contract_md_path, read_text(COMMUNICATION_CONTRACT_MD))
    write_json(communication_contract_json_path, read_json(COMMUNICATION_CONTRACT_JSON))
    write_text(bootstrap_directive_md_path, read_text(BOOTSTRAP_EXECUTION_DIRECTIVE_MD))
    write_json(bootstrap_directive_json_path, read_json(BOOTSTRAP_EXECUTION_DIRECTIVE_JSON))
    write_text(language_execution_contract_md_path, read_text(LANGUAGE_EXECUTION_CONTRACT_MD))
    write_json(language_execution_contract_json_path, read_json(LANGUAGE_EXECUTION_CONTRACT_JSON))
    write_text(role_settings_ack_protocol_md_path, read_text(ROLE_SETTINGS_ACK_PROTOCOL_MD))
    write_json(role_settings_ack_protocol_json_path, read_json(ROLE_SETTINGS_ACK_PROTOCOL_JSON))

    receipt = emit_receipt(
        ctx,
        f"settings_get_{agent}_{mode}_receipt.json",
        {
            "command": "settings-get",
            "agent": agent,
            "mode": mode,
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "outputs": [
                str(settings_md_path),
                str(settings_json_path),
                str(stop_conditions_path),
                str(response_contract_path),
                str(evidence_policy_path),
                str(communication_contract_md_path),
                str(communication_contract_json_path),
                str(bootstrap_directive_md_path),
                str(bootstrap_directive_json_path),
                str(language_execution_contract_md_path),
                str(language_execution_contract_json_path),
                str(role_settings_ack_protocol_md_path),
                str(role_settings_ack_protocol_json_path),
            ],
        },
    )
    print_artifacts(
        {
            "EXECUTION_SETTINGS_MD": settings_md_path,
            "EXECUTION_SETTINGS_JSON": settings_json_path,
            "STOP_CONDITIONS_JSON": stop_conditions_path,
            "RESPONSE_CONTRACT_MD": response_contract_path,
            "EVIDENCE_POLICY_MD": evidence_policy_path,
            "COMMUNICATION_CONTRACT_MD": communication_contract_md_path,
            "COMMUNICATION_CONTRACT_JSON": communication_contract_json_path,
            "BOOTSTRAP_EXECUTION_DIRECTIVE_MD": bootstrap_directive_md_path,
            "BOOTSTRAP_EXECUTION_DIRECTIVE_JSON": bootstrap_directive_json_path,
            "LANGUAGE_EXECUTION_CONTRACT_MD": language_execution_contract_md_path,
            "LANGUAGE_EXECUTION_CONTRACT_JSON": language_execution_contract_json_path,
            "ROLE_SETTINGS_ACK_PROTOCOL_MD": role_settings_ack_protocol_md_path,
            "ROLE_SETTINGS_ACK_PROTOCOL_JSON": role_settings_ack_protocol_json_path,
            "RECEIPT": receipt,
        }
    )
    return 0


def parse_task_pack_from_md(md_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("| REQ-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        req_id, requirement, acceptance = cells[0], cells[1], cells[2]
        rows.append(
            {
                "requirement_id": req_id,
                "source": "task_pack_md",
                "requirement": requirement,
                "acceptance": acceptance,
                "evidence_required": [],
                "status": "PENDING",
                "evidence_paths": [],
                "notes": "",
            }
        )
    return rows


def load_requirements_from_task_pack(task_pack_path: Path) -> tuple[str, list[dict[str, Any]]]:
    suffix = task_pack_path.suffix.lower()
    if suffix == ".zip":
        with zipfile.ZipFile(task_pack_path, "r") as archive:
            if "REQUIREMENTS/requirement_matrix_seed.json" in archive.namelist():
                payload = json.loads(archive.read("REQUIREMENTS/requirement_matrix_seed.json").decode("utf-8"))
                return payload.get("task_id", TASK_ID_DEFAULT), payload.get("requirements", [])
            if "task_pack.json" in archive.namelist():
                payload = json.loads(archive.read("task_pack.json").decode("utf-8"))
                return payload.get("task_id", TASK_ID_DEFAULT), []
            raise FileNotFoundError("No supported requirement seed found inside zip.")
    if suffix == ".json":
        payload = read_json(task_pack_path)
        if "requirements" in payload and isinstance(payload["requirements"], list):
            return payload.get("task_id", TASK_ID_DEFAULT), payload["requirements"]
        return payload.get("task_id", TASK_ID_DEFAULT), []
    if suffix == ".md":
        md_text = read_text(task_pack_path)
        task_id_match = re.search(r"TASK-[A-Z0-9\\-_]+", md_text)
        task_id = task_id_match.group(0) if task_id_match else TASK_ID_DEFAULT
        return task_id, parse_task_pack_from_md(md_text)
    raise ValueError("Unsupported task-pack extension. Use zip/json/md.")


def requirement_matrix_markdown(requirements: list[dict[str, Any]]) -> str:
    lines = ["# Requirement Matrix", "", "| REQ-ID | Requirement | Status | Evidence | Notes |", "|---|---|---|---|---|"]
    for req in requirements:
        req_id = str(req.get("requirement_id", "UNKNOWN"))
        requirement = str(req.get("requirement", "")).replace("|", "/")
        status = str(req.get("status", "PENDING"))
        evidence_paths = req.get("evidence_paths", [])
        evidence = "; ".join(str(item) for item in evidence_paths) if evidence_paths else "-"
        notes = str(req.get("notes", "")).replace("|", "/")
        lines.append(f"| {req_id} | {requirement} | {status} | {evidence} | {notes} |")
    lines.append("")
    return "\n".join(lines)


def cmd_requirements_compile(args: argparse.Namespace) -> int:
    task_pack_path = Path(args.task_pack).resolve()
    if not task_pack_path.exists():
        print(f"Task-pack not found: {task_pack_path}", file=sys.stderr)
        return 2
    ctx = create_context("requirements_compile")
    try:
        task_id, requirements = load_requirements_from_task_pack(task_pack_path)
    except Exception as error:
        print(f"Failed to parse task-pack: {error}", file=sys.stderr)
        return 2

    matrix = {"task_id": task_id, "source_task_pack": str(task_pack_path), "generated_at_utc": utc_now(), "requirements": requirements}
    out_dir = ctx.run_root / "requirements_compile"
    json_path = out_dir / "requirement_matrix.json"
    md_path = out_dir / "REQUIREMENT_MATRIX.md"
    write_json(json_path, matrix)
    write_text(md_path, requirement_matrix_markdown(requirements))

    receipt = emit_receipt(
        ctx,
        "requirements_compile_receipt.json",
        {
            "command": "requirements-compile",
            "task_pack": str(task_pack_path),
            "timestamp_utc": utc_now(),
            "verdict": "PASS",
            "requirements_count": len(requirements),
            "outputs": [str(json_path), str(md_path)],
        },
    )
    print_artifacts({"REQUIREMENT_MATRIX_JSON": json_path, "REQUIREMENT_MATRIX_MD": md_path, "RECEIPT": receipt})
    return 0


def build_pack_manifest(files: list[Path], base_dir: Path, agent: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for file_path in files:
        rel = file_path.relative_to(base_dir).as_posix()
        records.append({"path": rel, "size_bytes": file_path.stat().st_size, "sha256": sha256_file(file_path)})
    return {"manifest_version": "OFFICIO_ROLE_PACK_MANIFEST_V0_1", "agent": agent, "created_at_utc": utc_now(), "files": records}


def create_sha256s_txt(files: list[Path], base_dir: Path) -> str:
    lines: list[str] = []
    for file_path in sorted(files, key=lambda item: item.name):
        rel = file_path.relative_to(base_dir).as_posix()
        lines.append(f"{sha256_file(file_path)}  {rel}")
    return "\n".join(lines) + "\n"


def role_family_from_profile(agent: str, role_profile: dict[str, Any]) -> str:
    family = role_profile.get("role_family") or role_profile.get("family")
    if family:
        return str(family).strip().upper()
    if agent.startswith("LOGOS"):
        return "LOGOS"
    if agent.startswith("SERVITOR"):
        return "SERVITOR"
    return agent.split("_")[0]


def role_source_folder(agent: str) -> Path:
    canonical = valid_agent(agent)
    return ROLE_REGISTRY / canonical


def optional_json(path: Path) -> Any:
    if path.exists():
        return read_json(path)
    return None


def optional_text(path: Path) -> str:
    if path.exists():
        return read_text(path)
    return ""


def cmd_pack_build_role(args: argparse.Namespace) -> int:
    try:
        agent = valid_agent(args.agent)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    role_profile = load_role_profile(agent)
    mode = str(role_profile.get("default_mode", "EXECUTOR"))
    _settings, settings_md = build_execution_settings(agent, mode)
    ctx = create_context("pack_build_role")

    pack_root = ctx.run_root / "role_pack_work" / agent
    pack_root.mkdir(parents=True, exist_ok=True)

    role_pack_md = pack_root / "ROLE_PACK.md"
    role_pack_json = pack_root / "role_pack.json"
    response_contract = pack_root / "RESPONSE_CONTRACT.md"
    execution_settings = pack_root / "EXECUTION_SETTINGS.md"
    stop_conditions = pack_root / "STOP_CONDITIONS.json"
    evidence_policy = pack_root / "EVIDENCE_POLICY.md"
    communication_contract_md = pack_root / "COMMUNICATION_CONTRACT.md"
    communication_contract_json = pack_root / "communication_contract.json"
    bootstrap_directive_md = pack_root / "OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE.md"
    bootstrap_directive_json = pack_root / "officio_bootstrap_execution_directive.json"
    language_execution_contract_md = pack_root / "LANGUAGE_EXECUTION_CONTRACT.md"
    language_execution_contract_json = pack_root / "language_execution_contract.json"
    role_settings_ack_protocol_md = pack_root / "ROLE_SETTINGS_ACK_PROTOCOL.md"
    role_settings_ack_protocol_json = pack_root / "ROLE_SETTINGS_ACK_PROTOCOL.json"
    start_message = pack_root / "START_MESSAGE.txt"
    manifest = pack_root / "MANIFEST.json"
    sha256s = pack_root / "SHA256SUMS.txt"

    src_dir = role_source_folder(agent)
    family = role_family_from_profile(agent, role_profile)
    family_dir = ROLE_REGISTRY / family
    role_profile_md_source = optional_text(src_dir / "ROLE_PROFILE.md")
    family_profile_md_source = optional_text(family_dir / "FAMILY_PROFILE.md")
    family_profile_json_source = optional_json(family_dir / "family_profile.json")
    read_order_source = optional_json(src_dir / "read_order.json")
    response_ref_source = optional_json(src_dir / "response_contract_ref.json")
    communication_contract_md_source = optional_text(COMMUNICATION_CONTRACT_MD)
    communication_contract_json_source = optional_json(COMMUNICATION_CONTRACT_JSON)
    bootstrap_directive_md_source = optional_text(BOOTSTRAP_EXECUTION_DIRECTIVE_MD)
    bootstrap_directive_json_source = optional_json(BOOTSTRAP_EXECUTION_DIRECTIVE_JSON)
    language_execution_contract_md_source = optional_text(LANGUAGE_EXECUTION_CONTRACT_MD)
    language_execution_contract_json_source = optional_json(LANGUAGE_EXECUTION_CONTRACT_JSON)
    role_settings_ack_protocol_md_source = optional_text(ROLE_SETTINGS_ACK_PROTOCOL_MD)
    role_settings_ack_protocol_json_source = optional_json(ROLE_SETTINGS_ACK_PROTOCOL_JSON)

    role_profile_source_md = pack_root / "ROLE_PROFILE_SOURCE.md"
    family_profile_source_md = pack_root / "FAMILY_PROFILE_SOURCE.md"
    read_order_json = pack_root / "READ_ORDER.json"
    response_contract_ref_json = pack_root / "RESPONSE_CONTRACT_REF.json"
    family_profile_json = pack_root / "family_profile.json"

    write_text(role_profile_source_md, role_profile_md_source or f"# Missing ROLE_PROFILE.md for {agent}\n")
    write_text(family_profile_source_md, family_profile_md_source or f"# Missing FAMILY_PROFILE.md for {family}\n")
    write_json(read_order_json, read_order_source if read_order_source is not None else {"warning": "missing read_order.json"})
    write_json(response_contract_ref_json, response_ref_source if response_ref_source is not None else {"warning": "missing response_contract_ref.json"})
    write_json(family_profile_json, family_profile_json_source if family_profile_json_source is not None else {"warning": "missing family_profile.json"})

    write_text(
        role_pack_md,
        "\n".join(
            [
                f"# Role Pack: {agent}",
                "",
                f"- generated_at_utc: {utc_now()}",
                f"- role_family: {family}",
                f"- default_mode: {mode}",
                f"- status: {STATUS_READY}",
                "",
                "## Family Profile",
                family_profile_md_source or "MISSING FAMILY_PROFILE.md",
                "",
                "## Role Profile",
                role_profile_md_source or "MISSING ROLE_PROFILE.md",
                "",
                "## Execution Settings",
                settings_md,
                "",
                "## Communication Contract",
                communication_contract_md_source or "MISSING SERVITOR_COMMUNICATION_CONTRACT.md",
                "",
                "## Officio Bootstrap Execution Directive",
                bootstrap_directive_md_source or "MISSING OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE.md",
                "",
                "## Language Execution Contract",
                language_execution_contract_md_source or "MISSING LANGUAGE_EXECUTION_CONTRACT.md",
                "",
                "## Role Settings ACK Protocol",
                role_settings_ack_protocol_md_source or "MISSING ROLE_SETTINGS_ACK_PROTOCOL.md",
            ]
        )
        + "\n",
    )
    write_json(
        role_pack_json,
        {
            "agent": agent,
            "role_family": family,
            "role_profile": role_profile,
            "family_profile": family_profile_json_source,
            "read_order": read_order_source,
            "response_contract_ref": response_ref_source,
            "communication_contract": communication_contract_json_source,
            "bootstrap_execution_directive": bootstrap_directive_json_source,
            "language_execution_contract": language_execution_contract_json_source,
            "role_settings_ack_protocol": role_settings_ack_protocol_json_source,
            "default_mode": mode,
            "status": STATUS_READY,
            "generated_at_utc": utc_now(),
        },
    )
    write_text(response_contract, read_text(response_contract_path_for(agent)))
    write_text(execution_settings, settings_md + "\n")
    write_json(stop_conditions, load_stop_conditions())
    write_text(evidence_policy, read_text(EVIDENCE_POLICY_DIR / "EVIDENCE_POLICY.md"))
    write_text(communication_contract_md, communication_contract_md_source or "# Missing communication contract\n")
    write_json(
        communication_contract_json,
        communication_contract_json_source if communication_contract_json_source is not None else {"warning": "missing communication contract json"},
    )
    write_text(bootstrap_directive_md, bootstrap_directive_md_source or "# Missing bootstrap execution directive\n")
    write_json(
        bootstrap_directive_json,
        bootstrap_directive_json_source if bootstrap_directive_json_source is not None else {"warning": "missing bootstrap execution directive json"},
    )
    write_text(language_execution_contract_md, language_execution_contract_md_source or "# Missing language execution contract\n")
    write_json(
        language_execution_contract_json,
        language_execution_contract_json_source if language_execution_contract_json_source is not None else {"warning": "missing language execution contract json"},
    )
    write_text(role_settings_ack_protocol_md, role_settings_ack_protocol_md_source or "# Missing role settings ACK protocol\n")
    write_json(
        role_settings_ack_protocol_json,
        role_settings_ack_protocol_json_source if role_settings_ack_protocol_json_source is not None else {"warning": "missing role settings ACK protocol json"},
    )
    write_text(
        start_message,
        (
            f"You are entering role: {agent}. Read ROLE_PACK.md, ROLE_PROFILE_SOURCE.md, READ_ORDER.json, "
            "RESPONSE_CONTRACT.md, EXECUTION_SETTINGS.md, COMMUNICATION_CONTRACT.md, "
            "OFFICIO_BOOTSTRAP_EXECUTION_DIRECTIVE.md, LANGUAGE_EXECUTION_CONTRACT.md, "
            "ROLE_SETTINGS_ACK_PROTOCOL.md.\n"
        ),
    )

    pre_manifest_files = [
        role_pack_md,
        role_pack_json,
        role_profile_source_md,
        family_profile_source_md,
        family_profile_json,
        read_order_json,
        response_contract_ref_json,
        response_contract,
        execution_settings,
        stop_conditions,
        evidence_policy,
        communication_contract_md,
        communication_contract_json,
        bootstrap_directive_md,
        bootstrap_directive_json,
        language_execution_contract_md,
        language_execution_contract_json,
        role_settings_ack_protocol_md,
        role_settings_ack_protocol_json,
        start_message,
    ]
    write_json(manifest, build_pack_manifest(pre_manifest_files, pack_root, agent))
    all_files = pre_manifest_files + [manifest]
    write_text(sha256s, create_sha256s_txt(all_files, pack_root))

    zip_dir = ctx.run_root / "role_packs"
    zip_dir.mkdir(parents=True, exist_ok=True)
    zip_path = zip_dir / f"{agent}_ROLE_PACK.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in all_files + [sha256s]:
            archive.write(file_path, file_path.relative_to(pack_root).as_posix())

    receipt = emit_receipt(
        ctx,
        f"pack_build_role_{agent}_receipt.json",
        {"command": "pack-build-role", "agent": agent, "mode": mode, "timestamp_utc": utc_now(), "verdict": "PASS", "zip_path": str(zip_path), "outputs": [str(zip_path)]},
    )
    print_artifacts({"ROLE_PACK_ZIP": zip_path, "MANIFEST_JSON": manifest, "SHA256SUMS_TXT": sha256s, "RECEIPT": receipt})
    return 0


def resolve_matrix_from_input(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as archive:
            if "requirement_matrix.json" in archive.namelist():
                return json.loads(archive.read("requirement_matrix.json").decode("utf-8"))
            raise ValueError("Zip does not contain requirement_matrix.json")
    if path.suffix.lower() == ".json":
        return read_json(path)
    raise ValueError("Unsupported compliance input. Use json or zip.")


def cmd_compliance_check(args: argparse.Namespace) -> int:
    matrix_input = args.matrix if args.matrix else args.input
    if not matrix_input:
        print("Provide --matrix or --input", file=sys.stderr)
        return 2

    matrix_path = Path(matrix_input).resolve()
    try:
        payload = resolve_matrix_from_input(matrix_path)
    except Exception as error:
        print(f"Compliance input error: {error}", file=sys.stderr)
        return 2

    requirements = payload.get("requirements", []) if isinstance(payload, dict) else []
    missing_evidence: list[str] = []
    unfinished: list[str] = []
    invalid_status: list[str] = []
    allowed_statuses = {"PENDING", "DONE", "BLOCKED", "NOT_DONE"}
    for req in requirements:
        req_id = str(req.get("requirement_id", "UNKNOWN"))
        status = str(req.get("status", "PENDING"))
        evidence_paths = req.get("evidence_paths", [])
        if status not in allowed_statuses:
            invalid_status.append(req_id)
        if status != "DONE":
            unfinished.append(req_id)
        if status == "DONE" and not evidence_paths:
            missing_evidence.append(req_id)

    verdict = "PASS"
    if invalid_status:
        verdict = "FAIL"
    elif missing_evidence or unfinished:
        verdict = "WARN"

    ctx = create_context("compliance_check")
    out_dir = ctx.run_root / "compliance_check"
    summary_json = out_dir / "compliance_check.json"
    summary_md = out_dir / "COMPLIANCE_CHECK.md"
    write_json(
        summary_json,
        {
            "matrix_input": str(matrix_path),
            "checked_at_utc": utc_now(),
            "requirements_total": len(requirements),
            "unfinished_requirements": unfinished,
            "done_without_evidence": missing_evidence,
            "invalid_status_requirements": invalid_status,
            "verdict": verdict,
        },
    )
    write_text(summary_md, f"# Compliance Check\n\n- verdict: `{verdict}`\n")

    receipt = emit_receipt(
        ctx,
        "compliance_check_receipt.json",
        {"command": "compliance-check", "matrix": str(matrix_path), "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(summary_json), str(summary_md)]},
    )
    print_artifacts({"COMPLIANCE_JSON": summary_json, "COMPLIANCE_MD": summary_md, "RECEIPT": receipt})
    return 0 if verdict in {"PASS", "WARN"} else 1


def cmd_setting_list(_args: argparse.Namespace) -> int:
    ctx = create_context("setting_list")
    index = load_settings_index()
    settings = index.get("settings", [])
    out_dir = ctx.run_root / "setting_list"
    out_json = out_dir / "settings_registry_index.json"
    out_md = out_dir / "SETTING_LIST.md"
    write_json(out_json, index)
    lines = ["# Settings List", "", "| setting_id | state | path |", "|---|---|---|"]
    for entry in settings:
        lines.append(f"| {entry.get('setting_id', '')} | {entry.get('state', '')} | {entry.get('path', '')} |")
    lines.append("")
    write_text(out_md, "\n".join(lines))
    receipt = emit_receipt(ctx, "setting_list_receipt.json", {"command": "setting-list", "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_json), str(out_md)]})
    print_artifacts({"SETTINGS_INDEX_JSON": out_json, "SETTING_LIST_MD": out_md, "RECEIPT": receipt})
    return 0


def cmd_setting_show(args: argparse.Namespace) -> int:
    ctx = create_context("setting_show")
    index = load_settings_index()
    target = None
    for entry in index.get("settings", []):
        if str(entry.get("setting_id", "")) == args.setting_id:
            target = entry
            break
    if target is None:
        print(f"Unknown setting_id: {args.setting_id}", file=sys.stderr)
        return 1

    setting_path = ROOT / str(target.get("path", ""))
    if not setting_path.exists():
        print(f"Indexed setting file missing: {setting_path}", file=sys.stderr)
        return 1

    setting_json = read_json(setting_path)
    out_dir = ctx.run_root / "setting_show" / args.setting_id
    out_json = out_dir / "setting.json"
    out_md = out_dir / "SETTING_SHOW.md"
    write_json(out_json, setting_json)
    write_text(out_md, f"# Setting: {args.setting_id}\n\n- path: `{setting_path}`\n- state: `{setting_json.get('state', 'UNKNOWN')}`\n")
    receipt = emit_receipt(ctx, "setting_show_receipt.json", {"command": "setting-show", "setting_id": args.setting_id, "timestamp_utc": utc_now(), "verdict": "PASS", "outputs": [str(out_json), str(out_md)]})
    print_artifacts({"SETTING_JSON": out_json, "SETTING_MD": out_md, "RECEIPT": receipt})
    return 0


def validate_officio_setting(payload: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for field in OFFICIO_SETTING_REQUIRED_FIELDS:
        if field not in payload:
            problems.append(f"missing:{field}")
    state = str(payload.get("state", ""))
    if state and state not in {"DRAFT", "REVIEW", "ACTIVE", "DEPRECATED", "TOMBSTONE"}:
        problems.append(f"invalid_state:{state}")
    return problems


def cmd_setting_validate(_args: argparse.Namespace) -> int:
    ctx = create_context("setting_validate")
    index = load_settings_index()
    entries = index.get("settings", [])
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for entry in entries:
        sid = str(entry.get("setting_id", "UNKNOWN"))
        setting_path = ROOT / str(entry.get("path", ""))
        if not setting_path.exists():
            errors.append(f"{sid}:missing_file")
            continue
        try:
            payload = read_json(setting_path)
        except Exception as error:
            errors.append(f"{sid}:invalid_json:{error}")
            continue
        problems = validate_officio_setting(payload)
        results.append({"setting_id": sid, "path": str(setting_path), "problems": problems})
        errors.extend([f"{sid}:{problem}" for problem in problems])

    verdict = "PASS" if not errors else "FAIL"
    out_dir = ctx.run_root / "setting_validate"
    out_json = out_dir / "schema_validation_report.json"
    out_txt = out_dir / "setting_validate_output.txt"
    write_json(out_json, {"checked_at_utc": utc_now(), "verdict": verdict, "checked_settings": len(entries), "errors": errors, "results": results})
    write_text(out_txt, f"verdict={verdict}\nchecked_settings={len(entries)}\nerror_count={len(errors)}\n")
    receipt = emit_receipt(ctx, "setting_validate_receipt.json", {"command": "setting-validate", "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"SCHEMA_VALIDATION_REPORT": out_json, "SETTING_VALIDATE_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def cmd_prompt_pack_validate(args: argparse.Namespace) -> int:
    ctx = create_context("prompt_pack_validate")
    zip_path = Path(args.zip_path).resolve()
    if not zip_path.exists() or zip_path.suffix.lower() != ".zip":
        print(f"Invalid zip path: {zip_path}", file=sys.stderr)
        return 2
    policy = read_json(SETTINGS_REGISTRY / "prompt_intake" / "prompt_intake_policy.json")
    required_files = policy.get("machine_rule", {}).get("required_files", [])
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = set(archive.namelist())
    missing = [item for item in required_files if item not in names]
    verdict = "PASS" if not missing else "BLOCKED_PROMPT_PACK_INVALID"

    out_dir = ctx.run_root / "prompt_pack_validate"
    out_json = out_dir / "prompt_pack_validation.json"
    out_txt = out_dir / "prompt_pack_validation_output.txt"
    write_json(out_json, {"zip_path": str(zip_path), "missing_files": missing, "verdict": verdict, "checked_at_utc": utc_now()})
    write_text(out_txt, f"zip_path={zip_path}\nverdict={verdict}\nmissing_files={','.join(missing) if missing else '<none>'}\n")
    receipt = emit_receipt(ctx, "prompt_pack_validate_receipt.json", {"command": "prompt-pack-validate", "timestamp_utc": utc_now(), "verdict": "PASS" if verdict == "PASS" else "BLOCKED", "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"PROMPT_PACK_VALIDATION_JSON": out_json, "PROMPT_PACK_VALIDATION_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def load_task_pack_payload(task_pack_path: Path) -> dict[str, Any]:
    if task_pack_path.is_dir():
        for candidate in ("task_contract.json", "task_pack.json", "MANIFEST.json"):
            path = task_pack_path / candidate
            if path.exists():
                payload = read_json(path)
                if isinstance(payload, dict):
                    return payload
        return {}
    if task_pack_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(task_pack_path, "r") as archive:
            for candidate in ("task_pack.json", "task_contract.json", "MANIFEST.json"):
                if candidate in archive.namelist():
                    return json.loads(archive.read(candidate).decode("utf-8"))
            return {}
    if task_pack_path.suffix.lower() == ".json":
        return read_json(task_pack_path)
    if task_pack_path.suffix.lower() == ".md":
        md = read_text(task_pack_path)
        task_id_match = re.search(r"TASK-[A-Z0-9\\-_]+", md)
        return {"task_id": task_id_match.group(0) if task_id_match else "UNKNOWN", "raw_md": md}
    return {}


def _list_of_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_scope_values(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    values.extend(_list_of_strings(payload.get("allowed_scope")))
    scope = payload.get("scope")
    if isinstance(scope, dict):
        values.extend(_list_of_strings(scope.get("allowed_paths")))
        values.extend(_list_of_strings(scope.get("paths")))
    dedup: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item not in seen:
            seen.add(item)
            dedup.append(item)
    return dedup


def normalize_forbidden_scope_values(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    values.extend(_list_of_strings(payload.get("forbidden_scope")))
    values.extend(_list_of_strings(payload.get("forbidden_scope_markers")))
    scope = payload.get("scope")
    if isinstance(scope, dict):
        values.extend(_list_of_strings(scope.get("forbidden_paths")))
        values.extend(_list_of_strings(scope.get("forbidden_scope")))
    dedup: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item not in seen:
            seen.add(item)
            dedup.append(item)
    return dedup


def normalize_expected_heads(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("expected_base_head", "expected_head", "baseline_head", "base_head"):
        values.extend(_list_of_strings(payload.get(key)))
    repo_obj = payload.get("repo")
    if isinstance(repo_obj, dict):
        for key in ("expected_base_head", "expected_head", "baseline_head", "base_head", "head"):
            values.extend(_list_of_strings(repo_obj.get(key)))
    dedup: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item not in seen:
            seen.add(item)
            dedup.append(item)
    return dedup


def normalize_required_outputs(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    values.extend(_list_of_strings(payload.get("required_outputs")))
    values.extend(_list_of_strings(payload.get("required_reports")))
    values.extend(_list_of_strings(payload.get("expected_receipts")))
    outputs = payload.get("outputs")
    if isinstance(outputs, dict):
        values.extend(_list_of_strings(outputs.get("required")))
    dedup: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item not in seen:
            seen.add(item)
            dedup.append(item)
    return dedup


def normalize_commit_push_default(payload: dict[str, Any]) -> bool | None:
    value = payload.get("commit_push_default")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        token = value.strip().lower()
        if token in {"true", "1", "yes"}:
            return True
        if token in {"false", "0", "no"}:
            return False

    commit_cfg = payload.get("commit_push")
    if isinstance(commit_cfg, dict):
        nested = commit_cfg.get("default")
        if isinstance(nested, bool):
            return nested
        if isinstance(nested, str):
            token = nested.strip().lower()
            if token in {"true", "1", "yes"}:
                return True
            if token in {"false", "0", "no"}:
                return False
    return None


def infer_required_reports(payload: dict[str, Any]) -> list[str]:
    return normalize_required_outputs(payload)


def has_required_task_field(field: str, payload: dict[str, Any], task_pack_path: Path) -> bool:
    if field in payload:
        return True
    if field == "expected_base_head":
        return len(normalize_expected_heads(payload)) > 0
    if field == "expected_head":
        return len(normalize_expected_heads(payload)) > 0
    if field == "allowed_scope":
        return len(normalize_scope_values(payload)) > 0
    if field == "forbidden_scope":
        return len(normalize_forbidden_scope_values(payload)) > 0
    if field == "required_outputs":
        return len(normalize_required_outputs(payload)) > 0
    if field == "commit_push_default":
        return normalize_commit_push_default(payload) is not None
    if field == "requirements_file":
        if isinstance(payload.get("requirements"), list):
            return True
        if infer_required_reports(payload):
            return True
        if task_pack_path.is_dir():
            for candidate in ("WARN_DEBT_TARGETS.json", "WARN_DEBT_TARGETS.md", "ACCEPTANCE_MATRIX.md"):
                if (task_pack_path / candidate).exists():
                    return True
        return False
    if field == "evidence_policy_file":
        if infer_required_reports(payload):
            return True
        if task_pack_path.is_dir():
            if (task_pack_path / "ACCEPTANCE_MATRIX.md").exists():
                return True
        return False
    if field == "schema_version":
        return str(payload.get("schema_version", "")).strip() != ""
    return False


def cmd_task_acceptance_check(args: argparse.Namespace) -> int:
    ctx = create_context("task_acceptance_check")
    task_pack_path = Path(args.task_pack).resolve()
    if not task_pack_path.exists():
        print(f"Task pack not found: {task_pack_path}", file=sys.stderr)
        return 2

    payload = load_task_pack_payload(task_pack_path)
    policy = read_json(SETTINGS_REGISTRY / "task_acceptance" / "task_acceptance_policy.json")
    required_fields = policy.get("machine_rule", {}).get("required_task_fields", [])
    missing_fields = [field for field in required_fields if not has_required_task_field(str(field), payload, task_pack_path)]
    schema_value = str(payload.get("schema_version", "")).strip()
    supported_schema_versions = {"IMPERIUM_TASK_CONTRACT_V0_2", "IMPERIUM_TASK_CONTRACT_V0_1"}
    schema_supported = (not schema_value) or (schema_value in supported_schema_versions)
    expected_heads = normalize_expected_heads(payload)
    allowed_scope = normalize_scope_values(payload)
    forbidden_scope = normalize_forbidden_scope_values(payload)
    required_outputs = normalize_required_outputs(payload)
    commit_push_default = normalize_commit_push_default(payload)

    decision = "ACCEPT"
    reasons: list[str] = []
    if missing_fields:
        decision = "CLARIFICATION_REQUIRED"
        reasons.append("missing required fields: " + ", ".join(missing_fields))

    if decision == "ACCEPT" and not schema_supported:
        decision = "ACCEPT_WITH_WARNINGS"
        reasons.append(f"unsupported schema_version: {schema_value}")

    if decision in {"ACCEPT", "ACCEPT_WITH_WARNINGS"} and not expected_heads:
        decision = "CLARIFICATION_REQUIRED"
        reasons.append("missing expected head fields")

    if decision in {"ACCEPT", "ACCEPT_WITH_WARNINGS"}:
        forbidden_markers = payload.get("forbidden_scope_markers", ["THRONE", "CUSTODES"])
        marker_values = [str(marker).upper() for marker in forbidden_markers] if isinstance(forbidden_markers, list) else ["THRONE", "CUSTODES"]
        for scope in allowed_scope:
            upper_scope = scope.upper()
            if any(marker in upper_scope for marker in marker_values):
                decision = "BLOCKED_OUT_OF_SCOPE"
                reasons.append(f"forbidden scope marker in allowed_scope: {scope}")
                break

    text_blob = json.dumps(payload, ensure_ascii=False).lower()
    if decision in {"ACCEPT", "ACCEPT_WITH_WARNINGS"} and any(k in text_blob for k in ["rm -rf", "wipe all", "delete all", "format disk"]):
        decision = "BLOCKED_UNSAFE"
        reasons.append("unsafe keyword detected")

    if decision in {"ACCEPT", "ACCEPT_WITH_WARNINGS"} and isinstance(payload.get("requirements"), list) and len(payload["requirements"]) > 80:
        decision = "SPLIT_REQUIRED"
        reasons.append("too many requirements for a single bounded execution")

    if decision == "ACCEPT" and commit_push_default is None:
        decision = "ACCEPT_WITH_WARNINGS"
        reasons.append("commit_push_default unresolved")

    if decision == "ACCEPT" and not required_outputs:
        decision = "ACCEPT_WITH_WARNINGS"
        reasons.append("required_outputs unresolved")

    if decision == "ACCEPT" and not has_required_task_field("evidence_policy_file", payload, task_pack_path):
        decision = "ACCEPT_WITH_WARNINGS"
        reasons.append("explicit evidence_policy_file not found")

    out_dir = ctx.run_root / "task_acceptance_check"
    out_json = out_dir / "task_acceptance_check.json"
    out_txt = out_dir / "task_acceptance_check_output.txt"
    write_json(
        out_json,
        {
            "task_pack_path": str(task_pack_path),
            "checked_at_utc": utc_now(),
            "decision": decision,
            "reasons": reasons,
            "missing_fields": missing_fields,
            "contract_field_support": {
                "schema_version": schema_value,
                "schema_supported": schema_supported,
                "expected_heads": expected_heads,
                "allowed_scope_count": len(allowed_scope),
                "forbidden_scope_count": len(forbidden_scope),
                "required_outputs_count": len(required_outputs),
                "commit_push_default": commit_push_default,
                "supports_modern_fields": {
                    "expected_base_head": has_required_task_field("expected_base_head", payload, task_pack_path),
                    "expected_head": has_required_task_field("expected_head", payload, task_pack_path),
                    "allowed_scope": has_required_task_field("allowed_scope", payload, task_pack_path),
                    "forbidden_scope": has_required_task_field("forbidden_scope", payload, task_pack_path),
                    "required_outputs": has_required_task_field("required_outputs", payload, task_pack_path),
                    "commit_push_default": has_required_task_field("commit_push_default", payload, task_pack_path),
                },
            },
        },
    )
    write_text(out_txt, f"task_pack_path={task_pack_path}\ndecision={decision}\nreasons={'; '.join(reasons) if reasons else '<none>'}\n")
    receipt = emit_receipt(ctx, "task_acceptance_check_receipt.json", {"command": "task-acceptance-check", "timestamp_utc": utc_now(), "verdict": "PASS", "decision": decision, "outputs": [str(out_json), str(out_txt)]})
    print_artifacts({"TASK_ACCEPTANCE_JSON": out_json, "TASK_ACCEPTANCE_OUTPUT": out_txt, "RECEIPT": receipt})
    return 0


def cmd_tools(_args: argparse.Namespace) -> int:
    ctx = create_context("tools")
    out_dir = ctx.run_root / "tools"
    out_json = out_dir / "officio_tools_report.json"
    index_path = default_tool_index_path(REPO_ROOT)
    payload = build_organ_tool_view(organ_id="OFFICIO_AGENTIS_AGENT", index_path=index_path)
    payload["task_id"] = TASK_ID_DEFAULT
    payload["checked_at_utc"] = utc_now()
    write_json(out_json, payload)
    verdict = str(payload.get("verdict", "PASS"))
    receipt = emit_receipt(
        ctx,
        "tools_receipt.json",
        {
            "command": "tools",
            "timestamp_utc": utc_now(),
            "verdict": verdict,
            "outputs": [str(out_json)],
            "registry_source": str(index_path),
        },
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print_artifacts({"TOOLS_REPORT": out_json, "RECEIPT": receipt})
    return 0 if verdict in {"PASS", "WARN"} else 1


def cmd_recent(args: argparse.Namespace) -> int:
    runtime_root = get_runtime_root()
    runs = [p for p in runtime_root.iterdir() if p.is_dir() and p.name.startswith("run_")]
    for item in sorted(runs, key=lambda i: i.name, reverse=True)[: max(1, int(args.limit))]:
        print(item)
    return 0


def language_contract_checks() -> tuple[list[str], list[str], dict[str, Any]]:
    warnings: list[str] = []
    errors: list[str] = []
    details: dict[str, Any] = {
        "communication_contract_json": str(COMMUNICATION_CONTRACT_JSON),
        "bootstrap_directive_json": str(BOOTSTRAP_EXECUTION_DIRECTIVE_JSON),
        "language_execution_contract_json": str(LANGUAGE_EXECUTION_CONTRACT_JSON),
        "role_settings_ack_protocol_json": str(ROLE_SETTINGS_ACK_PROTOCOL_JSON),
        "response_contract_md": str(RESPONSE_CONTRACTS / "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md"),
        "required_violation_codes": [
            "WARN_RESPONSE_LANGUAGE_CONTRACT",
            "FAIL_RESPONSE_CONTRACT",
            "BLOCKED_OFFICIO_ACK_MISSING",
            "BLOCKED_ROLE_PACK_AUTHORITY_MISSING",
            "WARN_TASKPACK_ONLY_WORKAROUND_DETECTED",
        ],
    }

    try:
        comm = read_json(COMMUNICATION_CONTRACT_JSON)
    except Exception as error:
        errors.append(f"communication_contract_json_unreadable:{error}")
        return warnings, errors, details
    try:
        directive = read_json(BOOTSTRAP_EXECUTION_DIRECTIVE_JSON)
    except Exception as error:
        errors.append(f"bootstrap_directive_json_unreadable:{error}")
        return warnings, errors, details
    try:
        language_contract = read_json(LANGUAGE_EXECUTION_CONTRACT_JSON)
    except Exception as error:
        errors.append(f"language_execution_contract_json_unreadable:{error}")
        return warnings, errors, details
    try:
        ack_protocol = read_json(ROLE_SETTINGS_ACK_PROTOCOL_JSON)
    except Exception as error:
        errors.append(f"role_settings_ack_protocol_json_unreadable:{error}")
        return warnings, errors, details

    comm_rule = comm.get("machine_rule", {}) if isinstance(comm, dict) else {}
    directive_rule = directive.get("machine_rule", {}) if isinstance(directive, dict) else {}
    language_rule = language_contract.get("machine_rule", {}) if isinstance(language_contract, dict) else {}
    ack_rule = ack_protocol.get("machine_rule", {}) if isinstance(ack_protocol, dict) else {}
    surface_rules = language_rule.get("surface_language_rules", {}) if isinstance(language_rule.get("surface_language_rules", {}), dict) else {}
    details["communication_machine_rule"] = comm_rule
    details["bootstrap_machine_rule"] = directive_rule
    details["language_execution_machine_rule"] = language_rule
    details["ack_protocol_machine_rule"] = ack_rule

    def collect_codes(rule: dict[str, Any]) -> set[str]:
        collected: set[str] = set()
        for key in ("violation_codes", "language_violation_codes", "authority_violation_codes", "required_violation_codes"):
            value = rule.get(key, [])
            if isinstance(value, list):
                for entry in value:
                    collected.add(str(entry))
        return collected

    required_codes = set(details["required_violation_codes"])
    all_codes = collect_codes(comm_rule) | collect_codes(directive_rule) | collect_codes(language_rule) | collect_codes(ack_rule)
    missing_codes = sorted(list(required_codes - all_codes))
    if missing_codes:
        errors.append("missing_violation_codes:" + ",".join(missing_codes))

    if str(comm_rule.get("owner_live_commentary_language_after_officio_ack", "")).lower() != "russian":
        errors.append("missing_owner_live_commentary_language_rule")
    if str(comm_rule.get("owner_final_comments_language_after_officio_ack", "")).lower() != "russian":
        errors.append("missing_owner_final_comments_language_rule")
    if str(comm_rule.get("machine_artifact_language", "")).lower() != "english":
        errors.append("missing_machine_artifact_language_rule")

    if str(surface_rules.get("owner_live_commentary_after_officio_ack", "")).lower() != "russian":
        errors.append("language_execution_missing_owner_live_commentary_rule")
    if str(surface_rules.get("owner_final_comments_after_officio_ack", "")).lower() != "russian":
        errors.append("language_execution_missing_owner_final_comments_rule")
    if str(surface_rules.get("machine_artifacts", "")).lower() != "english":
        errors.append("language_execution_missing_machine_artifact_rule")

    required_ack_fields = {"language_execution_contract_ref", "role_settings_ack_protocol_ref", "violation_codes"}
    ack_settings_fields = set(str(x) for x in ack_rule.get("required_ack_settings_fields", [])) if isinstance(ack_rule.get("required_ack_settings_fields", []), list) else set()
    missing_ack_fields = sorted(list(required_ack_fields - ack_settings_fields))
    if missing_ack_fields:
        errors.append("ack_protocol_missing_required_settings_fields:" + ",".join(missing_ack_fields))

    response_contract_text = read_text(RESPONSE_CONTRACTS / "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.md")
    if "OWNER COMMENTS" not in response_contract_text:
        errors.append("response_contract_missing_owner_comments_section")
    if "Russian" not in response_contract_text and "russian" not in response_contract_text:
        errors.append("response_contract_missing_explicit_russian_requirement")
    if "FAIL_RESPONSE_CONTRACT" not in response_contract_text:
        errors.append("response_contract_missing_fail_response_contract_code")
    if "WARN_RESPONSE_LANGUAGE_CONTRACT" not in response_contract_text:
        warnings.append("response_contract_missing_warn_response_language_contract_code")

    if not bool(language_rule.get("anti_taskpack_only_workaround", False)):
        warnings.append("language_execution_contract_missing_anti_taskpack_only_workaround_flag")

    return warnings, errors, details


def cmd_check_all(_args: argparse.Namespace) -> int:
    ctx = create_context("check_all")
    required_files = [
        ROOT / "README.md",
        ROOT / "TOOLS" / "officio_agent_runner.py",
        SETTINGS_REGISTRY / "settings_index.json",
        SCHEMAS_DIR / "officio_setting.schema.json",
        SCHEMAS_DIR / "prompt_pack_contract.schema.json",
        SCHEMAS_DIR / "task_acceptance_policy.schema.json",
        ROLE_REGISTRY / "SERVITOR" / "role_profile.json",
        ROLE_REGISTRY / "SERVITOR" / "allowed_modes.json",
        ROLE_REGISTRY / "SERVITOR" / "read_order.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "role_profile.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "allowed_modes.json",
        ROLE_REGISTRY / "LOGOS_PRIME" / "read_order.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "role_profile.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "allowed_modes.json",
        ROLE_REGISTRY / "LOGOS_SPECULUM" / "read_order.json",
        EXAMPLES_DIR / "accepted_tasks" / "accepted_task_example.json",
        EXAMPLES_DIR / "rejected_tasks" / "rejected_task_out_of_scope.json",
        EXAMPLES_DIR / "valid_prompt_packs" / "valid_prompt_pack_manifest.json",
        EXAMPLES_DIR / "invalid_prompt_packs" / "missing_required_files.json",
        COMMUNICATION_CONTRACT_MD,
        COMMUNICATION_CONTRACT_JSON,
        BOOTSTRAP_EXECUTION_DIRECTIVE_MD,
        BOOTSTRAP_EXECUTION_DIRECTIVE_JSON,
        LANGUAGE_EXECUTION_CONTRACT_MD,
        LANGUAGE_EXECUTION_CONTRACT_JSON,
        ROLE_SETTINGS_ACK_PROTOCOL_MD,
        ROLE_SETTINGS_ACK_PROTOCOL_JSON,
    ]
    missing_files = [str(path) for path in required_files if not path.exists()]

    invalid_json: list[dict[str, str]] = []
    for path in ROOT.rglob("*.json"):
        try:
            read_json(path)
        except Exception as error:
            invalid_json.append({"path": str(path), "error": str(error)})

    settings_index_errors: list[str] = []
    try:
        idx = load_settings_index()
        for entry in idx.get("settings", []):
            setting_path = ROOT / str(entry.get("path", ""))
            if not setting_path.exists():
                settings_index_errors.append(f"missing_indexed_setting:{setting_path}")
            else:
                payload = read_json(setting_path)
                for field in OFFICIO_SETTING_REQUIRED_FIELDS:
                    if field not in payload:
                        settings_index_errors.append(f"missing_field:{setting_path.relative_to(ROOT)}:{field}")
    except Exception as error:
        settings_index_errors.append(f"settings_index_error:{error}")

    language_warnings, language_errors, language_details = language_contract_checks()
    verdict = "PASS" if not missing_files and not invalid_json and not settings_index_errors and not language_errors else "FAIL"
    out_dir = ctx.run_root / "check_all"
    report_json = out_dir / "check_all_report.json"
    report_txt = out_dir / "check_all_output.txt"
    write_json(
        report_json,
        {
            "checked_at_utc": utc_now(),
            "verdict": verdict,
            "missing_files": missing_files,
            "invalid_json": invalid_json,
            "settings_index_errors": settings_index_errors,
            "language_contract_warnings": language_warnings,
            "language_contract_errors": language_errors,
            "language_contract_details": language_details,
        },
    )
    write_text(
        report_txt,
        (
            f"verdict={verdict}\n"
            f"missing_files={len(missing_files)}\n"
            f"invalid_json={len(invalid_json)}\n"
            f"settings_index_errors={len(settings_index_errors)}\n"
            f"language_contract_warnings={len(language_warnings)}\n"
            f"language_contract_errors={len(language_errors)}\n"
        ),
    )
    receipt = emit_receipt(ctx, "check_all_receipt.json", {"command": "check-all", "timestamp_utc": utc_now(), "verdict": verdict, "outputs": [str(report_json), str(report_txt)]})
    print_artifacts({"CHECK_ALL_JSON": report_json, "CHECK_ALL_OUTPUT": report_txt, "RECEIPT": receipt})
    return 0 if verdict == "PASS" else 1


def load_primary_commands() -> list[str]:
    fallback = [
        "/help",
        "/status",
        "/modes",
        "/mode <name>",
        "/role <agent>",
        "/settings <agent> <mode>",
        "/settings-list",
        "/settings-show <setting_id>",
        "/validate",
        "/check",
        "/pack <agent>",
        "/prompt-check <zip_path>",
        "/task-check <task_pack_path>",
        "/tools",
        "/recent",
        "/where",
        "/exit",
    ]
    policy_path = COMMON_CLI_ROOT / "command_palette_policy.json"
    try:
        payload = read_json(policy_path)
        values = payload.get("primary_commands", [])
        if isinstance(values, list):
            commands = [str(item).strip() for item in values if str(item).strip()]
            if commands:
                return commands
    except Exception:
        pass
    return fallback


def load_shell_boundary_patterns() -> list[str]:
    fallback = [
        r"^cd\s+",
        r"^\$[A-Za-z_][A-Za-z0-9_]*\s*=",
        r"^(py|python|pwsh|powershell|cmd)(\s+|$)",
        r"^(dir|ls|git|npm|pip|where|type)(\s+|$)",
    ]
    policy_path = COMMON_CLI_ROOT / "shell_behavior_policy.json"
    try:
        payload = read_json(policy_path)
        boundary = payload.get("boundary_detection", {})
        patterns = boundary.get("os_command_patterns", []) if isinstance(boundary, dict) else []
        if isinstance(patterns, list):
            parsed = [str(item) for item in patterns if str(item).strip()]
            if parsed:
                return parsed
    except Exception:
        pass
    return fallback


def load_officio_crest() -> str:
    crest_registry = COMMON_CLI_ROOT / "HERALDRY" / "organ_crest_registry.json"
    try:
        payload = read_json(crest_registry)
        organs = payload.get("organs", [])
        if isinstance(organs, list):
            for entry in organs:
                if isinstance(entry, dict) and str(entry.get("organ_id", "")).upper() == "OFFICIO_AGENTIS":
                    crest = str(entry.get("ascii_compact", "")).strip()
                    if crest:
                        return crest
    except Exception:
        pass
    return "[=] <||> (o) {O} ->"


def count_settings() -> int:
    try:
        payload = load_settings_index()
        settings = payload.get("settings", [])
        if isinstance(settings, list):
            return len(settings)
    except Exception:
        return 0
    return 0


def count_roles() -> int:
    return sum(1 for child in ROLE_REGISTRY.iterdir() if child.is_dir())


def supports_unicode_output() -> bool:
    encoding = (sys.stdout.encoding or "").lower()
    return "utf" in encoding or "unicode" in encoding


def renderer_diagnostic(console_obj: Any) -> dict[str, Any]:
    width = shutil.get_terminal_size(fallback=(120, 40)).columns
    color_enabled = bool(HAVE_RICH and console_obj is not None and getattr(console_obj, "color_system", None) is not None)
    renderer = "rich" if HAVE_RICH and console_obj is not None else "ansi_fallback"
    return {
        "rich_installed": bool(HAVE_RICH),
        "renderer": renderer,
        "color_enabled": color_enabled,
        "terminal_width": int(width),
        "supports_unicode": supports_unicode_output(),
        "python_version": sys.version,
        "runtime_root": str(get_runtime_root()),
        "timestamp_utc": utc_now(),
    }


def color_diagnostic_payload(renderer_payload: dict[str, Any]) -> dict[str, Any]:
    theme_path = COMMON_CLI_ROOT / "color_theme_imperium.json"
    palette_name = "imperium_origin_terminal"
    try:
        payload = read_json(theme_path)
        palette_name = str(payload.get("theme_id", palette_name))
    except Exception:
        pass
    return {
        "palette_name": palette_name,
        "accent_available": bool(renderer_payload.get("color_enabled", False)),
        "warning_available": bool(renderer_payload.get("color_enabled", False)),
        "blocker_available": bool(renderer_payload.get("color_enabled", False)),
        "renderer": renderer_payload.get("renderer", "ansi_fallback"),
        "timestamp_utc": utc_now(),
    }


def is_shell_boundary_input(raw: str, patterns: list[str]) -> bool:
    stripped = raw.strip()
    if not stripped or stripped.startswith("/"):
        return False
    for pattern in patterns:
        try:
            if re.match(pattern, stripped, flags=re.IGNORECASE):
                return True
        except re.error:
            continue
    return True


def collect_artifact_paths(output_text: str) -> list[str]:
    paths: list[str] = []
    for line in output_text.splitlines():
        if ": " not in line:
            continue
        _, maybe_path = line.split(": ", 1)
        maybe_path = maybe_path.strip()
        if re.match(r"^[A-Za-z]:\\", maybe_path):
            paths.append(maybe_path)
    return paths


def render_shell_view(
    console: Any,
    latest_output: str,
    warnings: list[str],
    run_id: str,
    artifacts: list[str],
    shell_mode: str,
    active_role: str,
    primary_commands: list[str],
    crest: str,
    renderer: str,
    next_action: str,
    visual_status: str,
) -> None:
    g = git_info()
    header_lines = [
        "OFFICIO AGENTIS",
        f"mode: {shell_mode}",
        f"head: {g['head']}",
        f"dirty_state: {g['dirty']}",
        f"runtime_root: {get_runtime_root()}",
        f"role_count: {count_roles()}",
        f"setting_count: {count_settings()}",
        f"last_run_id: {run_id}",
        f"renderer: {renderer} | visual_status: {visual_status}",
        f"active_role: {active_role}",
        f"crest: {crest}",
    ]
    command_examples = [
        "/mode IMPLEMENT",
        "/role SERVITOR",
        "/settings SERVITOR EXECUTOR",
        "/tools",
        "/pack LOGOS_PRIME",
        "/where",
    ]
    right_lines = ["Primary commands:"] + primary_commands + ["", "Examples:"] + command_examples + ["", f"Next: {next_action}"]
    bottom_lines = [
        f"last_run_id: {run_id}",
        "artifacts_written: " + (", ".join(artifacts[-3:]) if artifacts else "none"),
        "latest_warning_or_blocker: " + (warnings[-1] if warnings else "none"),
        f"next_action: {next_action}",
    ]
    header_text = "\n".join(header_lines)
    right_text = "\n".join(right_lines)
    bottom_text = "\n".join(bottom_lines)
    left_text = latest_output or "No output yet."

    if HAVE_RICH and console is not None:
        layout = Layout()
        layout.split_column(Layout(name="header", size=12), Layout(name="body"), Layout(name="bottom", size=5))
        layout["body"].split_row(Layout(name="main"), Layout(name="right", size=48))
        layout["header"].update(Panel(header_text, title="TOP STATUS BAR", border_style="#3A2B52"))
        layout["main"].update(Panel(left_text, title="LEFT WORK ZONE", border_style="#2B5B84"))
        layout["right"].update(Panel(right_text, title="RIGHT COMMAND ZONE", border_style="#7D8596"))
        layout["bottom"].update(Panel(bottom_text, title="BOTTOM EVENT BAR", border_style="#3E8A5A"))
        console.clear()
        console.print(layout)
    else:
        print()
        print("TOP STATUS BAR")
        print(header_text)
        print()
        print("LEFT WORK ZONE")
        print(left_text)
        print()
        print("RIGHT COMMAND ZONE")
        print(right_text)
        print()
        print("BOTTOM EVENT BAR")
        print(bottom_text)


def cmd_shell(args: argparse.Namespace) -> int:
    ctx = create_context("shell")
    shell_dir = ctx.run_root / "shell"
    shell_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = shell_dir / "shell_transcript.txt"
    renderer_diag_path = shell_dir / "renderer_diagnostic.json"
    color_diag_path = shell_dir / "color_diagnostic.json"

    console_obj: Any = None
    if HAVE_RICH:
        console_obj = Console()  # type: ignore[misc]

    renderer_payload = renderer_diagnostic(console_obj)
    color_payload = color_diagnostic_payload(renderer_payload)
    write_json(renderer_diag_path, renderer_payload)
    write_json(color_diag_path, color_payload)

    command_lines: list[str] = []
    if args.commands_file:
        command_file = Path(args.commands_file)
        if command_file.exists():
            for raw_line in command_file.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if line:
                    command_lines.append(line)
    if args.once:
        once_value = args.once.strip()
        if once_value and not once_value.startswith("/"):
            once_value = f"/{once_value}"
        if once_value:
            command_lines.append(once_value)

    primary_commands = load_primary_commands()
    boundary_patterns = load_shell_boundary_patterns()
    crest = load_officio_crest()
    shell_mode = DEFAULT_SHELL_MODE
    active_role = "SERVITOR_PRIME"
    next_action = "/help"
    visual_status = "PASS" if bool(renderer_payload.get("color_enabled", False)) else "WARN"
    latest_output = "Use /help to list commands."
    warnings: list[str] = []
    artifacts: list[str] = [str(renderer_diag_path), str(color_diag_path)]
    transcript_rows: list[str] = [
        f"shell_run={ctx.run_root}",
        f"renderer={renderer_payload.get('renderer', 'ansi_fallback')}",
        f"visual_status={visual_status}",
    ]
    run_id = ctx.run_root.name

    def run_runner_command(raw_command: str, mapped_args: list[str], recommended: str) -> bool:
        nonlocal latest_output, next_action
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), *mapped_args], capture_output=True, text=True)
        output = (completed.stdout + "\n" + completed.stderr).strip()
        latest_output = output if output else "<no output>"
        transcript_rows.append(latest_output)
        artifacts.extend(collect_artifact_paths(completed.stdout))
        if completed.returncode != 0:
            warn_msg = f"command_failed:{raw_command}:code={completed.returncode}"
            warnings.append(warn_msg)
            next_action = "/check"
        else:
            next_action = recommended
        return True

    def execute_shell_command(raw: str) -> bool:
        nonlocal latest_output, shell_mode, active_role, next_action
        raw = raw.strip()
        if not raw:
            return True
        transcript_rows.append(f"> {raw}")
        if is_shell_boundary_input(raw, boundary_patterns):
            latest_output = BOUNDARY_MESSAGE
            transcript_rows.append(latest_output)
            next_action = "/help"
            return True
        try:
            parts = shlex.split(raw, posix=False)
        except ValueError as error:
            latest_output = f"Invalid command syntax: {error}"
            warnings.append(latest_output)
            transcript_rows.append(latest_output)
            next_action = "/help"
            return True
        if not parts:
            return True
        command = parts[0].lower()

        if command == "/help":
            latest_output = (
                "Primary commands:\n"
                + "\n".join(primary_commands)
                + "\n\nAliases:\n"
                "/role-get /settings-get /setting-list /setting-show /setting-validate "
                "/check-all /pack-build-role /prompt-pack-validate /task-acceptance-check /tools"
            )
            transcript_rows.append(latest_output)
            next_action = "/status"
            return True
        if command == "/exit":
            latest_output = "exit requested"
            transcript_rows.append(latest_output)
            return False
        if command == "/status":
            return run_runner_command(raw, ["status"], "/modes")
        if command == "/modes":
            latest_output = "Modes:\n" + "\n".join(SHELL_MODES)
            transcript_rows.append(latest_output)
            next_action = "/mode IMPLEMENT"
            return True
        if command == "/mode":
            if len(parts) != 2:
                latest_output = "Usage: /mode <ASK|ARCHITECT|IMPLEMENT|DEBUG|AUDIT|ORCHESTRATE>"
                transcript_rows.append(latest_output)
                next_action = "/modes"
                return True
            candidate = parts[1].strip().upper()
            if candidate not in SHELL_MODES:
                latest_output = f"Unsupported shell mode '{parts[1]}'."
                warnings.append(latest_output)
                transcript_rows.append(latest_output)
                next_action = "/modes"
                return True
            shell_mode = candidate
            latest_output = f"Mode changed: {shell_mode}"
            transcript_rows.append(latest_output)
            next_action = "/check"
            return True
        if command == "/where":
            latest_output = "\n".join(
                [
                    f"repo_root={REPO_ROOT}",
                    f"officio_root={ROOT}",
                    f"runner={Path(__file__).resolve()}",
                    f"runtime_root={ctx.runtime_root}",
                    f"cwd={Path.cwd()}",
                ]
            )
            transcript_rows.append(latest_output)
            next_action = "/status"
            return True
        if command == "/run":
            if len(parts) < 2:
                latest_output = "Usage: /run <command>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            if shell_mode not in RUN_ALLOWED_SHELL_MODES:
                latest_output = f"/run is blocked in mode {shell_mode}. Switch to IMPLEMENT, DEBUG, or ORCHESTRATE."
                warnings.append(latest_output)
                transcript_rows.append(latest_output)
                next_action = "/mode IMPLEMENT"
                return True
            proc = subprocess.run(" ".join(parts[1:]), shell=True, capture_output=True, text=True, cwd=REPO_ROOT)
            output = (proc.stdout + "\n" + proc.stderr).strip()
            latest_output = output if output else "<no output>"
            transcript_rows.append(latest_output)
            if proc.returncode != 0:
                warnings.append(f"run_failed:code={proc.returncode}")
                next_action = "/check"
            else:
                next_action = "/recent"
            return True

        if command in {"/role", "/role-get"}:
            if len(parts) != 2:
                latest_output = "Usage: /role <SERVITOR|SERVITOR_PRIME|SERVITOR_SPECULUM|LOGOS|LOGOS_PRIME|LOGOS_SPECULUM>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            try:
                active_role = valid_agent(parts[1])
            except ValueError as error:
                latest_output = str(error)
                warnings.append(latest_output)
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            return run_runner_command(raw, ["role-get", "--agent", active_role], f"/settings {active_role} EXECUTOR")

        if command == "/identity":
            return run_runner_command(raw, ["role-get", "--agent", active_role], f"/settings {active_role} EXECUTOR")

        if command in {"/settings", "/settings-get"}:
            if len(parts) != 3:
                latest_output = "Usage: /settings <AGENT> <EXECUTOR|AUDITOR|ARCHITECT|REPAIRER>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            try:
                agent = valid_agent(parts[1])
                mode = valid_mode(parts[2])
                active_role = agent
            except ValueError as error:
                latest_output = str(error)
                warnings.append(latest_output)
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            return run_runner_command(raw, ["settings-get", "--agent", agent, "--mode", mode], f"/pack {agent}")

        if command in {"/settings-list", "/setting-list"}:
            return run_runner_command(raw, ["setting-list"], "/settings-show response_formats")

        if command in {"/settings-show", "/setting-show"}:
            if len(parts) < 2:
                latest_output = "Usage: /settings-show <setting_id>"
                transcript_rows.append(latest_output)
                next_action = "/settings-list"
                return True
            setting_id = " ".join(parts[1:])
            return run_runner_command(raw, ["setting-show", "--setting-id", setting_id], "/validate")

        if command in {"/validate", "/setting-validate"}:
            return run_runner_command(raw, ["setting-validate"], "/check")

        if command in {"/check", "/check-all"}:
            return run_runner_command(raw, ["check-all"], "/pack LOGOS_PRIME")

        if command in {"/pack", "/pack-build-role"}:
            if len(parts) != 2:
                latest_output = "Usage: /pack <SERVITOR|SERVITOR_PRIME|SERVITOR_SPECULUM|LOGOS|LOGOS_PRIME|LOGOS_SPECULUM>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            try:
                agent = valid_agent(parts[1])
            except ValueError as error:
                latest_output = str(error)
                warnings.append(latest_output)
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            return run_runner_command(raw, ["pack-build-role", "--agent", agent], "/recent")

        if command in {"/prompt-check", "/prompt-pack-validate"}:
            if len(parts) < 2:
                latest_output = "Usage: /prompt-check <zip_path>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            zip_path = " ".join(parts[1:])
            return run_runner_command(raw, ["prompt-pack-validate", "--zip-path", zip_path], "/task-check <task_pack_path>")

        if command in {"/task-check", "/task-acceptance-check"}:
            if len(parts) < 2:
                latest_output = "Usage: /task-check <task_pack_path>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            task_pack = " ".join(parts[1:])
            return run_runner_command(raw, ["task-acceptance-check", "--task-pack", task_pack], "/recent")

        if command == "/tools":
            return run_runner_command(raw, ["tools"], "/check")

        if command == "/recent":
            return run_runner_command(raw, ["recent"], "/where")

        if command == "/compliance-check":
            if len(parts) < 2:
                latest_output = "Usage: /compliance-check <bundle_or_matrix_path>"
                transcript_rows.append(latest_output)
                next_action = "/help"
                return True
            matrix_input = " ".join(parts[1:])
            return run_runner_command(raw, ["compliance-check", "--input", matrix_input], "/recent")

        latest_output = f"Unknown command: {parts[0]}\nUse /help."
        warnings.append(latest_output)
        transcript_rows.append(latest_output)
        next_action = "/help"
        return True

    if command_lines:
        for line in command_lines:
            if not execute_shell_command(line):
                break
            render_shell_view(
                console_obj,
                latest_output,
                warnings,
                run_id,
                artifacts,
                shell_mode,
                active_role,
                primary_commands,
                crest,
                str(renderer_payload.get("renderer", "ansi_fallback")),
                next_action,
                visual_status,
            )

    interactive_enabled = (not args.non_interactive) and (not bool(args.once))
    if interactive_enabled:
        while True:
            render_shell_view(
                console_obj,
                latest_output,
                warnings,
                run_id,
                artifacts,
                shell_mode,
                active_role,
                primary_commands,
                crest,
                str(renderer_payload.get("renderer", "ansi_fallback")),
                next_action,
                visual_status,
            )
            try:
                raw = input("officio> ").strip()
            except EOFError:
                break
            if not execute_shell_command(raw):
                break

    write_text(transcript_path, "\n".join(transcript_rows) + "\n")
    verdict = "PASS" if visual_status == "PASS" else "WARN"
    receipt = emit_receipt(
        ctx,
        "shell_receipt.json",
        {
            "command": "shell",
            "timestamp_utc": utc_now(),
            "verdict": verdict,
            "visual_status": visual_status,
            "warnings": warnings,
            "outputs": [str(transcript_path), str(renderer_diag_path), str(color_diag_path)],
        },
    )
    print_artifacts(
        {
            "SHELL_TRANSCRIPT": transcript_path,
            "RENDERER_DIAGNOSTIC": renderer_diag_path,
            "COLOR_DIAGNOSTIC": color_diag_path,
            "RECEIPT": receipt,
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Officio Agent Runner V0.1+")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    role_get = sub.add_parser("role-get")
    role_get.add_argument("--agent", required=True)
    settings_get = sub.add_parser("settings-get")
    settings_get.add_argument("--agent", required=True)
    settings_get.add_argument("--mode", required=True)
    req_compile = sub.add_parser("requirements-compile")
    req_compile.add_argument("--task-pack", required=True)
    pack_build = sub.add_parser("pack-build-role")
    pack_build.add_argument("--agent", required=True)
    compliance = sub.add_parser("compliance-check")
    compliance.add_argument("--matrix", required=False, default=None)
    compliance.add_argument("--input", required=False, default=None)
    compliance.add_argument("--evidence", required=False, default=None)
    sub.add_parser("check-all")
    sub.add_parser("setting-list")
    setting_show = sub.add_parser("setting-show")
    setting_show.add_argument("--setting-id", required=True)
    sub.add_parser("setting-validate")
    prompt_validate = sub.add_parser("prompt-pack-validate")
    prompt_validate.add_argument("--zip-path", required=True)
    acceptance = sub.add_parser("task-acceptance-check")
    acceptance.add_argument("--task-pack", required=True)
    sub.add_parser("tools")
    recent = sub.add_parser("recent")
    recent.add_argument("--limit", default="20")
    shell = sub.add_parser("shell")
    shell.add_argument("--commands-file", required=False, default=None)
    shell.add_argument("--non-interactive", action="store_true")
    shell.add_argument("--once", required=False, default=None)
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "status":
        return cmd_status(args)
    if args.command == "role-get":
        return cmd_role_get(args)
    if args.command == "settings-get":
        return cmd_settings_get(args)
    if args.command == "requirements-compile":
        return cmd_requirements_compile(args)
    if args.command == "pack-build-role":
        return cmd_pack_build_role(args)
    if args.command == "compliance-check":
        return cmd_compliance_check(args)
    if args.command == "check-all":
        return cmd_check_all(args)
    if args.command == "setting-list":
        return cmd_setting_list(args)
    if args.command == "setting-show":
        return cmd_setting_show(args)
    if args.command == "setting-validate":
        return cmd_setting_validate(args)
    if args.command == "prompt-pack-validate":
        return cmd_prompt_pack_validate(args)
    if args.command == "task-acceptance-check":
        return cmd_task_acceptance_check(args)
    if args.command == "tools":
        return cmd_tools(args)
    if args.command == "recent":
        return cmd_recent(args)
    if args.command == "shell":
        return cmd_shell(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
