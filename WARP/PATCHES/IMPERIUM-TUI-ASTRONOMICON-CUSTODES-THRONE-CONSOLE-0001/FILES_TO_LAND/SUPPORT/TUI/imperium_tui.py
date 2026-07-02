#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ACTIONS_FILE = Path("SUPPORT/TUI/IMPERIUM_TUI_ACTIONS_V0_1.json")
LOG_DIR = Path("SUPPORT/TUI/LOGS")
RECEIPT_DIR = Path("SUPPORT/TUI/RECEIPTS")
REPORT_DIR = Path("SUPPORT/TUI/REPORTS")

def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def file_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def safe_id(text: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_") or "action"

def print_line(text: str = "", sink=None):
    print(text, flush=True)
    if sink is not None:
        sink.write(text + "\n")
        sink.flush()

def git_short(repo: Path, args: List[str]) -> str:
    try:
        p = subprocess.run(["git"] + args, cwd=str(repo), capture_output=True, text=True, timeout=30)
        return (p.stdout or p.stderr or "").strip()
    except Exception as e:
        return f"git error: {e}"

def rel(repo: Path, p: str) -> Path:
    return repo / p

def read_summary(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    return data if isinstance(data, dict) else {}

def table_pairs(title: str, pairs: List[tuple[str, Any]], sink):
    print_line("", sink)
    print_line(f"### {title}", sink)
    for k, v in pairs:
        print_line(f"{k}: {v}", sink)

def internal_status(repo: Path, sink) -> int:
    print_line("СТАТУС ИМПЕРИУМА / АКВАРИУМ", sink)
    table_pairs("Git", [
        ("HEAD", git_short(repo, ["rev-parse", "--short", "HEAD"])),
        ("branch", git_short(repo, ["branch", "--show-current"])),
        ("status", git_short(repo, ["status", "--short"]) or "clean"),
    ], sink)

    throne = read_summary(repo / "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json")
    custodes = read_summary(repo / "ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json")
    rb = read_summary(repo / "ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json")
    stage = read_summary(repo / "ORGANS/THRONE/REPORTS/ORGAN_ASSEMBLY_STAGE_SCORING_SUMMARY_V0_1.json")

    table_pairs("Astronomicon / Custodes / Throne", [
        ("Custodes verdict", custodes.get("verdict")),
        ("Custodes score", custodes.get("custodes_validation_score")),
        ("Custodes indictments", len(custodes.get("indictments", [])) if isinstance(custodes.get("indictments"), list) else custodes.get("indictments")),
        ("Astronomicon red local", rb.get("red_local_hardening_score")),
        ("Astronomicon blue local", rb.get("blue_local_hardening_score")),
        ("Throne verdict", throne.get("verdict")),
        ("Crown truth state", throne.get("crown_order_truth_state")),
        ("Astronomicon crown order", throne.get("astronomicon_crown_order_score")),
        ("Throne self-validation", throne.get("throne_self_validation_score")),
        ("Astronomicon assembled", throne.get("astronomicon_assembled_score")),
    ], sink)

    scores = stage.get("scores", {}) if isinstance(stage.get("scores"), dict) else {}
    table_pairs("Great Nine stage scores", [
        ("profile_baseline_score", scores.get("profile_baseline_score")),
        ("duty_defined_score", scores.get("duty_defined_score")),
        ("assembly_target_defined_score", scores.get("assembly_target_defined_score")),
        ("red_team_score", scores.get("red_team_score")),
        ("blue_team_score", scores.get("blue_team_score")),
        ("organ_truth_maturity_score", scores.get("organ_truth_maturity_score")),
        ("organ_assembled_score", scores.get("organ_assembled_score")),
    ], sink)
    return 0

def internal_throne_readout(repo: Path, sink) -> int:
    data = read_summary(repo / "ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json")
    if not data:
        print_line("Нет THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json", sink)
        return 2
    table_pairs("Трон: последний Crown-приговор по Астрономикону", [
        ("verdict", data.get("verdict")),
        ("truth_state", data.get("crown_order_truth_state")),
        ("gate_count", data.get("gate_count")),
        ("gate_pass_count", data.get("gate_pass_count")),
        ("astronomicon_crown_order_score", data.get("astronomicon_crown_order_score")),
        ("astronomicon_crown_gate_score", data.get("astronomicon_crown_gate_score")),
        ("astronomicon_red_team_crown_score", data.get("astronomicon_red_team_crown_score")),
        ("astronomicon_blue_team_crown_score", data.get("astronomicon_blue_team_crown_score")),
        ("throne_self_validation_score", data.get("throne_self_validation_score")),
        ("external_witness_for_throne_score", data.get("external_witness_for_throne_score")),
        ("astronomicon_assembled_score", data.get("astronomicon_assembled_score")),
    ], sink)
    print_line("", sink)
    print_line("Gates:", sink)
    for g in data.get("gates", []):
        print_line(f"- {g.get('status')} | {g.get('gate_id')} | score={g.get('score')} | evidence={g.get('evidence')}", sink)
    print_line("", sink)
    print_line("Not claimed:", sink)
    for x in data.get("not_claimed", []):
        print_line(f"- {x}", sink)
    return 0

def internal_custodes_readout(repo: Path, sink) -> int:
    data = read_summary(repo / "ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json")
    if not data:
        print_line("Нет CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json", sink)
        return 2
    table_pairs("Кустодес: прокурорский docket по Астрономикону", [
        ("verdict", data.get("verdict")),
        ("target_organ", data.get("target_organ")),
        ("identity_score", data.get("identity_score")),
        ("capability_evidence_score", data.get("capability_evidence_score")),
        ("validator_working_score", data.get("validator_working_score")),
        ("boundary_honesty_score", data.get("boundary_honesty_score")),
        ("red_blue_truth_score", data.get("red_blue_truth_score")),
        ("evidence_chain_score", data.get("evidence_chain_score")),
        ("custodes_validation_score", data.get("custodes_validation_score")),
        ("throne_confirmation_score", data.get("throne_confirmation_score")),
    ], sink)
    print_line("", sink)
    print_line("Indictments:", sink)
    indictments = data.get("indictments", [])
    if indictments:
        for x in indictments:
            print_line(f"- {x}", sink)
    else:
        print_line("- none", sink)
    print_line("", sink)
    print_line("Validators tested:", sink)
    for v in data.get("validators_tested", []):
        print_line(f"- {v.get('status')} | {v.get('path')} | {v.get('verdict')} | exit={v.get('exit_code')}", sink)
    return 0

def internal_score_guidance(repo: Path, sink) -> int:
    print_line("ПОДСКАЗКА: обновление цифр после цикла", sink)
    print_line("", sink)
    print_line("Эта функция ничего не запускает автоматически. Она показывает честный следующий refresh-контур:", sink)
    print_line("", sink)
    print_line("pwsh WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-REFRESH-0001/RUN_IMPERIUM_POPULATION_CENSUS_REFRESH.ps1", sink)
    print_line("pwsh WARP/PATCHES/THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001/RUN_THRONE_TARGET_GAP_ORGAN_IMPLEMENTATION_SPLIT.ps1", sink)
    print_line("pwsh WARP/PATCHES/THRONE-ORGAN-ASSEMBLY-STAGE-SCORING-INTEGRATION-0001/RUN_ORGAN_ASSEMBLY_STAGE_SCORING.ps1", sink)
    print_line("", sink)
    print_line("После них в TUI смотри: Статус Империума и рабочей ветки.", sink)
    return 0

def run_external(repo: Path, action: Dict[str, Any], sink) -> int:
    cmd = list(action.get("command", []))
    if not cmd:
        print_line("У действия нет command.", sink)
        return 2

    # Prevent forbidden git operations in this TUI layer.
    joined = " ".join(cmd).lower()
    for bad in ["git commit", "git push"]:
        if bad in joined:
            print_line(f"ЗАПРЕЩЕНО TUI: {bad}", sink)
            return 2

    print_line("АКВАРИУМ ВЫЗОВА", sink)
    print_line(f"Действие: {action.get('ru_label')}", sink)
    print_line(f"Описание: {action.get('ru_description')}", sink)
    print_line("Команда:", sink)
    print_line("  " + " ".join(cmd), sink)
    print_line("", sink)
    print_line("----- terminal output begin -----", sink)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.Popen(cmd, cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env)
    assert p.stdout is not None
    for line in p.stdout:
        print_line(line.rstrip("\n"), sink)
    code = p.wait()

    print_line("----- terminal output end -----", sink)
    print_line(f"exit_code: {code}", sink)
    return code

def run_action(repo: Path, action_id: str) -> int:
    data = load_json(repo / ACTIONS_FILE)
    if not isinstance(data, dict):
        print(f"Не найден manifest TUI: {ACTIONS_FILE}")
        return 2
    action = next((a for a in data.get("actions", []) if a.get("id") == action_id), None)
    if not action:
        print(f"Неизвестное действие: {action_id}")
        return 2
    if not action.get("aquarium_log_required"):
        print(f"Действие без aquarium_log_required запрещено: {action_id}")
        return 2

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = repo / LOG_DIR / f"{file_stamp()}_{safe_id(action_id)}.log"
    receipt_path = repo / RECEIPT_DIR / f"{file_stamp()}_{safe_id(action_id)}_receipt.json"

    with log_path.open("w", encoding="utf-8") as sink:
        print_line("============================================================", sink)
        print_line("IMPERIUM TUI / АКВАРИУМ РАБОТЫ", sink)
        print_line("============================================================", sink)
        print_line(f"generated_at_utc: {utc_stamp()}", sink)
        print_line(f"repo: {repo}", sink)
        print_line(f"action_id: {action_id}", sink)
        print_line(f"label: {action.get('ru_label')}", sink)
        print_line(f"mutates_repo: {action.get('mutates_repo')}", sink)
        print_line("============================================================", sink)
        print_line("", sink)

        if action_id == "status":
            code = internal_status(repo, sink)
        elif action_id == "throne-readout":
            code = internal_throne_readout(repo, sink)
        elif action_id == "custodes-readout":
            code = internal_custodes_readout(repo, sink)
        elif action_id == "score-refresh-guidance":
            code = internal_score_guidance(repo, sink)
        elif action.get("kind") == "external_command":
            code = run_external(repo, action, sink)
        else:
            print_line(f"Неподдержанный тип действия: {action.get('kind')}", sink)
            code = 2

        print_line("", sink)
        print_line("============================================================", sink)
        print_line(f"ACTION EXIT CODE: {code}", sink)
        print_line("============================================================", sink)

    receipt = {
        "receipt_id": "receipt.support_tui.action.v0_1",
        "generated_at_utc": utc_stamp(),
        "action_id": action_id,
        "label": action.get("ru_label"),
        "exit_code": code,
        "log": str(log_path.relative_to(repo)).replace("\\", "/"),
        "mutates_repo": action.get("mutates_repo"),
        "aquarium_log_required": True
    }
    write_json(receipt_path, receipt)
    print("")
    print(f"Лог аквариума: {log_path.relative_to(repo)}")
    print(f"Receipt TUI: {receipt_path.relative_to(repo)}")
    return code

def list_actions(repo: Path):
    data = load_json(repo / ACTIONS_FILE)
    if not isinstance(data, dict):
        print(f"Не найден manifest TUI: {ACTIONS_FILE}")
        return 2
    for a in data.get("actions", []):
        print(f"{a.get('id')}\t{a.get('ru_label')}\tmutates={a.get('mutates_repo')}")
    return 0

def menu(repo: Path) -> int:
    data = load_json(repo / ACTIONS_FILE)
    if not isinstance(data, dict):
        print(f"Не найден manifest TUI: {ACTIONS_FILE}")
        return 2
    actions = data.get("actions", [])
    while True:
        print("")
        print("============================================================")
        print("ИМПЕРИУМ TUI — АСТРОНОМИКОН / КУСТОДЕС / ТРОН")
        print("============================================================")
        print("Каждая функция показывает аквариум работы и пишет лог.")
        print("")
        for i, a in enumerate(actions, start=1):
            mut = "пишет receipts/reports" if a.get("mutates_repo") else "только читает"
            print(f"{i}. {a.get('ru_label')} [{mut}]")
            print(f"   {a.get('ru_description')}")
        print("0. Выход")
        choice = input("\nВыбор: ").strip()
        if choice in ["0", "q", "quit", "exit"]:
            return 0
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(actions):
            print("Не понял выбор.")
            continue
        action = actions[int(choice) - 1]
        code = run_action(repo, action["id"])
        input("\nНажми Enter, чтобы вернуться в меню...")
        if code != 0:
            print(f"Действие завершилось с code={code}. Смотри лог.")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--list-actions", action="store_true")
    ap.add_argument("--action")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    if args.list_actions:
        return list_actions(repo)
    if args.action:
        return run_action(repo, args.action)
    return menu(repo)

if __name__ == "__main__":
    raise SystemExit(main())
