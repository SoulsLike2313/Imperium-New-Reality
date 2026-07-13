"""Phase 2 negative-proof orchestration and red/green mutation receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .negative_observer import OBSERVER_ID, OBSERVER_VERSION, observe_scenario
from .registry import atomic_write_json, sha256_file
from .root_resolver import resolve_repository_context


TASK_ID = "IMPERIUM_CORE_TRUTH_HARDENING_0002"
WARP_ID = "WARP-CORE-REFERENCE-0001"
BASE_HEAD = "281c3a7c8463de7fb64473929fe0ed975f99f595"
REPORT_RELATIVE = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002")
CATALOG_RELATIVE = Path("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/contracts/NEGATIVE_SCENARIO_EXPECTATIONS.json")
VALIDATOR_RELATIVE = Path("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/negative_proof_validator.py")
OBSERVER_RELATIVE = Path("ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/negative_observer.py")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_hash(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("receipt_hash", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    value["receipt_hash"] = _canonical_hash(value)
    atomic_write_json(path, value)


def _relative(path: Path, report: Path) -> str:
    return path.resolve().relative_to(report.resolve()).as_posix()


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], shell=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def _truth(reality: Path, warp: Path) -> dict[str, Any]:
    return {
        "reality_head": _git(reality, "rev-parse", "HEAD"),
        "reality_origin_master": _git(reality, "rev-parse", "origin/master"),
        "reality_status": _git(reality, "status", "--porcelain=v1", "--untracked-files=all").splitlines(),
        "warp_head": _git(warp, "rev-parse", "HEAD"),
        "warp_status": _git(warp, "status", "--porcelain=v1", "--untracked-files=all").splitlines(),
    }


def _load_catalog(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("scenarios") if isinstance(data, dict) else None
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("expected catalog must contain exactly 20 scenarios")
    ids = [row.get("scenario_id") for row in rows if isinstance(row, dict)]
    orders = [row.get("order") for row in rows if isinstance(row, dict)]
    if len(ids) != 20 or len(set(ids)) != 20 or orders != list(range(1, 21)):
        raise ValueError("expected catalog ordering or ids are invalid")
    if any(not isinstance(row.get("expected_verdict"), str) for row in rows):
        raise ValueError("every scenario needs an expected verdict")
    return rows


def _invoke_validator(
    validator: Path,
    receipt: Path,
    report: Path,
    *,
    task_id: str,
    warp_id: str,
    base_head: str,
    mode: str,
) -> dict[str, Any]:
    argv = [sys.executable, str(validator), "--receipt", str(receipt), "--report-root", str(report), "--task-id", task_id, "--warp-id", warp_id, "--base-head", base_head, "--mode", mode]
    started = _utc_now()
    result = subprocess.run(argv, cwd=str(report.parent.parent.parent.parent), shell=False, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    try:
        parsed = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"validator emitted invalid JSON: {result.stdout!r} {result.stderr!r}") from exc
    wrapper = {
        "schema_version": "imperium.core_reference_corridor.negative_validator_execution.v1",
        "scenario_id": parsed.get("scenario_id"),
        "mode": mode,
        "started_at_utc": started,
        "ended_at_utc": _utc_now(),
        "exact_argv": argv,
        "python_executable": str(Path(sys.executable).resolve()),
        "python_sha256": sha256_file(Path(sys.executable).resolve()),
        "validator_path": str(validator.resolve()),
        "validator_sha256": sha256_file(validator),
        "exit_code": result.returncode,
        "stdout_sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode("utf-8")).hexdigest(),
        "validator_result": parsed,
    }
    wrapper["receipt_hash"] = _canonical_hash(wrapper)
    return wrapper


def _observation_receipt(
    report: Path,
    path: Path,
    *,
    scenario_id: str,
    observations: dict[str, Any],
    observer_path: Path,
) -> dict[str, Any]:
    receipt = {
        "schema_version": "imperium.core_reference_corridor.negative_observation_receipt.v1",
        "scenario_id": scenario_id,
        "fixture_id": observations["fixture_id"],
        "observed_at_utc": _utc_now(),
        "observer": {"id": OBSERVER_ID, "version": OBSERVER_VERSION, "path": str(observer_path.resolve()), "sha256": sha256_file(observer_path)},
        "observations": observations,
    }
    _write_json(path, receipt)
    return receipt


def _scenario_template(
    *,
    entry: dict[str, Any],
    observations: dict[str, Any],
    observation_path: Path,
    report: Path,
    catalog: Path,
    validator: Path,
    task_id: str,
    warp_id: str,
    base_head: str,
) -> dict[str, Any]:
    return {
        "schema_version": "imperium.core_reference_corridor.negative_scenario_receipt.v1",
        "task_id": task_id,
        "warp_id": warp_id,
        "base_head": base_head,
        "scenario_id": entry["scenario_id"],
        "fixture_id": observations["fixture_id"],
        "expected_source": {"path": str(catalog.resolve()), "sha256": sha256_file(catalog), "entry_sha256": hashlib.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()},
        "expected_verdict": entry["expected_verdict"],
        "observations": observations,
        "observation_evidence_refs": [{"path": _relative(observation_path, report), "sha256": sha256_file(observation_path)}],
        "validator": {"id": "negative_proof_observation_validator_v1", "version": "1.0.0", "path": str(validator.resolve()), "sha256": sha256_file(validator)},
        "actual_source": "INDEPENDENT_VALIDATOR_SUBPROCESS_FROM_MEASURED_OBSERVATIONS",
    }


def _derive_and_validate(
    scenario: dict[str, Any],
    scenario_path: Path,
    validation_path: Path,
    *,
    validator: Path,
    report: Path,
    task_id: str,
    warp_id: str,
    base_head: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    scenario.pop("actual_verdict", None)
    _write_json(scenario_path, scenario)
    derived = _invoke_validator(validator, scenario_path, report, task_id=task_id, warp_id=warp_id, base_head=base_head, mode="derive")
    scenario["actual_verdict"] = derived["validator_result"]["actual_verdict"]
    scenario["actual_derivation"] = {"mode": "derive", "validator_result_hash": derived["validator_result"]["receipt_hash"], "exit_code": derived["exit_code"]}
    _write_json(scenario_path, scenario)
    validated = _invoke_validator(validator, scenario_path, report, task_id=task_id, warp_id=warp_id, base_head=base_head, mode="validate")
    _write_json(validation_path, validated)
    return scenario, validated


def _green_copy(
    canonical: Path,
    destination: Path,
    validation_path: Path,
    *,
    validator: Path,
    report: Path,
    task_id: str,
    warp_id: str,
    base_head: str,
) -> dict[str, Any]:
    value = json.loads(canonical.read_text(encoding="utf-8"))
    _write_json(destination, value)
    validated = _invoke_validator(validator, destination, report, task_id=task_id, warp_id=warp_id, base_head=base_head, mode="validate")
    _write_json(validation_path, validated)
    return validated


def _mutation_summary(path: Path, *, mutation_id: str, red_scenario: Path, red_validation: Path, green_scenario: Path, green_validation: Path) -> dict[str, Any]:
    red = json.loads(red_validation.read_text(encoding="utf-8"))
    green = json.loads(green_validation.read_text(encoding="utf-8"))
    red_result, green_result = red["validator_result"], green["validator_result"]
    value = {
        "schema_version": "imperium.core_reference_corridor.negative_mutation_receipt.v1",
        "mutation_id": mutation_id,
        "red": {"scenario_receipt": red_scenario.name, "scenario_sha256": sha256_file(red_scenario), "validation_receipt": red_validation.name, "validation_sha256": sha256_file(red_validation), "actual_verdict": red_result["actual_verdict"], "suite_verdict": red_result["validation_verdict"], "exit_code": red["exit_code"]},
        "green_after_restore": {"scenario_receipt": green_scenario.name, "scenario_sha256": sha256_file(green_scenario), "validation_receipt": green_validation.name, "validation_sha256": sha256_file(green_validation), "actual_verdict": green_result["actual_verdict"], "suite_verdict": green_result["validation_verdict"], "exit_code": green["exit_code"]},
    }
    value["red_detected"] = value["red"]["suite_verdict"] == "BLOCK" and value["red"]["exit_code"] != 0
    value["green_restored"] = value["green_after_restore"]["suite_verdict"] == "PASS" and value["green_after_restore"]["exit_code"] == 0
    value["verdict"] = "RED_DETECTED_GREEN_RESTORED" if value["red_detected"] and value["green_restored"] else "BLOCK"
    _write_json(path, value)
    return value


def _run_mutations(
    *,
    report: Path,
    catalog: Path,
    entries: dict[str, dict[str, Any]],
    canonical: dict[str, Path],
    validator: Path,
    observer: Path,
    boundary: Path,
    reality: Path,
    warp: Path,
    task_id: str,
    warp_id: str,
    base_head: str,
) -> list[dict[str, Any]]:
    mutations_root = report / "PHASE_2_MUTATIONS"
    rows: list[dict[str, Any]] = []

    organ_root = mutations_root / "01_broken_organ_verdict_calculation"
    organ_root.mkdir(parents=True, exist_ok=True)
    mutant = organ_root / "MUTANT_NEGATIVE_PROOF_VALIDATOR.py"
    source = validator.read_text(encoding="utf-8")
    target = 'return "BLOCK_MISSING_ORGAN_PROVEN"  # MUTATION_TARGET_ORGAN_VERDICT'
    if source.count(target) != 1:
        raise RuntimeError("organ verdict mutation target is not unique")
    mutant.write_text(source.replace(target, 'return "PASS_PROVEN"  # MUTATION_TARGET_ORGAN_VERDICT'), encoding="utf-8", newline="\n")
    red_scenario = json.loads(canonical["missing_organ"].read_text(encoding="utf-8"))
    red_scenario["validator"] = {"id": "negative_proof_observation_validator_v1", "version": "1.0.0", "path": str(mutant.resolve()), "sha256": sha256_file(mutant)}
    red_path, red_validation = organ_root / "RED_SCENARIO_RECEIPT.json", organ_root / "RED_RECEIPT.json"
    _derive_and_validate(red_scenario, red_path, red_validation, validator=mutant, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    green_path, green_validation = organ_root / "GREEN_SCENARIO_RECEIPT.json", organ_root / "GREEN_RECEIPT.json"
    _green_copy(canonical["missing_organ"], green_path, green_validation, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    rows.append(_mutation_summary(organ_root / "MUTATION_RECEIPT.json", mutation_id="broken_organ_verdict_calculation", red_scenario=red_path, red_validation=red_validation, green_scenario=green_path, green_validation=green_validation))

    unknown_root = mutations_root / "02_allow_unknown_capability"
    unknown_root.mkdir(parents=True, exist_ok=True)
    observations = observe_scenario(scenario_id="unregistered_capability", fixture_boundary=boundary, host_reality=reality, host_warp=warp, bindings={"task_id": task_id, "warp_id": warp_id, "base_head": base_head}, mutation="allow_unknown_capability")
    observation_path = unknown_root / "RED_OBSERVATION_RECEIPT.json"
    _observation_receipt(report, observation_path, scenario_id="unregistered_capability", observations=observations, observer_path=observer)
    red_scenario = _scenario_template(entry=entries["unregistered_capability"], observations=observations, observation_path=observation_path, report=report, catalog=catalog, validator=validator, task_id=task_id, warp_id=warp_id, base_head=base_head)
    red_path, red_validation = unknown_root / "RED_SCENARIO_RECEIPT.json", unknown_root / "RED_RECEIPT.json"
    _derive_and_validate(red_scenario, red_path, red_validation, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    green_path, green_validation = unknown_root / "GREEN_SCENARIO_RECEIPT.json", unknown_root / "GREEN_RECEIPT.json"
    _green_copy(canonical["unregistered_capability"], green_path, green_validation, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    rows.append(_mutation_summary(unknown_root / "MUTATION_RECEIPT.json", mutation_id="allow_unknown_capability", red_scenario=red_path, red_validation=red_validation, green_scenario=green_path, green_validation=green_validation))

    hash_root = mutations_root / "03_substitute_evidence_hash"
    hash_root.mkdir(parents=True, exist_ok=True)
    red_scenario = json.loads(canonical["evidence_tampering"].read_text(encoding="utf-8"))
    red_scenario["observation_evidence_refs"][0]["sha256"] = "f" * 64
    red_path, red_validation = hash_root / "RED_SCENARIO_RECEIPT.json", hash_root / "RED_RECEIPT.json"
    _derive_and_validate(red_scenario, red_path, red_validation, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    green_path, green_validation = hash_root / "GREEN_SCENARIO_RECEIPT.json", hash_root / "GREEN_RECEIPT.json"
    _green_copy(canonical["evidence_tampering"], green_path, green_validation, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
    rows.append(_mutation_summary(hash_root / "MUTATION_RECEIPT.json", mutation_id="substitute_evidence_hash", red_scenario=red_path, red_validation=red_validation, green_scenario=green_path, green_validation=green_validation))
    return rows


def run_negative_suite(
    *,
    report: Path,
    worktree: Path,
    reality: Path,
    task_id: str = TASK_ID,
    warp_id: str = WARP_ID,
    base_head: str = BASE_HEAD,
) -> dict[str, Any]:
    report, worktree, reality = report.resolve(), worktree.resolve(), reality.resolve()
    report.mkdir(parents=True, exist_ok=True)
    catalog, validator, observer = worktree / CATALOG_RELATIVE, worktree / VALIDATOR_RELATIVE, worktree / OBSERVER_RELATIVE
    entries_list = _load_catalog(catalog)
    entries = {row["scenario_id"]: row for row in entries_list}
    suite_before = _truth(reality, worktree)
    scenario_rows: list[dict[str, Any]] = []
    canonical: dict[str, Path] = {}
    with tempfile.TemporaryDirectory(prefix="imperium-phase2-fixtures-") as temporary:
        boundary = Path(temporary).resolve()
        for entry in entries_list:
            scenario_id, order = entry["scenario_id"], entry["order"]
            observations = observe_scenario(scenario_id=scenario_id, fixture_boundary=boundary, host_reality=reality, host_warp=worktree, bindings={"task_id": task_id, "warp_id": warp_id, "base_head": base_head})
            observation_path = report / "PHASE_2_OBSERVATIONS" / f"{order:02d}_{scenario_id}.json"
            observation_path.parent.mkdir(parents=True, exist_ok=True)
            _observation_receipt(report, observation_path, scenario_id=scenario_id, observations=observations, observer_path=observer)
            scenario_path = report / "PHASE_2_SCENARIOS" / f"{order:02d}_{scenario_id}.json"
            validation_path = report / "PHASE_2_SCENARIO_VALIDATIONS" / f"{order:02d}_{scenario_id}.json"
            scenario_path.parent.mkdir(parents=True, exist_ok=True)
            validation_path.parent.mkdir(parents=True, exist_ok=True)
            scenario = _scenario_template(entry=entry, observations=observations, observation_path=observation_path, report=report, catalog=catalog, validator=validator, task_id=task_id, warp_id=warp_id, base_head=base_head)
            scenario, validation = _derive_and_validate(scenario, scenario_path, validation_path, validator=validator, report=report, task_id=task_id, warp_id=warp_id, base_head=base_head)
            result = validation["validator_result"]
            canonical[scenario_id] = scenario_path
            scenario_rows.append({"order": order, "scenario_id": scenario_id, "expected_verdict": entry["expected_verdict"], "actual_verdict": scenario["actual_verdict"], "observation_receipt": _relative(observation_path, report), "observation_sha256": sha256_file(observation_path), "scenario_receipt": _relative(scenario_path, report), "scenario_sha256": sha256_file(scenario_path), "validation_receipt": _relative(validation_path, report), "validation_sha256": sha256_file(validation_path), "validator_exit_code": validation["exit_code"], "validation_verdict": result["validation_verdict"], "comparison_match": result["comparison_match"]})
        mutation_rows = _run_mutations(report=report, catalog=catalog, entries=entries, canonical=canonical, validator=validator, observer=observer, boundary=boundary, reality=reality, warp=worktree, task_id=task_id, warp_id=warp_id, base_head=base_head)
    suite_after = _truth(reality, worktree)
    reality_unchanged = suite_before["reality_head"] == suite_after["reality_head"] == suite_before["reality_origin_master"] == suite_after["reality_origin_master"] and suite_before["reality_status"] == suite_after["reality_status"] == []
    scenarios_pass = len(scenario_rows) == 20 and all(row["validation_verdict"] == "PASS" and row["validator_exit_code"] == 0 and row["comparison_match"] for row in scenario_rows)
    mutations_pass = len(mutation_rows) == 3 and all(row["red_detected"] and row["green_restored"] for row in mutation_rows)
    index = {
        "schema_version": "imperium.core_reference_corridor.negative_scenario_index.v1",
        "task_id": task_id,
        "warp_id": warp_id,
        "base_head": base_head,
        "generated_at_utc": _utc_now(),
        "expected_source": {"path": str(catalog.resolve()), "sha256": sha256_file(catalog)},
        "actual_source": {"path": str(validator.resolve()), "sha256": sha256_file(validator), "policy": "MEASURED_OBSERVATIONS_ONLY"},
        "source_separation": {"different_files": catalog.resolve() != validator.resolve(), "validator_imports_expectation_catalog": "NEGATIVE_SCENARIO_EXPECTATIONS" in validator.read_text(encoding="utf-8")},
        "observer": {"path": str(observer.resolve()), "sha256": sha256_file(observer), "assigns_verdicts": False},
        "scenario_count": len(scenario_rows),
        "scenarios": scenario_rows,
        "mutation_count": len(mutation_rows),
        "mutations": mutation_rows,
        "reality": {"before": suite_before, "after": suite_after, "unchanged_and_clean": reality_unchanged},
        "phase_acceptance": "NEGATIVE_PROOF_HARDENING_PASS" if scenarios_pass and mutations_pass and reality_unchanged else "BLOCK",
        "campaign_verdict": "TRUTH_HARDENING_PARTIAL_NOT_READY",
        "phase_3_started": False,
    }
    _write_json(report / "NEGATIVE_SCENARIO_INDEX.json", index)
    lines = ["# Phase 2 Negative Scenario Index", "", f"- Phase acceptance: `{index['phase_acceptance']}`", f"- Scenarios: `{len(scenario_rows)}/20` observation-derived validations passed", f"- Mutations: `{len(mutation_rows)}/3` red detected and green restored", f"- Reality unchanged and clean: `{str(reality_unchanged).lower()}`", "- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`", "- Phase 3: `NOT_STARTED`", "", "## Scenario receipts", ""]
    lines.extend(f"- `{row['order']:02d} {row['scenario_id']}`: `{row['actual_verdict']}` — `{row['validation_verdict']}`" for row in scenario_rows)
    (report / "NEGATIVE_SCENARIO_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return index


def _junit(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    return {"path": path.name, "sha256": sha256_file(path), "tests": sum(int(item.attrib.get("tests", 0)) for item in suites), "failures": sum(int(item.attrib.get("failures", 0)) for item in suites), "errors": sum(int(item.attrib.get("errors", 0)) for item in suites), "skipped": sum(int(item.attrib.get("skipped", 0)) for item in suites)}


def write_checkpoint(*, report: Path, worktree: Path, reality: Path, targeted: Path, regression: Path) -> dict[str, Any]:
    index_path = report / "NEGATIVE_SCENARIO_INDEX.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    targeted_result, regression_result = _junit(targeted), _junit(regression)
    tests_pass = all(item["tests"] > 0 and item["failures"] == item["errors"] == item["skipped"] == 0 for item in (targeted_result, regression_result))
    reality_truth = _truth(reality, worktree)
    reality_ok = reality_truth["reality_head"] == reality_truth["reality_origin_master"] == BASE_HEAD and reality_truth["reality_status"] == []
    phase_pass = index.get("phase_acceptance") == "NEGATIVE_PROOF_HARDENING_PASS" and tests_pass and reality_ok
    changed = _git(worktree, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    checkpoint = {
        "schema_version": "imperium.core_reference_corridor.phase_receipt.v1",
        "task_id": TASK_ID,
        "phase": 2,
        "PHASE_VERDICT": "NEGATIVE_PROOF_HARDENING_PASS" if phase_pass else "BLOCK",
        "EXPECTED_ACTUAL_SEPARATION": index["source_separation"],
        "SCENARIOS": {"required": 20, "passed": sum(row["validation_verdict"] == "PASS" for row in index["scenarios"]), "index": "NEGATIVE_SCENARIO_INDEX.json", "index_sha256": sha256_file(index_path)},
        "MUTATION_TESTS": {"required": 3, "red_detected_green_restored": sum(row["red_detected"] and row["green_restored"] for row in index["mutations"]), "mutations": index["mutations"]},
        "TESTS": {"targeted": targeted_result, "regression": regression_result},
        "REALITY": {**reality_truth, "unchanged_and_clean": reality_ok},
        "FILES_CHANGED": changed,
        "KNOWN_GAPS": ["Phase 3 and all later hardening phases are not started.", "The overall campaign remains partial until later phase checkpoints and independent revalidation."],
        "campaign_verdict": "TRUTH_HARDENING_PARTIAL_NOT_READY",
        "phase_3_started": False,
    }
    _write_json(report / "NEGATIVE_PROOF_TRUTH.json", checkpoint)
    md = ["# Phase 2 — Negative Proof Truth", "", f"- Phase verdict: `{checkpoint['PHASE_VERDICT']}`", f"- Scenarios: `{checkpoint['SCENARIOS']['passed']}/20`", f"- Mutation tests: `{checkpoint['MUTATION_TESTS']['red_detected_green_restored']}/3` red→green", f"- Targeted tests: `{targeted_result['tests']} passed`", f"- Regression tests: `{regression_result['tests']} passed`", f"- Reality/master: `{reality_truth['reality_head']}`, unchanged and clean", "- Campaign verdict: `TRUTH_HARDENING_PARTIAL_NOT_READY`", "- Phase 3: `NOT_STARTED`", ""]
    (report / "NEGATIVE_PROOF_TRUTH.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    return checkpoint


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--checkpoint", action="store_true")
    parser.add_argument("--targeted", type=Path)
    parser.add_argument("--regression", type=Path)
    args = parser.parse_args(argv)
    context = resolve_repository_context(".")
    report = Path(context.worktree_root) / REPORT_RELATIVE
    if args.checkpoint:
        if not args.targeted or not args.regression:
            parser.error("--checkpoint requires --targeted and --regression")
        result = write_checkpoint(report=report, worktree=Path(context.worktree_root), reality=Path(context.reality_root), targeted=args.targeted.resolve(), regression=args.regression.resolve())
    elif args.write:
        result = run_negative_suite(report=report, worktree=Path(context.worktree_root), reality=Path(context.reality_root))
    else:
        parser.error("choose --write or --checkpoint")
    print(json.dumps({"phase_verdict": result.get("PHASE_VERDICT", result.get("phase_acceptance")), "report": str(report)}, sort_keys=True))
    return 0 if result.get("PHASE_VERDICT", result.get("phase_acceptance")) == "NEGATIVE_PROOF_HARDENING_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
