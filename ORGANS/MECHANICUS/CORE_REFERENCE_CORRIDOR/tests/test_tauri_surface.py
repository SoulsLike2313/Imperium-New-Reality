from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.diagnostic import collect_diagnostic
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.registry import (
    CapabilityRegistry,
    RegistryError,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.tauri_surface_inventory import (
    REQUIRED_LEGACY,
    build_inventory,
    evaluate_surface,
    parse_invoke_handler,
)


ROOT = Path(__file__).resolve().parents[4]
MAIN = ROOT / "SUPPORT/APP_TAURI/src-tauri/src/main.rs"


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def inventory() -> dict:
    return build_inventory(ROOT)


def test_phase3_01_inventory_equals_real_rust_invoke_surface(inventory: dict) -> None:
    parsed = [item.split("::")[-1] for item in parse_invoke_handler(MAIN.read_text(encoding="utf-8"))]

    assert inventory["inventory_method"] == "PARSE_REAL_RUST_INVOKE_HANDLER_NOT_FRONTEND_DECLARATIONS"
    assert inventory["registered_tauri_commands"] == parsed
    assert parsed == ["corridor_ui_snapshot", "corridor_ui_action"]
    assert set(inventory["effect_classification"]) == set(parsed)


def test_phase3_02_unknown_effect_blocks_surface_verdict() -> None:
    result = evaluate_surface(
        [
            {
                "command": "mystery",
                "effect": "UNKNOWN",
                "canonical_capability_registry_routed": False,
                "typed_executor_routed": False,
                "owner_gate_required": False,
            }
        ],
        [],
        [],
    )

    assert result["unknown_commands"] == ["mystery"]
    assert result["surface_verdict"] == "PHASE_3_BLOCKED"


def test_phase3_03_unrouted_or_ungated_mutation_blocks_surface_verdict() -> None:
    result = evaluate_surface(
        [
            {
                "command": "direct_mutation",
                "effect": "MUTATING",
                "canonical_capability_registry_routed": False,
                "typed_executor_routed": False,
                "owner_gate_required": False,
            }
        ],
        [],
        [],
    )

    assert result["unregistered_mutating_commands"] == ["direct_mutation"]
    assert result["unrouted_mutating_commands"] == ["direct_mutation"]
    assert result["ungated_mutating_commands"] == ["direct_mutation"]
    assert result["surface_verdict"] == "PHASE_3_BLOCKED"


def test_phase3_04_required_legacy_mutations_fail_closed(inventory: dict) -> None:
    probes = {row["command"]: row for row in inventory["legacy_command_probes"]}

    assert set(REQUIRED_LEGACY).issubset(probes)
    for command in REQUIRED_LEGACY:
        probe = probes[command]
        assert probe["effect"] == "MUTATING"
        assert probe["rust_command_attribute_present"] is False
        assert probe["registered_in_invoke_handler"] is False
        assert probe["corridor_reachable"] is False
        assert probe["direct_invocation_result"] == "BLOCK_COMMAND_NOT_REGISTERED"


def test_phase3_05_every_reachable_mutation_is_canonical_typed_and_gated(
    inventory: dict,
) -> None:
    mutations = [row for row in inventory["commands"] if row["effect"] == "MUTATING"]

    assert [row["command"] for row in mutations] == ["corridor_ui_action"]
    assert all(row["canonical_capability_registry_routed"] for row in mutations)
    assert all(row["typed_executor_routed"] for row in mutations)
    assert all(row["owner_gate_required"] for row in mutations)
    assert inventory["surface_verdict"] == "LEGACY_MUTATION_SURFACE_CLOSED"


def test_phase3_06_unknown_capability_is_default_denied() -> None:
    registry = CapabilityRegistry(ROOT / "not-read-in-this-test.json")
    registry.data = {"capabilities": [], "ui_actions": []}

    with pytest.raises(RegistryError, match="CAPABILITY_NOT_REGISTERED"):
        registry.resolve("UNKNOWN_MUTATING_CAPABILITY", "run")


def test_phase3_07_frontend_unknown_command_blocks_inventory(inventory: dict) -> None:
    result = evaluate_surface(inventory["commands"], inventory["legacy_command_probes"], ["frontend_unknown"])

    assert result["frontend_unknown_commands"] == ["frontend_unknown"]
    assert result["surface_verdict"] == "PHASE_3_BLOCKED"


def test_phase3_08_read_only_diagnostic_preserves_reality() -> None:
    reality = Path(_git(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve().parent
    before = {
        "head": _git(reality, "rev-parse", "HEAD"),
        "origin": _git(reality, "rev-parse", "origin/master"),
        "status": _git(reality, "status", "--porcelain=v1"),
    }

    result = collect_diagnostic(ROOT)

    after = {
        "head": _git(reality, "rev-parse", "HEAD"),
        "origin": _git(reality, "rev-parse", "origin/master"),
        "status": _git(reality, "status", "--porcelain=v1"),
    }
    assert result["verdict"] == "PASS_PROVEN"
    assert result["git"]["reality_matches_origin_master"] is True
    assert before == after
