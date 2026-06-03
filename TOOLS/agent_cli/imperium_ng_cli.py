#!/usr/bin/env python3
"""IMPERIUM New Generation CLI base runner (first 3 agents)."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent

FIRST_THREE = {
    "ADMINISTRATUM_AGENT",
    "CUSTODES_AGENT",
    "MECHANICUS_AGENT",
}

CANDIDATE_OSS_TOOLS = [
    "uv",
    "Ruff",
    "pytest",
    "jsonschema",
    "ripgrep",
    "jq/yq",
    "SQLite",
    "DuckDB",
    "Datasette",
    "Playwright",
    "Lighthouse CI",
    "bandit",
    "pip-audit",
    "gitleaks",
    "Semgrep CE",
    "tree-sitter",
    "Repomix scoped exporter",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return f"{prefix}_{hashlib.sha1(payload).hexdigest()[:12]}"


def normalize_agent_id(agent: str) -> str:
    agent = agent.strip().upper()
    if not agent.endswith("_AGENT"):
        agent += "_AGENT"
    return agent


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def append_jsonl(path: Path, item: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=False) + "\n")


def agent_root(agent_id: str) -> Path:
    return ROOT / "ORGAN_AGENTS" / agent_id


def manifest_for(agent_id: str) -> Dict[str, Any]:
    p = agent_root(agent_id) / "agent_manifest.json"
    if not p.exists():
        raise FileNotFoundError(f"Agent manifest not found: {p}")
    return load_json(p)


def memory_paths(agent_id: str) -> Dict[str, Path]:
    base = agent_root(agent_id) / "memory"
    return {
        "short_term": base / "short_term.jsonl",
        "working": base / "working_memory.json",
        "correction": base / "correction_memory.jsonl",
        "approved": base / "approved_learning.jsonl",
        "rejected": base / "rejected_learning.jsonl",
    }


def memory_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as fh:
        return sum(1 for _ in fh)


def update_agent_memory(agent_id: str, memory_event: Dict[str, Any]) -> None:
    paths = memory_paths(agent_id)
    append_jsonl(paths["short_term"], memory_event)
    working = {}
    if paths["working"].exists():
        working = load_json(paths["working"])
    working["last_event"] = memory_event
    working["last_updated_utc"] = now_utc()
    working["short_term_count"] = memory_line_count(paths["short_term"])
    write_json(paths["working"], working)


def append_ledger_event(event_type: str, agent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event = {
        "event_id": stable_id("evt", event_type, agent, payload.get("task_id", "NA"), now_utc()),
        "timestamp_utc": now_utc(),
        "event_type": event_type,
        "agent": agent,
        "payload": payload,
    }
    append_jsonl(ROOT / "LEDGER" / "brain_event_ledger.jsonl", event)
    return event


def update_index_list(index_path: Path, key: str, item: Dict[str, Any]) -> None:
    if index_path.exists():
        data = load_json(index_path)
    else:
        data = {key: []}
    data.setdefault(key, [])
    data[key].append(item)
    write_json(index_path, data)


def is_path_under_new_generation(path_text: str) -> Tuple[bool, str]:
    p = Path(path_text)
    if p.is_absolute():
        abs_path = p.resolve()
    else:
        abs_path = (REPO_ROOT / p).resolve()
    inside = (abs_path == ROOT) or (ROOT in abs_path.parents)
    return inside, str(abs_path)


def custodes_verdict_for_paths(question: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    payload = question.get("payload", {})
    proposed = payload.get("proposed_paths", [])
    if isinstance(proposed, str):
        proposed = [proposed]
    operation = str(payload.get("operation", "write")).lower()
    read_only = bool(question.get("read_only", False))

    findings: List[Dict[str, Any]] = []
    has_external_write = False
    has_external_read = False
    has_core_impact = False

    for path_text in proposed:
        inside, resolved = is_path_under_new_generation(path_text)
        findings.append(
            {
                "path": path_text,
                "resolved_path": resolved,
                "inside_new_generation": inside,
                "operation": operation,
                "read_only": read_only,
            }
        )
        if not inside and operation in {"write", "create", "modify", "delete"} and not read_only:
            has_external_write = True
        if not inside and (operation == "read" or read_only):
            has_external_read = True
        if inside and "/CORE/" in resolved.replace("\\", "/"):
            has_core_impact = True

    action = question.get("action", "")
    if has_external_write:
        return "BLOCK_CORE_ACCESS", findings
    if action == "CHECK_CORE_IMPACT" and has_core_impact:
        return "ADMIT_WITH_GATES", findings
    if has_external_read:
        return "ADMIT_WITH_GATES", findings
    return "ADMIT", findings


def handle_custodes(question: Dict[str, Any]) -> Dict[str, Any]:
    action = question.get("action", "")
    if action not in {"FILTER_ZONE_ADMISSION", "CHECK_ALLOWED_PATHS", "CHECK_CORE_IMPACT"}:
        return {
            "verdict": "REQUEST_MORE_EVIDENCE",
            "summary": f"Unsupported action for CUSTODES_AGENT: {action}",
            "data": {"supported_actions": ["FILTER_ZONE_ADMISSION", "CHECK_ALLOWED_PATHS", "CHECK_CORE_IMPACT"]},
        }

    verdict, findings = custodes_verdict_for_paths(question)
    summary = {
        "ADMIT": "Path admission accepted.",
        "ADMIT_WITH_GATES": "Admitted with gates; external read/core impact detected.",
        "REJECT": "Rejected by admission rules.",
        "BLOCK_CORE_ACCESS": "Write outside IMPERIUM_NEW_GENERATION is blocked.",
        "REQUEST_MORE_EVIDENCE": "More evidence required.",
    }.get(verdict, "Custodes verdict produced.")

    return {
        "verdict": verdict,
        "summary": summary,
        "data": {
            "findings": findings,
            "policy": "No out-of-scope write allowed in first-stage base spine",
        },
    }


def candidate_tool_objects() -> List[Dict[str, Any]]:
    return [
        {
            "tool": t,
            "status": "CANDIDATE_ONLY",
            "installed": False,
            "canon_authority": False,
        }
        for t in CANDIDATE_OSS_TOOLS
    ]


def mechanicus_tool_match(task_text: str) -> List[str]:
    txt = task_text.lower()
    matched: List[str] = []
    if any(k in txt for k in ["test", "stress", "coverage"]):
        matched.append("pytest")
    if any(k in txt for k in ["schema", "json"]):
        matched.extend(["jsonschema", "jq/yq"])
    if any(k in txt for k in ["lint", "style"]):
        matched.append("Ruff")
    if any(k in txt for k in ["search", "scan"]):
        matched.append("ripgrep")
    if any(k in txt for k in ["query", "analytics", "table"]):
        matched.extend(["SQLite", "DuckDB"])
    if not matched:
        matched = ["uv", "Ruff", "pytest"]
    dedup: List[str] = []
    seen = set()
    for m in matched:
        if m not in seen:
            dedup.append(m)
            seen.add(m)
    return dedup


def handle_mechanicus(question: Dict[str, Any]) -> Dict[str, Any]:
    action = question.get("action", "")
    payload = question.get("payload", {})

    if action == "LIST_AVAILABLE_TOOLS":
        return {"verdict": "PASS", "summary": "Candidate tools listed.", "data": {"tools": candidate_tool_objects()}}

    if action == "MATCH_TOOLS_TO_TASK":
        task_text = str(payload.get("task_text", ""))
        matched = mechanicus_tool_match(task_text)
        return {
            "verdict": "PASS",
            "summary": "Tool candidates matched to task text.",
            "data": {"matched_candidates": matched, "policy": "candidate_only_no_install_in_this_stage"},
        }

    if action == "RECOMMEND_QUALITY_GATES":
        return {
            "verdict": "PASS",
            "summary": "Quality gate recommendations prepared.",
            "data": {
                "recommended_gates": [
                    "GATE-U00-GIT-TRUTH",
                    "GATE-U02-SCOPE-BOUNDARY",
                    "GATE-U04-EVIDENCE-RECEIPT",
                    "GATE-U09-NO-FAKE-GREEN",
                    "GATE-U12-REPORT-OUTPUT-BUDGET",
                ],
                "notes": "Recommendations only; no external tool installation.",
            },
        }

    if action == "REGISTER_TOOL_CANDIDATE":
        entry = {
            "tool": str(payload.get("tool", "UNKNOWN")),
            "reason": str(payload.get("reason", "No reason provided")),
            "status": "CANDIDATE_ONLY",
            "registered_at_utc": now_utc(),
        }
        reg_path = agent_root("MECHANICUS_AGENT") / "state" / "tool_candidates_registry.json"
        registry = {"candidates": []}
        if reg_path.exists():
            registry = load_json(reg_path)
        registry.setdefault("candidates", [])
        registry["candidates"].append(entry)
        write_json(reg_path, registry)
        return {"verdict": "PASS", "summary": "Tool candidate registered.", "data": entry}

    return {
        "verdict": "REQUEST_MORE_EVIDENCE",
        "summary": f"Unsupported action for MECHANICUS_AGENT: {action}",
        "data": {
            "supported_actions": [
                "LIST_AVAILABLE_TOOLS",
                "MATCH_TOOLS_TO_TASK",
                "RECOMMEND_QUALITY_GATES",
                "REGISTER_TOOL_CANDIDATE",
            ]
        },
    }


def handle_administratum(question: Dict[str, Any]) -> Dict[str, Any]:
    action = question.get("action", "")
    supported = [
        "CREATE_TASK_ENVELOPE",
        "CREATE_ROUTE_SHEET",
        "REGISTER_ORGAN_ANSWER",
        "REGISTER_RECEIPT",
        "BUILD_FINAL_ROUTE_REPORT",
    ]
    if action not in supported:
        return {
            "verdict": "REQUEST_MORE_EVIDENCE",
            "summary": f"Unsupported action for ADMINISTRATUM_AGENT: {action}",
            "data": {"supported_actions": supported},
        }
    return {
        "verdict": "PASS",
        "summary": f"Administratum action accepted: {action}",
        "data": {"action": action, "status": "delegated_to_route_pipeline"},
    }


def route_dispatch(question: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
    if agent_id == "CUSTODES_AGENT":
        return handle_custodes(question)
    if agent_id == "MECHANICUS_AGENT":
        return handle_mechanicus(question)
    if agent_id == "ADMINISTRATUM_AGENT":
        return handle_administratum(question)
    return {
        "verdict": "SKELETON_ONLY_NOT_IMPLEMENTED",
        "summary": f"{agent_id} is skeleton-only in this stage.",
        "data": {"status": "SKELETON_ONLY_NOT_IMPLEMENTED"},
    }


def answer_and_receipt_paths(answer_id: str, agent_id: str) -> Tuple[Path, Path, Path, Path]:
    answer_path = ROOT / "EXCHANGE" / "ORGAN_BUS" / "answers" / f"{answer_id}.json"
    receipt_path = ROOT / "EXCHANGE" / "ORGAN_BUS" / "receipts" / f"{answer_id}_receipt.json"
    outbox_path = agent_root(agent_id) / "outbox" / f"{answer_id}.json"
    agent_receipt_path = agent_root(agent_id) / "receipts" / f"{answer_id}_receipt.json"
    return answer_path, receipt_path, outbox_path, agent_receipt_path


def process_question(question: Dict[str, Any], forced_agent: str | None = None) -> Dict[str, Any]:
    question_id = str(question.get("question_id", "NO_QUESTION_ID"))
    task_id = str(question.get("task_id", "NO_TASK_ID"))
    action = str(question.get("action", "NO_ACTION"))
    target_agent = normalize_agent_id(forced_agent or question.get("target_agent", ""))
    manifest = manifest_for(target_agent)
    answer_id = stable_id("answer", question_id, target_agent, action)

    if manifest.get("status") == "SKELETON_ONLY_NOT_IMPLEMENTED":
        body = {
            "verdict": "SKELETON_ONLY_NOT_IMPLEMENTED",
            "summary": f"{target_agent} is not implemented in this stage.",
            "data": {"status": "SKELETON_ONLY_NOT_IMPLEMENTED"},
        }
    else:
        body = route_dispatch(question, target_agent)

    answer = {
        "answer_id": answer_id,
        "question_id": question_id,
        "task_id": task_id,
        "agent": target_agent,
        "action": action,
        "verdict": body.get("verdict", "REQUEST_MORE_EVIDENCE"),
        "summary": body.get("summary", "No summary"),
        "data": body.get("data", {}),
        "generated_at_utc": now_utc(),
    }

    answer_path, receipt_path, outbox_path, agent_receipt_path = answer_and_receipt_paths(answer_id, target_agent)
    write_json(answer_path, answer)
    write_json(outbox_path, answer)

    receipt = {
        "receipt_id": stable_id("receipt", answer_id, target_agent),
        "answer_id": answer_id,
        "question_id": question_id,
        "task_id": task_id,
        "agent": target_agent,
        "verdict": answer["verdict"],
        "written_paths": [str(answer_path), str(outbox_path)],
        "timestamp_utc": now_utc(),
    }
    write_json(receipt_path, receipt)
    write_json(agent_receipt_path, receipt)

    update_agent_memory(
        target_agent,
        {
            "timestamp_utc": now_utc(),
            "event": "QUESTION_PROCESSED",
            "question_id": question_id,
            "task_id": task_id,
            "action": action,
            "verdict": answer["verdict"],
        },
    )
    append_ledger_event(
        "AGENT_ANSWER",
        target_agent,
        {"task_id": task_id, "question_id": question_id, "answer_id": answer_id, "verdict": answer["verdict"]},
    )

    return {"answer": answer, "receipt": receipt, "answer_path": str(answer_path), "receipt_path": str(receipt_path)}


def administratum_create_task_envelope(task: Dict[str, Any]) -> Dict[str, Any]:
    task_id = task["task_id"]
    envelope = {
        "envelope_id": stable_id("envelope", task_id),
        "task_id": task_id,
        "title": task.get("title", ""),
        "description": task.get("description", ""),
        "payload": task.get("payload", {}),
        "created_at_utc": now_utc(),
        "owner": task.get("owner", "OWNER_UNKNOWN"),
    }
    out = ROOT / "EXCHANGE" / "SERVITOR" / "inbox" / f"{task_id}_task_envelope.json"
    arch = ROOT / "ARCHIVE" / "ADMINISTRATUM_PERMANENT_ARCHIVE" / "task_archive" / f"{task_id}_task_envelope.json"
    write_json(out, envelope)
    write_json(arch, envelope)
    update_index_list(
        ROOT / "LEDGER" / "task_index.json",
        "tasks",
        {"task_id": task_id, "envelope_path": str(out), "created_at_utc": envelope["created_at_utc"]},
    )
    append_ledger_event("TASK_ENVELOPE_CREATED", "ADMINISTRATUM_AGENT", {"task_id": task_id, "path": str(out)})
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "TASK_ENVELOPE_CREATED",
            "task_id": task_id,
            "path": str(out),
        },
    )
    return {"data": envelope, "path": str(out), "archive_path": str(arch)}


def administratum_create_route_sheet(task: Dict[str, Any]) -> Dict[str, Any]:
    task_id = task["task_id"]
    route_id = stable_id("route", task_id)
    route = {
        "route_id": route_id,
        "task_id": task_id,
        "route_sequence": [
            "ADMINISTRATUM_AGENT",
            "CUSTODES_AGENT",
            "MECHANICUS_AGENT",
            "ADMINISTRATUM_AGENT",
        ],
        "status": "ROUTE_OPEN",
        "created_at_utc": now_utc(),
        "steps": [],
    }
    serv_path = ROOT / "EXCHANGE" / "SERVITOR" / "route_sheets" / f"{route_id}.json"
    bus_path = ROOT / "EXCHANGE" / "ORGAN_BUS" / "route_sessions" / f"{route_id}.json"
    write_json(serv_path, route)
    write_json(bus_path, route)
    update_index_list(
        ROOT / "LEDGER" / "route_index.json",
        "routes",
        {"route_id": route_id, "task_id": task_id, "path": str(serv_path), "status": "ROUTE_OPEN"},
    )
    append_ledger_event("ROUTE_SHEET_CREATED", "ADMINISTRATUM_AGENT", {"task_id": task_id, "route_id": route_id})
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "ROUTE_SHEET_CREATED",
            "task_id": task_id,
            "route_id": route_id,
        },
    )
    return {"data": route, "path": str(serv_path), "bus_path": str(bus_path)}


def administratum_register_organ_answer(answer_blob: Dict[str, Any]) -> str:
    answer = answer_blob["answer"]
    task_id = answer.get("task_id", "NO_TASK")
    aid = answer["answer_id"]
    path = ROOT / "ARCHIVE" / "ADMINISTRATUM_PERMANENT_ARCHIVE" / "answer_archive" / f"{aid}.json"
    write_json(path, answer)
    append_ledger_event(
        "ANSWER_REGISTERED",
        "ADMINISTRATUM_AGENT",
        {"task_id": task_id, "answer_id": aid, "verdict": answer.get("verdict", "UNKNOWN")},
    )
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "ANSWER_REGISTERED",
            "task_id": task_id,
            "answer_id": aid,
            "verdict": answer.get("verdict", "UNKNOWN"),
        },
    )
    return str(path)


def administratum_register_receipt(receipt_data: Dict[str, Any], name_hint: str) -> str:
    path = ROOT / "ARCHIVE" / "ADMINISTRATUM_PERMANENT_ARCHIVE" / "receipt_archive" / f"{name_hint}.json"
    write_json(path, receipt_data)
    append_ledger_event(
        "RECEIPT_REGISTERED",
        "ADMINISTRATUM_AGENT",
        {"task_id": receipt_data.get("task_id", "NO_TASK"), "receipt_id": receipt_data.get("receipt_id", name_hint)},
    )
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "RECEIPT_REGISTERED",
            "task_id": receipt_data.get("task_id", "NO_TASK"),
            "receipt_id": receipt_data.get("receipt_id", name_hint),
        },
    )
    return str(path)


def administratum_build_final_route_report(task: Dict[str, Any], route_sheet: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    task_id = task["task_id"]
    route_id = route_sheet["route_id"]
    final = {
        "final_route_report_id": stable_id("route_final", route_id, task_id),
        "task_id": task_id,
        "route_id": route_id,
        "generated_at_utc": now_utc(),
        "answers": [
            {
                "agent": a["answer"]["agent"],
                "action": a["answer"]["action"],
                "verdict": a["answer"]["verdict"],
                "answer_path": a["answer_path"],
                "receipt_path": a["receipt_path"],
            }
            for a in answers
        ],
        "route_verdict": "PASS"
        if all(a["answer"]["verdict"] not in {"REJECT", "BLOCK_CORE_ACCESS", "FAIL"} for a in answers)
        else "BLOCKED",
    }
    route_path = ROOT / "ARCHIVE" / "ADMINISTRATUM_PERMANENT_ARCHIVE" / "route_archive" / f"{final['final_route_report_id']}.json"
    write_json(route_path, final)
    append_ledger_event(
        "FINAL_ROUTE_REPORT_BUILT",
        "ADMINISTRATUM_AGENT",
        {"task_id": task_id, "route_id": route_id, "route_verdict": final["route_verdict"]},
    )
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "FINAL_ROUTE_REPORT_BUILT",
            "task_id": task_id,
            "route_id": route_id,
            "route_verdict": final["route_verdict"],
        },
    )
    return {"data": final, "path": str(route_path)}


def run_route(task_path: Path) -> Dict[str, Any]:
    task = load_json(task_path)
    task_id = task.get("task_id", "NO_TASK_ID")

    envelope = administratum_create_task_envelope(task)
    route_sheet = administratum_create_route_sheet(task)

    cust_q = {
        "question_id": stable_id("q", task_id, "custodes"),
        "task_id": task_id,
        "target_agent": "CUSTODES_AGENT",
        "action": "FILTER_ZONE_ADMISSION",
        "payload": {
            "operation": "write",
            "proposed_paths": [
                "IMPERIUM_NEW_GENERATION/EXCHANGE/ORGAN_BUS/answers",
                "IMPERIUM_NEW_GENERATION/ARCHIVE",
            ],
            "reason": "Base route admission check",
        },
        "requested_by": "ADMINISTRATUM_AGENT",
        "read_only": False,
    }
    cust_q_path = ROOT / "EXCHANGE" / "ORGAN_BUS" / "questions" / f"{cust_q['question_id']}.json"
    write_json(cust_q_path, cust_q)
    cust_ans = process_question(cust_q)

    mech_q = {
        "question_id": stable_id("q", task_id, "mechanicus"),
        "task_id": task_id,
        "target_agent": "MECHANICUS_AGENT",
        "action": "MATCH_TOOLS_TO_TASK",
        "payload": {
            "task_text": f"{task.get('title', '')} {task.get('description', '')}",
            "constraints": "candidate_only_no_install",
        },
        "requested_by": "ADMINISTRATUM_AGENT",
        "read_only": True,
    }
    mech_q_path = ROOT / "EXCHANGE" / "ORGAN_BUS" / "questions" / f"{mech_q['question_id']}.json"
    write_json(mech_q_path, mech_q)
    mech_ans = process_question(mech_q)

    answer_arch_1 = administratum_register_organ_answer(cust_ans)
    answer_arch_2 = administratum_register_organ_answer(mech_ans)
    final_report = administratum_build_final_route_report(task, route_sheet["data"], [cust_ans, mech_ans])

    route_receipt = {
        "receipt_id": stable_id("route_receipt", task_id, route_sheet["data"]["route_id"]),
        "task_id": task_id,
        "route_id": route_sheet["data"]["route_id"],
        "timestamp_utc": now_utc(),
        "envelope_path": envelope["path"],
        "route_sheet_path": route_sheet["path"],
        "questions": [str(cust_q_path), str(mech_q_path)],
        "answers": [cust_ans["answer_path"], mech_ans["answer_path"]],
        "answer_archive_paths": [answer_arch_1, answer_arch_2],
        "final_route_report_path": final_report["path"],
        "route_verdict": final_report["data"]["route_verdict"],
    }

    serv_receipt = ROOT / "EXCHANGE" / "SERVITOR" / "receipts" / f"{route_receipt['receipt_id']}.json"
    write_json(serv_receipt, route_receipt)
    archive_receipt = administratum_register_receipt(route_receipt, route_receipt["receipt_id"])
    append_ledger_event(
        "ROUTE_COMPLETED",
        "ADMINISTRATUM_AGENT",
        {
            "task_id": task_id,
            "route_id": route_receipt["route_id"],
            "route_verdict": route_receipt["route_verdict"],
        },
    )
    update_agent_memory(
        "ADMINISTRATUM_AGENT",
        {
            "timestamp_utc": now_utc(),
            "event": "ROUTE_COMPLETED",
            "task_id": task_id,
            "route_id": route_receipt["route_id"],
            "route_verdict": route_receipt["route_verdict"],
        },
    )

    return {
        "task_id": task_id,
        "route_receipt_path": str(serv_receipt),
        "archive_receipt_path": archive_receipt,
        "final_route_report_path": final_report["path"],
        "route_verdict": route_receipt["route_verdict"],
    }


def get_agent_status(agent_id: str) -> Dict[str, Any]:
    manifest = manifest_for(agent_id)
    mpaths = memory_paths(agent_id)
    return {
        "agent": agent_id,
        "status": manifest.get("status", "UNKNOWN"),
        "maturity_stage": manifest.get("maturity_stage", "UNKNOWN"),
        "supported_actions": manifest.get("supported_actions", []),
        "short_term_entries": memory_line_count(mpaths["short_term"]),
        "approved_learning_entries": memory_line_count(mpaths["approved"]),
        "rejected_learning_entries": memory_line_count(mpaths["rejected"]),
    }


def cmd_agent_status(args: argparse.Namespace) -> int:
    agent_id = normalize_agent_id(args.agent)
    status = get_agent_status(agent_id)
    print(f"AGENT {status['agent']}")
    print(f"STATUS {status['status']}")
    print(f"STAGE {status['maturity_stage']}")
    print(f"ACTIONS {','.join(status['supported_actions']) if status['supported_actions'] else 'none'}")
    print(f"SHORT_TERM_ENTRIES {status['short_term_entries']}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    question_path = Path(args.question)
    question = load_json(question_path)
    result = process_question(question, forced_agent=normalize_agent_id(args.agent))
    print(f"ASK_AGENT {result['answer']['agent']}")
    print(f"ASK_VERDICT {result['answer']['verdict']}")
    print(f"ANSWER_JSON {result['answer_path']}")
    print(f"RECEIPT_JSON {result['receipt_path']}")
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    task_path = Path(args.task)
    result = run_route(task_path)
    print(f"ROUTE_TASK {result['task_id']}")
    print(f"ROUTE_VERDICT {result['route_verdict']}")
    print(f"ROUTE_RECEIPT {result['route_receipt_path']}")
    print(f"FINAL_ROUTE_REPORT {result['final_route_report_path']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="imperium_ng_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    agent = sub.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="agent_cmd", required=True)
    st = agent_sub.add_parser("status")
    st.add_argument("--agent", required=True)
    st.set_defaults(func=cmd_agent_status)

    ask = sub.add_parser("ask")
    ask.add_argument("--agent", required=True)
    ask.add_argument("--question", required=True)
    ask.set_defaults(func=cmd_ask)

    route = sub.add_parser("route")
    route.add_argument("--task", required=True)
    route.set_defaults(func=cmd_route)
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
