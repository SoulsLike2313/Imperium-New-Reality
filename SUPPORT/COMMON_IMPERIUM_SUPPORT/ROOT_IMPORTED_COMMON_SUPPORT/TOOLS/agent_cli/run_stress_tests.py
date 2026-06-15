#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "TOOLS" / "agent_cli" / "imperium_ng_cli.py"
OUT_DIR = ROOT / "STRESS_TESTS"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_changed_paths():
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT.parent,
        capture_output=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    results = []
    baseline_paths = git_changed_paths()

    for agent in ["ADMINISTRATUM", "CUSTODES", "MECHANICUS"]:
        rc, out, err = run([sys.executable, str(CLI), "agent", "status", "--agent", agent])
        results.append(
            {
                "test": f"status_{agent}",
                "pass": rc == 0 and "STATUS BASE_IMPLEMENTED_V0_1" in out,
                "stdout": out,
                "stderr": err,
            }
        )

    q_ok = ROOT / "STRESS_TESTS" / "custodes_question_ok_v0_1.json"
    q_ok.write_text(
        json.dumps(
            {
                "question_id": "stress_q_custodes_ok",
                "task_id": "stress_task_first_3",
                "target_agent": "CUSTODES_AGENT",
                "action": "CHECK_ALLOWED_PATHS",
                "payload": {
                    "operation": "write",
                    "proposed_paths": ["IMPERIUM_NEW_GENERATION/EXCHANGE/ORGAN_BUS/answers"],
                },
                "read_only": False,
                "requested_by": "STRESS_TEST",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    rc, out, err = run([sys.executable, str(CLI), "ask", "--agent", "CUSTODES", "--question", str(q_ok)])
    results.append({"test": "ask_custodes", "pass": rc == 0 and "ASK_VERDICT ADMIT" in out, "stdout": out, "stderr": err})

    demo_task = ROOT / "INTAKE" / "normalized" / "demo_task_first_3_agent_route_v0_1.json"
    rc, out, err = run([sys.executable, str(CLI), "route", "--task", str(demo_task)])
    results.append({"test": "route_first_three", "pass": rc == 0 and "ROUTE_VERDICT PASS" in out, "stdout": out, "stderr": err})

    receipt_files = list((ROOT / "EXCHANGE" / "SERVITOR" / "receipts").glob("*.json"))
    results.append({"test": "receipts_created", "pass": len(receipt_files) > 0, "count": len(receipt_files)})

    mem_pass = True
    for agent in ["ADMINISTRATUM_AGENT", "CUSTODES_AGENT", "MECHANICUS_AGENT"]:
        st = ROOT / "ORGAN_AGENTS" / agent / "memory" / "short_term.jsonl"
        if not st.exists() or not st.read_text(encoding="utf-8").strip():
            mem_pass = False
    results.append({"test": "memory_updated_first_three", "pass": mem_pass})

    archive_count = len(list((ROOT / "ARCHIVE" / "ADMINISTRATUM_PERMANENT_ARCHIVE").rglob("*.json")))
    results.append({"test": "administratum_archive_written", "pass": archive_count > 0, "json_files": archive_count})

    q_bad = ROOT / "STRESS_TESTS" / "custodes_question_forbidden_write_v0_1.json"
    q_bad.write_text(
        json.dumps(
            {
                "question_id": "stress_q_custodes_forbidden",
                "task_id": "stress_task_first_3",
                "target_agent": "CUSTODES_AGENT",
                "action": "CHECK_ALLOWED_PATHS",
                "payload": {
                    "operation": "write",
                    "proposed_paths": ["ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json"],
                },
                "read_only": False,
                "requested_by": "STRESS_TEST",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    rc, out, err = run([sys.executable, str(CLI), "ask", "--agent", "CUSTODES", "--question", str(q_bad)])
    results.append(
        {
            "test": "forbidden_write_rejected",
            "pass": rc == 0 and "ASK_VERDICT BLOCK_CORE_ACCESS" in out,
            "stdout": out,
            "stderr": err,
        }
    )

    rc, out, err = run([sys.executable, str(CLI), "agent", "status", "--agent", "THRONE"])
    results.append(
        {
            "test": "skeleton_status_honest",
            "pass": rc == 0 and "STATUS SKELETON_ONLY_NOT_IMPLEMENTED" in out,
            "stdout": out,
            "stderr": err,
        }
    )

    rc, out, err = run([sys.executable, str(ROOT / "TOOLS" / "agent_cli" / "count_agent_units.py")])
    results.append({"test": "count_agent_units", "pass": rc == 0 and "TOTAL:" in out, "stdout": out, "stderr": err})

    post_paths = git_changed_paths()
    new_paths = post_paths - baseline_paths
    outside_new_gen = sorted([p for p in new_paths if not p.startswith("IMPERIUM_NEW_GENERATION/")])
    results.append({"test": "no_new_out_of_scope_writes", "pass": len(outside_new_gen) == 0, "new_outside_paths": outside_new_gen})

    passed = sum(1 for r in results if r.get("pass"))
    report = {
        "suite": "NEW_GENERATION_FIRST_3_BASE_STRESS_V0_1",
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
        "verdict": "PASS" if passed == len(results) else "WARN_PARTIAL",
    }

    out_json = OUT_DIR / "NEW_GENERATION_FIRST_3_BASE_STRESS_RESULTS_V0_1.json"
    out_md = OUT_DIR / "NEW_GENERATION_FIRST_3_BASE_STRESS_RESULTS_V0_1.md"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# New Generation First 3 Base Stress Results V0.1",
        "",
        f"- total: {report['total']}",
        f"- passed: {report['passed']}",
        f"- failed: {report['failed']}",
        f"- verdict: {report['verdict']}",
        "",
    ]
    for item in results:
        lines.append(f"- {item['test']}: {'PASS' if item.get('pass') else 'FAIL'}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"STRESS_JSON {out_json}")
    print(f"STRESS_MD {out_md}")
    print(f"STRESS_VERDICT {report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
