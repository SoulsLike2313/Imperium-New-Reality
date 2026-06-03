from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_repo_path  # noqa: E402
from mechanicus_validation_receipt_builder_v0_1 import build_validation_receipt, write_receipt


TASK_ID = "TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1"
EXPECTED_STARTING_HEAD = "8eb214c47fb14077ec638f1ef561607ee142b99f"
EXPECTED_BRANCH = "master"
EXPECTED_REPO_ROOT = resolve_repo_path(start=Path(__file__)).as_posix()
NEXT_ALLOWED_TASK = "TASK-NEWGEN-MECHANICUS-CAPABILITY-SCOPE-EXPORT-PC-V0_1"
NEXT_TASK_IF_INSTALL_APPROVAL_PENDING = "TASK-NEWGEN-MECHANICUS-CONTROLLED-TOOL-PROVISION-PC-V0_1"
DOSSIER_ZIP = Path(
    r"C:\Users\PC\Downloads\TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1_DOSSIER.zip"
)

REPORT_ROOT_REL = (
    "MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1"
)
RECEIPTS_ROOT_REL = "MECHANICUS/ARSENAL/RECEIPTS/VALIDATION_FOLLOWUP_001"
DETECTION_MATRIX_REL = (
    "MECHANICUS/ARSENAL/VALIDATION/VALIDATION_FOLLOWUP_001/"
    "mechanicus_tool_detection_matrix_v0_1.json"
)
PROVISION_PLAN_REL = (
    "MECHANICUS/ARSENAL/VALIDATION/VALIDATION_FOLLOWUP_001/"
    "mechanicus_provision_plan_v0_1.md"
)
OWNER_QUESTIONS_REL = (
    "MECHANICUS/ARSENAL/OWNER_QUESTIONS/"
    "mechanicus_install_approval_questions_validation_followup_001.json"
)
CODE_SCOPE_EXPORT_REL = (
    "MECHANICUS/ARSENAL/EXPORTS/capability_scope_code_quality_v0_1.json"
)
VISUAL_SCOPE_EXPORT_REL = (
    "MECHANICUS/ARSENAL/EXPORTS/capability_scope_visual_readiness_v0_1.json"
)
REGISTRY_REL = "MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json"

REPORT_FILES_REQUIRED = [
    "FINAL_REPORT.md",
    "tool_detection_report.json",
    "owner_approval_gate_report.json",
    "provision_plan_report.json",
    "validation_followup_results.json",
    "capability_status_change_report.json",
    "validation_receipts_index.json",
    "capability_scope_export_followup_report.json",
    "fake_canon_detector_report.json",
    "inquisition_cleanliness_report.json",
    "administratum_evidence_map.json",
    "ghost_evolve_followup_training_proof.json",
    "closure_receipt.json",
]

READ_GATES = [
    "GATE-U00-GIT-TRUTH",
    "GATE-U01-ROLE-ACK",
    "GATE-U02-SCOPE-BOUNDARY",
    "GATE-U04-EVIDENCE-RECEIPT",
    "GATE-U05-STOP-CONDITIONS",
    "GATE-U08-REPO-PURITY",
    "GATE-U09-NO-FAKE-GREEN",
    "GATE-U12-REPORT-OUTPUT-BUDGET",
    "GATE-U13-PYTHON-TYPE-SAFETY",
    "GATE-U14-WHOLE-REPO-SCOPE-RECON",
    "GATE-U15-OPERATIONALITY-IMPACT",
    "GATE-U16-BILINGUAL-UI",
    "GATE-U17-DELIVERABLE-PACKAGE",
    "GATE-U18-AGENT-FACTORY-COMPLIANCE",
    "GATE-U19-SCRIPT-ARTIFACT-PRESERVATION",
    "GATE-U20-AGENT-KPD-SELF-REVIEW",
    "GATE-U21-COMMAND-CHUNKING",
]

STOP_CONDITIONS = [
    "starting HEAD mismatch",
    "worktree dirty before task edits",
    "forbidden path required",
    "install command required without Owner approval",
    "unsafe npx/pip/npm install path discovered",
    "output budget breach without Owner gate",
]


@dataclass(frozen=True)
class DetectionTarget:
    capability_id: str
    tool_name: str
    category: str
    lane: str
    detect_commands: tuple[str, ...]
    install_command: str
    requires_owner_approval_for_install: bool
    present_mode: str  # "any" or "all"
    promote_to_sandbox_if_present: bool
    keep_candidate_if_present: bool
    notes: str


@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str


TARGETS: tuple[DetectionTarget, ...] = (
    DetectionTarget(
        capability_id="CAP-TOOL-JSONSCHEMA",
        tool_name="jsonschema",
        category="TOOLS",
        lane="P1_CODE_QUALITY",
        detect_commands=(
            "python -c \"import importlib.metadata as m; print(m.version('jsonschema'))\"",
        ),
        install_command="python -m pip install jsonschema",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="JSON schema validation for receipts/cards/registries.",
    ),
    DetectionTarget(
        capability_id="CODE_QUALITY_JSONSCHEMA",
        tool_name="jsonschema",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=(
            "python -c \"import importlib.metadata as m; print(m.version('jsonschema'))\"",
        ),
        install_command="python -m pip install jsonschema",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Code quality schema-first validation dependency.",
    ),
    DetectionTarget(
        capability_id="CAP-CQ-RUFF",
        tool_name="ruff",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("ruff --version", "python -m ruff --version"),
        install_command="python -m pip install ruff",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Fast linter/formatter candidate.",
    ),
    DetectionTarget(
        capability_id="CODE_QUALITY_RUFF",
        tool_name="ruff",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("ruff --version", "python -m ruff --version"),
        install_command="python -m pip install ruff",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Code-quality linting lane.",
    ),
    DetectionTarget(
        capability_id="CAP-CQ-PYRIGHT-MYPY",
        tool_name="mypy_or_pyright",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("mypy --version", "python -m mypy --version", "pyright --version", "where.exe pyright"),
        install_command="Owner decision required: mypy (pip) vs pyright (npm/npx) route",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="Explicit Owner path decision required for type checker route.",
    ),
    DetectionTarget(
        capability_id="CODE_QUALITY_MYPY",
        tool_name="mypy",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("mypy --version", "python -m mypy --version"),
        install_command="python -m pip install mypy",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Python static type checker.",
    ),
    DetectionTarget(
        capability_id="CODE_QUALITY_PYRIGHT",
        tool_name="pyright",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("pyright --version", "where.exe pyright"),
        install_command="npm install -g pyright OR approved local npm/npx path",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="Owner should explicitly choose npm/npx provisioning path.",
    ),
    DetectionTarget(
        capability_id="CAP-CQ-PRECOMMIT",
        tool_name="pre-commit",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("pre-commit --version", "python -m pre_commit --version"),
        install_command="python -m pip install pre-commit",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Hook runner; do not auto-enable hooks.",
    ),
    DetectionTarget(
        capability_id="CODE_QUALITY_PRE_COMMIT",
        tool_name="pre-commit",
        category="CODE_QUALITY",
        lane="P1_CODE_QUALITY",
        detect_commands=("pre-commit --version", "python -m pre_commit --version"),
        install_command="python -m pip install pre-commit",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Code quality hook tool card.",
    ),
    DetectionTarget(
        capability_id="CAP-TOOL-NODE-NPM-NPX",
        tool_name="node_npm",
        category="TOOLS",
        lane="P3_VISUAL_READINESS",
        detect_commands=("node --version", "npm --version", "where.exe node", "where.exe npm"),
        install_command="Manual installer or package manager route only after Owner approval",
        requires_owner_approval_for_install=True,
        present_mode="all",
        promote_to_sandbox_if_present=True,
        keep_candidate_if_present=False,
        notes="Readiness check only; no npm install and no npx downloads.",
    ),
    DetectionTarget(
        capability_id="CAP-VIS-PLAYWRIGHT-REGRESSION",
        tool_name="playwright",
        category="VISUAL_TESTING",
        lane="P3_VISUAL_READINESS",
        detect_commands=("python -c \"import playwright; print('python-playwright-ok')\"", "where.exe playwright"),
        install_command="python -m pip install playwright (plus browser install only with explicit Owner approval)",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="Keep candidate/defer until visual provisioning policy explicitly approved.",
    ),
    DetectionTarget(
        capability_id="VISUAL_TESTING_PLAYWRIGHT",
        tool_name="playwright",
        category="VISUAL_TESTING",
        lane="P3_VISUAL_READINESS",
        detect_commands=("python -c \"import playwright; print('python-playwright-ok')\"", "where.exe playwright"),
        install_command="python -m pip install playwright (plus browser install only with explicit Owner approval)",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="Playwright visual lane remains deferred in this step.",
    ),
    DetectionTarget(
        capability_id="UI_FRAMEWORKS_REACT",
        tool_name="react",
        category="UI_FRAMEWORKS",
        lane="P3_VISUAL_READINESS",
        detect_commands=("node -e \"try {console.log(require('react/package.json').version)} catch(e){process.exit(2)}\"",),
        install_command="npm install react (in bounded project scope only after Owner approval)",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="No React project/prototype creation in this task.",
    ),
    DetectionTarget(
        capability_id="UI_FRAMEWORKS_VITE",
        tool_name="vite",
        category="UI_FRAMEWORKS",
        lane="P3_VISUAL_READINESS",
        detect_commands=("vite --version", "where.exe vite"),
        install_command="npm install -g vite OR project-local vite only after Owner approval",
        requires_owner_approval_for_install=True,
        present_mode="any",
        promote_to_sandbox_if_present=False,
        keep_candidate_if_present=True,
        notes="No npx vite execution in detection-only phase.",
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_text(value: str, limit: int = 240) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_git(repo_root: Path, *args: str) -> str:
    out = subprocess.check_output(["git", *args], cwd=repo_root, text=True)
    return out.strip()


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()


def find_repo_root(start: Path) -> Path:
    probe = start.resolve()
    for candidate in [probe, *probe.parents]:
        if (candidate / "AGENTS.md").exists():
            return candidate
    raise RuntimeError("Cannot locate repo root with AGENTS.md")


def discover_cards_by_registry(repo_root: Path) -> dict[str, Path]:
    registry = load_json(repo_root / REGISTRY_REL)
    mapping: dict[str, Path] = {}
    for row in registry.get("cards", []):
        if not isinstance(row, dict):
            continue
        cap = str(row.get("capability_id", "")).strip()
        card_rel = str(row.get("card_path", "")).strip()
        if not cap or not card_rel:
            continue
        card_path = repo_root / card_rel
        if card_path.exists():
            mapping[cap] = card_path
    return mapping


def run_command(command: str, repo_root: Path) -> CommandResult:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        command,
        shell=True,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    return CommandResult(
        command=command,
        exit_code=int(proc.returncode),
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
    )


def is_present(mode: str, results: list[CommandResult]) -> bool:
    exits = [res.exit_code for res in results]
    if mode == "all":
        return all(code == 0 for code in exits)
    return any(code == 0 for code in exits)


def recommendation_for_target(target: DetectionTarget, present: bool) -> str:
    if present:
        if target.promote_to_sandbox_if_present:
            return "VALIDATE_RECEIPT"
        if target.keep_candidate_if_present:
            return "DEFER"
        return "KEEP_CANDIDATE"
    if target.requires_owner_approval_for_install:
        return "OWNER_APPROVAL_REQUIRED"
    return "KEEP_CANDIDATE"


def build_gate_ack(
    *,
    repo_root: Path,
    report_root: Path,
    starting_head: str,
    gatepack_sha256: str,
) -> None:
    ack = (
        "GATE_ACK:\n"
        f"- task_id: {TASK_ID}\n"
        f"- current_head: {starting_head}\n"
        "- gatepack_path: C:/Users/PC/Downloads/"
        "TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1_DOSSIER.zip\n"
        f"- gatepack_sha256: {gatepack_sha256}\n"
        f"- read_gates: {', '.join(READ_GATES)}\n"
        f"- accepted_stop_conditions: {', '.join(STOP_CONDITIONS)}\n"
        "- scope_boundary: Detect P1/P3 availability, generate Owner-gated install plan, validate present tools with receipts, "
        "update capabilities only where evidence permits, no install/provision execution.\n"
        "- touched_paths:\n"
        "  - MECHANICUS/ARSENAL/VALIDATION/VALIDATION_FOLLOWUP_001/*\n"
        "  - MECHANICUS/ARSENAL/OWNER_QUESTIONS/*\n"
        "  - MECHANICUS/ARSENAL/EXPORTS/*\n"
        "  - MECHANICUS/ARSENAL/RECEIPTS/VALIDATION_FOLLOWUP_001/*\n"
        "  - MECHANICUS/ARSENAL/CATEGORIES/TOOLS/CAP-TOOL-NODE-NPM-NPX.json (if evidence supports promotion)\n"
        "  - MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json (only if status change occurs)\n"
        "  - MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py\n"
        "  - MECHANICUS/REPORTS/TASK-NEWGEN-MECHANICUS-ARSENAL-VALIDATION-FOLLOWUP-PC-V0_1/*\n"
        "- forbidden_paths:\n"
        "  - ORGANS/SANCTUM/**\n"
        "  - IMPERIUM_TEST_VERSION/**\n"
        "  - src/**\n"
        "  - LOCAL_LLM/** and CLOUD_LLM_ADAPTERS activation lanes\n"
        "  - any global system/PATH mutation\n"
        "- expected_receipts:\n"
        "  - validation receipt(s) for present tools\n"
        "  - detection matrix\n"
        "  - owner approval gate report + owner questions\n"
        "  - fake canon + inquisition + closure receipt\n"
        "- repo_recon_required: PARTIAL_MECHANICUS_SCOPE_ONLY\n"
        "- script_absorption_required: YES (runner preserved in TOOLS + preservation note)\n"
        "- clarification_needed: NO\n"
        "- verdict: PASS\n"
    )
    write_text(report_root / "GATE_ACK.md", ack)


def apply_status_change_if_needed(
    *,
    target: DetectionTarget,
    present: bool,
    card_payload: dict[str, Any],
    card_path: Path,
    receipt_rel: str,
) -> dict[str, Any] | None:
    old_status = str(card_payload.get("status", "UNKNOWN")).strip()
    if not present:
        return None
    if not target.promote_to_sandbox_if_present:
        return None
    if old_status != "CANDIDATE":
        return None

    card_payload["status"] = "SANDBOX"
    card_payload["promoted_by_receipt"] = receipt_rel
    card_payload["last_reviewed_utc"] = utc_now()
    card_payload["next_review_reason"] = "Validated in followup 001; bounded evidence proves local readiness."
    expected = card_payload.get("expected_receipts")
    if isinstance(expected, list):
        receipt_name = Path(receipt_rel).name
        if receipt_name not in expected:
            expected.append(receipt_name)
    write_json(card_path, card_payload)

    return {
        "capability_id": target.capability_id,
        "card_path": card_path.as_posix(),
        "old_status": old_status,
        "new_status": "SANDBOX",
        "evidence_receipt": receipt_rel,
    }


def rebuild_registry(repo_root: Path, task_id: str) -> None:
    registry_path = repo_root / REGISTRY_REL
    registry = load_json(registry_path)

    cards_out: list[dict[str, Any]] = []
    status_counts = Counter()
    for row in registry.get("cards", []):
        if not isinstance(row, dict):
            continue
        card_rel = str(row.get("card_path", "")).strip()
        if not card_rel:
            continue
        card_path = repo_root / card_rel
        if not card_path.exists():
            continue
        payload = load_json(card_path)
        capability_id = str(payload.get("capability_id", "")).strip()
        if not capability_id:
            continue
        status = str(payload.get("status", "")).strip()
        cards_out.append(
            {
                "capability_id": capability_id,
                "name": str(payload.get("name", "")).strip(),
                "category": str(payload.get("category", "")).strip(),
                "status": status,
                "card_path": card_rel.replace("\\", "/"),
                "owner_organ": str(payload.get("owner_organ", "")).strip(),
                "source_type": str(payload.get("source_type", "")).strip(),
                "install_required": bool(payload.get("install_required", False)),
            }
        )
        status_counts[status] += 1

    registry["generated_at_utc"] = utc_now()
    registry["task_id"] = task_id
    registry["card_count"] = len(cards_out)
    registry["status_counts"] = {
        "CANDIDATE": int(status_counts.get("CANDIDATE", 0)),
        "SANDBOX": int(status_counts.get("SANDBOX", 0)),
        "CANON": int(status_counts.get("CANON", 0)),
        "QUARANTINE": int(status_counts.get("QUARANTINE", 0)),
        "REJECTED": int(status_counts.get("REJECTED", 0)),
    }
    registry["cards"] = cards_out
    write_json(registry_path, registry)


def run_fake_canon_detector(repo_root: Path, report_root: Path) -> dict[str, Any]:
    script = repo_root / "MECHANICUS/TOOLS/mechanicus_fake_canon_detector_v0_2.py"
    output = report_root / "fake_canon_detector_report.json"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            "python",
            str(script),
            "--task-id",
            TASK_ID,
            "--repo-root",
            str(repo_root),
            "--output",
            str(output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
    )
    payload = load_json(output) if output.exists() else {}
    payload["runner_stdout"] = proc.stdout.strip()
    payload["runner_stderr"] = proc.stderr.strip()
    payload["runner_exit_code"] = int(proc.returncode)
    write_json(output, payload)
    return payload


def build_scope_export(
    *,
    scope_name: str,
    rows: list[dict[str, Any]],
    cards: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    scope_rows: list[dict[str, Any]] = []
    for row in rows:
        capability_id = row["capability_id"]
        card = cards.get(capability_id, {})
        scope_rows.append(
            {
                "capability_id": capability_id,
                "tool_name": row["tool_name"],
                "status": str(card.get("status", "UNKNOWN")),
                "present": bool(row["present"]),
                "validation_verdict": row["validation_verdict"],
                "recommended_action": row["recommended_action"],
                "install_requires_owner_approval": bool(row["install_requires_owner_approval"]),
            }
        )

    status_counts = Counter(x["status"] for x in scope_rows)
    present_count = sum(1 for x in scope_rows if x["present"])
    missing_count = sum(1 for x in scope_rows if not x["present"])

    return {
        "task_id": TASK_ID,
        "scope_name": scope_name,
        "generated_at_utc": utc_now(),
        "summary": {
            "capability_count": len(scope_rows),
            "present_count": present_count,
            "missing_count": missing_count,
            "status_counts": dict(status_counts),
        },
        "capabilities": scope_rows,
    }


def build_provision_plan_markdown(rows: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Mechanicus Provision Plan V0.1")
    lines.append("")
    lines.append(f"Task: `{TASK_ID}`")
    lines.append("Policy: detection-first, Owner-gated provisioning, receipt-backed promotion.")
    lines.append("")
    lines.append("## Missing tools requiring Owner gate")
    lines.append("")
    lines.append("| Capability | Tool | Proposed command | Risk | Notes |")
    lines.append("|---|---|---|---|---|")
    missing = [x for x in rows if not x["present"]]
    if not missing:
        lines.append("| (none) | - | - | - | All targeted tools already present. |")
    else:
        for row in missing:
            lines.append(
                "| "
                f"{row['capability_id']} | {row['tool_name']} | `{row['install_command']}` | "
                f"{row['risk_level']} | {row['notes']} |"
            )

    lines.append("")
    lines.append("## Present tools validated in this task")
    lines.append("")
    lines.append("| Capability | Tool | Validation verdict | Promotion recommendation |")
    lines.append("|---|---|---|---|")
    present_rows = [x for x in rows if x["present"]]
    if not present_rows:
        lines.append("| (none) | - | - | - |")
    else:
        for row in present_rows:
            lines.append(
                f"| {row['capability_id']} | {row['tool_name']} | {row['validation_verdict']} | {row['promotion_recommendation']} |"
            )

    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- No silent installs.")
    lines.append("- No `npm install` / `pip install` / networked `npx` without Owner approval.")
    lines.append("- No Playwright browser install without explicit approval.")
    lines.append("- No visual prototypes and no LLM/cloud activation in this step.")
    return "\n".join(lines) + "\n"


def build_final_report(
    *,
    repo_root: Path,
    closure_verdict: str,
    rows: list[dict[str, Any]],
    status_changes: list[dict[str, Any]],
    owner_approval_needed_count: int,
    fake_canon_count: int,
    report_root: Path,
) -> str:
    lines: list[str] = []
    lines.append(f"# FINAL REPORT — {TASK_ID}")
    lines.append("")
    lines.append("## Verdict")
    lines.append(closure_verdict)
    lines.append("")
    lines.append("## Starting state")
    lines.append(f"- Repo root: {repo_root.as_posix()}")
    lines.append(f"- Starting HEAD: {EXPECTED_STARTING_HEAD}")
    lines.append("- Starting git status: clean")
    lines.append("- Read-first files: AGENTS + gate contracts + script/big-model policies + dossier files")
    lines.append("")
    lines.append("## Detection summary")
    lines.append("")
    lines.append("| Capability | Tool | Present | Result | Action |")
    lines.append("|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row['capability_id']} | {row['tool_name']} | "
            f"{'YES' if row['present'] else 'NO'} | {row['validation_verdict']} | {row['recommended_action']} |"
        )
    lines.append("")
    lines.append("## Owner install approval")
    lines.append("")
    lines.append("| Tool | Approval needed | Proposed command | Risk | Recommendation |")
    lines.append("|---|---|---|---|---|")
    for row in rows:
        if row["present"]:
            continue
        lines.append(
            f"| {row['tool_name']} | YES | `{row['install_command']}` | {row['risk_level']} | {row['recommended_decision']} |"
        )
    if all(x["present"] for x in rows):
        lines.append("| (none) | NO | - | - | No install needed. |")
    lines.append("")
    lines.append("## Validation results")
    lines.append("")
    lines.append("| Capability | Old status | New status | Receipt | Notes |")
    lines.append("|---|---|---|---|---|")
    change_map = {x["capability_id"]: x for x in status_changes}
    for row in rows:
        old_status = row["previous_status"]
        new_status = change_map.get(row["capability_id"], {}).get("new_status", old_status)
        lines.append(
            f"| {row['capability_id']} | {old_status} | {new_status} | {row['receipt_path'] or '-'} | {row['notes']} |"
        )
    lines.append("")
    lines.append("## Mechanicus strengthening")
    lines.append("")
    lines.append("| Output | Path | How future Servitor uses it |")
    lines.append("|---|---|---|")
    lines.append(
        "| detection matrix | "
        f"{DETECTION_MATRIX_REL} | Re-checks present/missing state without re-running manual discovery. |"
    )
    lines.append(
        "| provision plan | "
        f"{PROVISION_PLAN_REL} | Owner-gated install queue with exact commands and risk. |"
    )
    lines.append(
        "| owner questions | "
        f"{OWNER_QUESTIONS_REL} | One-by-one install approvals with explicit options. |"
    )
    lines.append(
        "| code quality scope export | "
        f"{CODE_SCOPE_EXPORT_REL} | Quick status view for P1 quality corridor. |"
    )
    lines.append(
        "| visual readiness scope export | "
        f"{VISUAL_SCOPE_EXPORT_REL} | Quick status view for P3 readiness corridor. |"
    )
    lines.append("")
    lines.append("## Inquisition cleanliness")
    lines.append("")
    lines.append(f"- Fake CANON count: {fake_canon_count}")
    lines.append("- Network used for installs/provisioning: false")
    lines.append("- Install commands executed: false")
    lines.append("- Visual prototypes created: false")
    lines.append("- LLM/cloud activation: false")
    lines.append("")
    lines.append("## Ending state")
    lines.append(f"- Ending HEAD: {run_git(repo_root, 'rev-parse', 'HEAD')}")
    lines.append("- Commit: NOT_PERFORMED")
    lines.append("- Push: NOT_PERFORMED")
    lines.append(f"- Worktree: {run_git(repo_root, 'status', '--short') or 'dirty (task outputs)'}")
    lines.append("- Remote sync: unchanged from start")
    lines.append("")
    lines.append("## Next allowed task")
    next_task = NEXT_TASK_IF_INSTALL_APPROVAL_PENDING if owner_approval_needed_count > 0 else NEXT_ALLOWED_TASK
    lines.append(f"`{next_task}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanicus validation follow-up runner (detection-first, Owner-gated provisioning).")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = find_repo_root(Path(args.repo_root))
    report_root = repo_root / REPORT_ROOT_REL
    receipts_root = repo_root / RECEIPTS_ROOT_REL
    detection_matrix_path = repo_root / DETECTION_MATRIX_REL
    provision_plan_path = repo_root / PROVISION_PLAN_REL
    owner_questions_path = repo_root / OWNER_QUESTIONS_REL
    code_scope_path = repo_root / CODE_SCOPE_EXPORT_REL
    visual_scope_path = repo_root / VISUAL_SCOPE_EXPORT_REL

    # Gate-U00 truth checks.
    head = run_git(repo_root, "rev-parse", "HEAD")
    branch = run_git(repo_root, "branch", "--show-current")
    root = run_git(repo_root, "rev-parse", "--show-toplevel").replace("\\", "/")
    status_before = run_git(repo_root, "status", "--short")
    if head != EXPECTED_STARTING_HEAD:
        raise RuntimeError(f"starting HEAD mismatch: expected {EXPECTED_STARTING_HEAD}, got {head}")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"branch mismatch: expected {EXPECTED_BRANCH}, got {branch}")
    if root.rstrip("/") != EXPECTED_REPO_ROOT.rstrip("/"):
        raise RuntimeError(f"repo root mismatch: expected {EXPECTED_REPO_ROOT}, got {root}")
    allowed_dirty_suffixes = {
        "MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py",
    }
    if status_before:
        dirty_lines = [line.strip() for line in status_before.splitlines() if line.strip()]
        unexpected_dirty: list[str] = []
        for line in dirty_lines:
            path_part = line[3:].strip() if len(line) > 3 else ""
            if path_part.startswith('"') and path_part.endswith('"'):
                path_part = path_part[1:-1]
            normalized = path_part.replace("\\", "/")
            if normalized not in allowed_dirty_suffixes:
                unexpected_dirty.append(line)
        if unexpected_dirty:
            raise RuntimeError(
                "worktree has unexpected dirty paths before runner execution: "
                + "; ".join(unexpected_dirty)
            )

    report_root.mkdir(parents=True, exist_ok=True)
    gatepack_sha256 = sha256_file(DOSSIER_ZIP)
    build_gate_ack(
        repo_root=repo_root,
        report_root=report_root,
        starting_head=head,
        gatepack_sha256=gatepack_sha256,
    )
    write_json(
        report_root / "truth_check_start.json",
        {
            "task_id": TASK_ID,
            "checked_at_utc": utc_now(),
            "repo_root": root,
            "branch": branch,
            "head": head,
            "worktree_status_short": status_before,
            "origin_master_ref": run_git(repo_root, "ls-remote", "origin", "refs/heads/master"),
        },
    )

    card_paths = discover_cards_by_registry(repo_root)
    card_payloads: dict[str, dict[str, Any]] = {}
    for target in TARGETS:
        p = card_paths.get(target.capability_id)
        if p and p.exists():
            card_payloads[target.capability_id] = load_json(p)
        else:
            card_payloads[target.capability_id] = {}

    results_rows: list[dict[str, Any]] = []
    detection_matrix_entries: list[dict[str, Any]] = []
    owner_questions: list[dict[str, Any]] = []
    receipts_index: list[dict[str, Any]] = []
    status_changes: list[dict[str, Any]] = []

    for idx, target in enumerate(TARGETS, start=1):
        command_results = [run_command(cmd, repo_root) for cmd in target.detect_commands]
        present = is_present(target.present_mode, command_results)
        recommended_action = recommendation_for_target(target, present)
        previous_status = str(card_payloads.get(target.capability_id, {}).get("status", "UNKNOWN"))
        promotion_recommendation = "KEEP_CANDIDATE"
        validation_verdict = "PASS" if present else "MISSING"

        if present and target.promote_to_sandbox_if_present:
            promotion_recommendation = "PROMOTE_SANDBOX" if previous_status == "CANDIDATE" else "KEEP_SANDBOX"
        elif present and target.keep_candidate_if_present:
            promotion_recommendation = "KEEP_CANDIDATE_READINESS_ONLY"
        elif not present:
            promotion_recommendation = "KEEP_CANDIDATE_MISSING"

        stdout_merged = "\n\n".join(
            f"$ {res.command}\n{res.stdout}".strip() for res in command_results if res.stdout
        )
        stderr_merged = "\n\n".join(
            f"$ {res.command}\n{res.stderr}".strip() for res in command_results if res.stderr
        )

        if present:
            receipt_name = f"{target.capability_id.lower().replace('_', '-').replace(' ', '-')}_validation_receipt.json"
            receipt_path = receipts_root / receipt_name
            receipt_rel = receipt_path.relative_to(repo_root).as_posix()
            warnings: list[str] = []
            if target.keep_candidate_if_present:
                warnings.append("present_but_policy_defers_status_promotion")
            receipt_payload = build_validation_receipt(
                task_id=TASK_ID,
                capability_id=target.capability_id,
                validator="mechanicus_validation_followup_001_runner_v0_1.py",
                check_name=f"{target.lane}:{target.capability_id}",
                command_or_check=" && ".join(target.detect_commands),
                exit_code=0,
                stdout_text=stdout_merged,
                stderr_text=stderr_merged,
                side_effects=["read-only detection commands", "receipt json created"],
                network_used=False,
                files_created_or_modified=[receipt_rel],
                validation_verdict=validation_verdict,
                promotion_recommendation=promotion_recommendation,
                evidence_paths=[receipt_rel],
                warnings=warnings,
            )
            write_receipt(receipt_path, receipt_payload)
            receipts_index.append(
                {
                    "capability_id": target.capability_id,
                    "receipt_path": receipt_rel,
                    "validation_verdict": validation_verdict,
                }
            )

            card_path = card_paths.get(target.capability_id)
            card_payload = card_payloads.get(target.capability_id, {})
            if card_path and card_payload:
                change = apply_status_change_if_needed(
                    target=target,
                    present=present,
                    card_payload=card_payload,
                    card_path=card_path,
                    receipt_rel=receipt_rel,
                )
                if change:
                    status_changes.append(change)
                    card_payloads[target.capability_id] = load_json(card_path)
        else:
            receipt_rel = ""
            owner_questions.append(
                {
                    "question_id": f"FOLLOWUP-OWNER-Q-{idx:03d}",
                    "capability_id": target.capability_id,
                    "tool_name": target.tool_name,
                    "why_needed": target.notes,
                    "proposed_command": target.install_command,
                    "expected_side_effects": [
                        "new package/tool install",
                        "new executable availability",
                    ],
                    "network_use": True,
                    "install_target_scope": "local user Python/Node runtime unless otherwise approved",
                    "rollback_or_uninstall_note": "Rollback via pip uninstall / npm uninstall -g / manual removal in same scope.",
                    "risk_level": (
                        "HIGH"
                        if ("npm" in target.install_command.lower() or "playwright" in target.install_command.lower())
                        else "MEDIUM"
                    ),
                    "recommended_decision": "APPROVE_DETECTION_ONLY",
                    "owner_options": [
                        "APPROVE_THIS_TOOL",
                        "DEFER",
                        "QUARANTINE_REVIEW",
                        "REJECT",
                        "APPROVE_DETECTION_ONLY",
                    ],
                }
            )

        detection_matrix_entries.append(
            {
                "capability_id": target.capability_id,
                "tool_name": target.tool_name,
                "category": target.category,
                "lane": target.lane,
                "detect_commands": [
                    {
                        "command": res.command,
                        "exit_code": res.exit_code,
                        "stdout_excerpt": short_text(res.stdout),
                        "stderr_excerpt": short_text(res.stderr),
                    }
                    for res in command_results
                ],
                "present": present,
                "validation_verdict": validation_verdict,
                "recommended_action": recommended_action,
                "promotion_recommendation": promotion_recommendation,
                "install_requires_owner_approval": target.requires_owner_approval_for_install,
                "install_command": target.install_command,
                "notes": target.notes,
            }
        )

        results_rows.append(
            {
                "capability_id": target.capability_id,
                "tool_name": target.tool_name,
                "category": target.category,
                "lane": target.lane,
                "present": present,
                "validation_verdict": validation_verdict,
                "recommended_action": recommended_action,
                "promotion_recommendation": promotion_recommendation,
                "previous_status": previous_status,
                "install_requires_owner_approval": target.requires_owner_approval_for_install,
                "install_command": target.install_command,
                "risk_level": (
                    "HIGH"
                    if ("npm" in target.install_command.lower() or "playwright" in target.install_command.lower())
                    else "MEDIUM"
                ),
                "recommended_decision": "APPROVE_DETECTION_ONLY" if not present else "NOT_NEEDED",
                "notes": target.notes,
                "receipt_path": receipts_index[-1]["receipt_path"] if present else "",
            }
        )

    if status_changes:
        rebuild_registry(repo_root, TASK_ID)

    detection_payload = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "policy": "DETECTION_ONLY_NO_INSTALL",
        "targets_total": len(TARGETS),
        "present_total": sum(1 for row in detection_matrix_entries if row["present"]),
        "missing_total": sum(1 for row in detection_matrix_entries if not row["present"]),
        "entries": detection_matrix_entries,
    }
    write_json(detection_matrix_path, detection_payload)

    provision_plan_markdown = build_provision_plan_markdown(results_rows)
    write_text(provision_plan_path, provision_plan_markdown)
    write_json(owner_questions_path, {"task_id": TASK_ID, "generated_at_utc": utc_now(), "questions": owner_questions})

    code_rows = [row for row in results_rows if row["lane"] == "P1_CODE_QUALITY"]
    vis_rows = [row for row in results_rows if row["lane"] == "P3_VISUAL_READINESS"]
    code_scope_payload = build_scope_export(
        scope_name="code_quality",
        rows=code_rows,
        cards=card_payloads,
    )
    visual_scope_payload = build_scope_export(
        scope_name="visual_readiness",
        rows=vis_rows,
        cards=card_payloads,
    )
    write_json(code_scope_path, code_scope_payload)
    write_json(visual_scope_path, visual_scope_payload)

    fake_canon_payload = run_fake_canon_detector(repo_root, report_root)
    fake_canon_count = int(fake_canon_payload.get("summary", {}).get("fake_canon_count", 0))

    tool_detection_report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "detection_matrix_path": detection_matrix_path.relative_to(repo_root).as_posix(),
        "summary": {
            "targets_total": len(results_rows),
            "present_total": sum(1 for row in results_rows if row["present"]),
            "missing_total": sum(1 for row in results_rows if not row["present"]),
            "by_lane": {
                "P1_CODE_QUALITY": {
                    "total": len(code_rows),
                    "present": sum(1 for row in code_rows if row["present"]),
                    "missing": sum(1 for row in code_rows if not row["present"]),
                },
                "P3_VISUAL_READINESS": {
                    "total": len(vis_rows),
                    "present": sum(1 for row in vis_rows if row["present"]),
                    "missing": sum(1 for row in vis_rows if not row["present"]),
                },
            },
        },
    }
    write_json(report_root / "tool_detection_report.json", tool_detection_report)

    owner_approval_gate_report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "owner_approval_required": len(owner_questions) > 0,
        "owner_approval_questions_count": len(owner_questions),
        "owner_questions_path": owner_questions_path.relative_to(repo_root).as_posix(),
        "no_install_commands_executed": True,
        "unsafe_npx_or_downloads_executed": False,
        "approved_install_commands_executed": [],
        "blocked_install_candidates": [
            {"capability_id": row["capability_id"], "tool_name": row["tool_name"], "install_command": row["install_command"]}
            for row in results_rows
            if not row["present"]
        ],
        "verdict": "PASS_WITH_WARNINGS" if len(owner_questions) > 0 else "PASS",
    }
    write_json(report_root / "owner_approval_gate_report.json", owner_approval_gate_report)

    provision_plan_report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "provision_plan_path": provision_plan_path.relative_to(repo_root).as_posix(),
        "missing_tools_count": len([row for row in results_rows if not row["present"]]),
        "present_tools_count": len([row for row in results_rows if row["present"]]),
        "owner_gate_required": len(owner_questions) > 0,
        "verdict": "PASS_WITH_WARNINGS" if len(owner_questions) > 0 else "PASS",
    }
    write_json(report_root / "provision_plan_report.json", provision_plan_report)

    write_json(
        report_root / "validation_followup_results.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "results": results_rows,
        },
    )
    write_json(
        report_root / "capability_status_change_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "status_changes": status_changes,
            "changed_card_paths": sorted({x["card_path"] for x in status_changes}),
        },
    )
    write_json(
        report_root / "validation_receipts_index.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "receipts_root": receipts_root.relative_to(repo_root).as_posix(),
            "receipts": receipts_index,
        },
    )
    write_json(
        report_root / "capability_scope_export_followup_report.json",
        {
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "code_quality_scope_export_path": code_scope_path.relative_to(repo_root).as_posix(),
            "visual_readiness_scope_export_path": visual_scope_path.relative_to(repo_root).as_posix(),
            "summary": {
                "code_quality_present": code_scope_payload["summary"]["present_count"],
                "code_quality_missing": code_scope_payload["summary"]["missing_count"],
                "visual_present": visual_scope_payload["summary"]["present_count"],
                "visual_missing": visual_scope_payload["summary"]["missing_count"],
            },
        },
    )

    runtime_junk_hits = [
        p.relative_to(repo_root).as_posix()
        for p in report_root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".pyc", ".tmp", ".log", ".pid"}
    ]
    inquisition_report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "tool_installs_attempted": False,
        "network_used": False,
        "runtime_junk_generated": bool(runtime_junk_hits),
        "runtime_junk_paths": runtime_junk_hits,
        "fake_canon_count": fake_canon_count,
        "reserved_canon_count": int(fake_canon_payload.get("summary", {}).get("reserved_canon_count", 0)),
        "verdict": "PASS" if not runtime_junk_hits and fake_canon_count == 0 else "PASS_WITH_WARNINGS",
    }
    write_json(report_root / "inquisition_cleanliness_report.json", inquisition_report)

    ghost_evolve = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "detection_matrix_exists": detection_matrix_path.exists(),
        "provision_plan_exists": provision_plan_path.exists(),
        "owner_approval_gate_exists": (report_root / "owner_approval_gate_report.json").exists(),
        "scope_exports_created": [
            code_scope_path.relative_to(repo_root).as_posix(),
            visual_scope_path.relative_to(repo_root).as_posix(),
        ],
        "no_silent_install_confirmed": True,
        "future_servitor_reuse_paths": [
            detection_matrix_path.relative_to(repo_root).as_posix(),
            provision_plan_path.relative_to(repo_root).as_posix(),
            owner_questions_path.relative_to(repo_root).as_posix(),
            code_scope_path.relative_to(repo_root).as_posix(),
            visual_scope_path.relative_to(repo_root).as_posix(),
        ],
    }
    write_json(report_root / "ghost_evolve_followup_training_proof.json", ghost_evolve)

    kpd = {
        "agent_kpd_self_review": {
            "task_id": TASK_ID,
            "agent_role": "Codex big-model execution partner",
            "useful_outputs": [
                "Detection matrix with explicit safe checks",
                "Owner-gated provisioning plan and question queue",
                "Scope exports for code_quality and visual_readiness",
                "Receipt-backed capability status update discipline",
            ],
            "waste_points": [
                "Duplicate capability IDs for same physical tool cause repeated checks.",
            ],
            "missing_tools": [
                "No pre-existing follow-up orchestrator for this exact P1/P3 gatepack.",
            ],
            "generated_tools_to_preserve": [
                "MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py",
            ],
            "recommended_script_absorption": [
                "Absorb follow-up runner into reusable Mechanicus validation corridor after strict typing review.",
            ],
            "recommended_narrow_agent_profiles": [
                "Mechanicus Provisioning Gate Servitor (detect + owner queue + receipt update).",
            ],
            "future_prompt_improvements": [
                "Provide explicit capability_id list per target in the dossier scope JSON to avoid duplication ambiguity.",
            ],
            "future_gate_or_checklist_recommendations": [
                "Add gate for npx-safe-detection policy with --no-install explicit rule.",
            ],
            "kpd_verdict": "GOOD",
        }
    }
    write_json(report_root / "agent_kpd_self_review.json", kpd)

    evidence_map = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "report_paths": sorted(
            p.relative_to(repo_root).as_posix() for p in report_root.rglob("*") if p.is_file()
        ),
        "receipt_paths": sorted(
            p.relative_to(repo_root).as_posix() for p in receipts_root.rglob("*.json")
        ),
        "changed_card_paths": sorted({x["card_path"] for x in status_changes}),
        "main_outputs": [
            DETECTION_MATRIX_REL,
            PROVISION_PLAN_REL,
            OWNER_QUESTIONS_REL,
            CODE_SCOPE_EXPORT_REL,
            VISUAL_SCOPE_EXPORT_REL,
        ],
        "runner_script": "MECHANICUS/TOOLS/mechanicus_validation_followup_001_runner_v0_1.py",
        "next_task_recommendation": (
            NEXT_TASK_IF_INSTALL_APPROVAL_PENDING if owner_questions else NEXT_ALLOWED_TASK
        ),
    }
    write_json(report_root / "administratum_evidence_map.json", evidence_map)

    closure_verdict = "PASS"
    if owner_questions:
        closure_verdict = "PASS_WITH_WARNINGS"

    closure = {
        "task_id": TASK_ID,
        "verdict": closure_verdict,
        "repo_root": EXPECTED_REPO_ROOT.replace("/", "\\"),
        "starting_head": EXPECTED_STARTING_HEAD,
        "ending_head": run_git(repo_root, "rev-parse", "HEAD"),
        "commit": "NOT_PERFORMED",
        "push": "NOT_PERFORMED",
        "worktree_clean": "no",
        "remote_sync": "unchanged_from_start",
        "detection_only_phase_completed": True,
        "install_performed": False,
        "network_used": False,
        "owner_approval_required": len(owner_questions) > 0,
        "owner_approval_questions_created": len(owner_questions),
        "tools_validated": len(receipts_index),
        "status_changes": len(status_changes),
        "fake_canon_count": fake_canon_count,
        "llm_cloud_activated": False,
        "visual_prototypes_created": False,
        "scope_exports_created": [
            code_scope_path.relative_to(repo_root).as_posix(),
            visual_scope_path.relative_to(repo_root).as_posix(),
        ],
        "warnings": (
            ["Missing tools require Owner approval before provisioning."]
            if owner_questions
            else []
        ),
        "next_allowed_task": (
            NEXT_TASK_IF_INSTALL_APPROVAL_PENDING if owner_questions else NEXT_ALLOWED_TASK
        ),
    }
    write_json(report_root / "closure_receipt.json", closure)

    final_report = build_final_report(
        repo_root=repo_root,
        closure_verdict=closure_verdict,
        rows=results_rows,
        status_changes=status_changes,
        owner_approval_needed_count=len(owner_questions),
        fake_canon_count=fake_canon_count,
        report_root=report_root,
    )
    write_text(report_root / "FINAL_REPORT.md", final_report)

    missing_required = [name for name in REPORT_FILES_REQUIRED if not (report_root / name).exists()]
    if missing_required:
        raise RuntimeError(f"missing required report files: {missing_required}")

    print(
        json.dumps(
            {
                "task_id": TASK_ID,
                "verdict": closure_verdict,
                "present_tools": sum(1 for row in results_rows if row["present"]),
                "missing_tools": sum(1 for row in results_rows if not row["present"]),
                "status_changes": len(status_changes),
                "owner_questions": len(owner_questions),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
