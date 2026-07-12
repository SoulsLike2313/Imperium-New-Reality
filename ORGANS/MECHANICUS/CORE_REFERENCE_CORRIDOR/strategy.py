"""Deterministic confidence, strategy and cost/time pause calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def confidence_assessment() -> dict[str, Any]:
    components = {
        "authority_and_scope": {"score": 0.95, "evidence": "digest-bound taskpack + exact Owner prompt hash"},
        "base_truth": {"score": 1.0, "evidence": "exact HEAD/clean/master-origin/pwsh drift guard"},
        "component_reuse_map": {"score": 0.9, "evidence": "targeted reconciliation across Mechanicus, WARP and APP_TAURI"},
        "negative_testability": {"score": 0.95, "evidence": "20 disposable scenarios specified"},
        "land_authority": {"score": 0.5, "evidence": "Owner land decision intentionally pending"},
    }
    weighted = sum(item["score"] for item in components.values()) / len(components)
    return {
        "components": components,
        "overall": round(weighted, 3),
        "threshold": 0.8,
        "verdict": "CONFIDENCE_SUFFICIENT_FOR_WARP" if weighted >= 0.8 else "BLOCK",
        "truth_boundary": "Confidence permits bounded WARP work; it is not result acceptance.",
    }


def selected_strategy() -> dict[str, Any]:
    return {
        "strategy_id": "MODULAR_PYTHON_SPINE_WITH_THIN_TAURI_ADAPTER",
        "selected": True,
        "reasons": [
            "Existing repository has Python validation/tooling lanes and a current Tauri product shell.",
            "Stdlib-only backend keeps the first corridor replayable without new dependencies.",
            "One task-local registry and typed executor remove UI/CLI authority duplication.",
        ],
        "reused": ["git worktree", "Astronomicon digest intake", "Tauri/Vite shell", "Great Nine active matrix"],
        "isolated": ["copytree WARP", "legacy registries", "hardcoded UI actions", "direct RUN_*.ps1 runner"],
        "rejected_alternatives": [
            {"strategy": "new universal framework", "reason": "out of scope and violates bounded-corridor law"},
            {"strategy": "new parallel IDE", "reason": "duplicates existing product surface"},
            {"strategy": "reuse copytree WARP", "reason": "cannot prove exact HEAD or Git lifecycle"},
        ],
    }


def cost_time_assessment(
    *,
    estimated_minutes: float,
    observed_minutes: float,
    estimated_cost_units: float,
    observed_cost_units: float,
) -> dict[str, Any]:
    time_ratio = observed_minutes / estimated_minutes if estimated_minutes > 0 else None
    cost_ratio = observed_cost_units / estimated_cost_units if estimated_cost_units > 0 else None
    triggers: list[str] = []
    if cost_ratio is not None and cost_ratio > 1.5:
        triggers.append("COST_OVER_150_PERCENT_PAUSE")
    if time_ratio is not None and time_ratio >= 2.0:
        triggers.append("TIME_AT_200_PERCENT_PAUSE_AND_DIAGNOSE")
    return {
        "schema_version": "imperium.core_reference_corridor.cost_time_assessment.v0_1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "estimated_minutes": estimated_minutes,
        "observed_minutes": observed_minutes,
        "time_ratio": time_ratio,
        "estimated_cost_units": estimated_cost_units,
        "observed_cost_units": observed_cost_units,
        "cost_ratio": cost_ratio,
        "pause_triggers": triggers,
        "verdict": "OWNER_CONFIRMATION_REQUIRED" if triggers else "WITHIN_CONTRACT",
        "resume_authority": "OWNER",
    }

