from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_verdict_payload(
    *,
    organ_id: str,
    task_id: str,
    mode: str,
    verdict: str,
    applied_rules: Iterable[str],
    required_actions: Iterable[str],
    forbidden_actions: Iterable[str],
    evidence_required: Iterable[str],
    evidence_refs: Iterable[str],
    not_proven: Iterable[str],
    owner_question: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema_id": "newgen_organ_verdict_v0_1",
        "organ_id": organ_id,
        "task_id": task_id,
        "mode": mode,
        "verdict": verdict,
        "applied_rules": list(applied_rules),
        "required_actions": list(required_actions),
        "forbidden_actions": list(forbidden_actions),
        "evidence_required": list(evidence_required),
        "owner_question": owner_question,
        "not_proven": list(not_proven),
        "evidence_refs": list(evidence_refs),
    }


def read_organ_bundle(organ_root: Path) -> Dict[str, Any]:
    identity_path = organ_root / "IDENTITY" / "organ_identity_v0_1.md"
    contract_path = organ_root / "CONTRACTS" / "servitor_contract_v0_1.md"
    gate_catalog_path = organ_root / "GATES" / "organ_gate_catalog_v0_1.json"
    state_path = organ_root / "STATE" / "current_state_v0_1.json"
    template_path = organ_root / "TEMPLATES" / "organ_verdict_template_v0_1.json"
    return {
        "identity_path": str(identity_path),
        "contract_path": str(contract_path),
        "gate_catalog_path": str(gate_catalog_path),
        "state_path": str(state_path),
        "template_path": str(template_path),
        "gate_catalog": load_json(gate_catalog_path),
        "state": load_json(state_path),
        "template": load_json(template_path),
    }


def _to_lines(values: Iterable[str]) -> List[str]:
    lines = [str(item).strip() for item in values if str(item).strip()]
    return lines if lines else ["none"]


def render_tui(
    *,
    organ_title: str,
    color: str,
    responsibility: str,
    ask_map: Iterable[str],
    warn_block_map: Iterable[str],
    bundle: Dict[str, Any],
    verdict_payload: Dict[str, Any],
) -> None:
    if not HAVE_RICH:
        print(f"[{organ_title}] Rich unavailable, plain fallback active.")
        print(json.dumps({"bundle": bundle, "verdict": verdict_payload}, ensure_ascii=False, indent=2))
        return

    console = Console()
    header = (
        f"{organ_title}\n"
        f"responsibility: {responsibility}\n"
        f"verdict: {verdict_payload.get('verdict', 'UNKNOWN')}\n"
        f"mode: {verdict_payload.get('mode', 'SERVITOR_QUERY')}"
    )
    console.print(Panel(header, title="WAVE1 ORGAN TUI", border_style=color))

    table = Table(title="Servitor Interface", border_style=color)
    table.add_column("Block", style=color)
    table.add_column("Value")
    table.add_row("Ask", "\n".join(_to_lines(ask_map)))
    table.add_row("Warn/Block", "\n".join(_to_lines(warn_block_map)))
    table.add_row("Gate Catalog", str(bundle.get("gate_catalog_path", "")))
    table.add_row("State", str(bundle.get("state_path", "")))
    table.add_row("Contract", str(bundle.get("contract_path", "")))
    table.add_row("Identity", str(bundle.get("identity_path", "")))
    console.print(table)

    gate_table = Table(title="Gate Preview", border_style=color)
    gate_table.add_column("Gate ID", style=color)
    gate_table.add_column("Severity")
    gate_table.add_column("Verdict")
    gates = bundle.get("gate_catalog", {}).get("gates", [])
    if isinstance(gates, list):
        for gate in gates[:8]:
            if isinstance(gate, dict):
                gate_table.add_row(
                    str(gate.get("gate_id", "UNKNOWN")),
                    str(gate.get("severity", "UNKNOWN")),
                    str(gate.get("expected_verdict", "n/a")),
                )
    console.print(gate_table)
