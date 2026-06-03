from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

HERE = Path(__file__).resolve()
NEWGEN_ROOT = HERE.parents[2]
COMMON_ROOT = NEWGEN_ROOT / "ORGAN_AGENT_COMMON"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from organ_agent_runtime_v0_1 import build_verdict_payload, read_organ_bundle, utc_now, write_json

TASK_ID_DEFAULT = "TASK-20260524-NEWGEN-CORE-ORGAN-FORM-TUI-WAVE1-VM3-V0_1"
ORGAN_ID = "OFFICIO_AGENTIS"
ORGAN_ROOT = HERE.parents[1]


def _collect_evidence_required(gates: Iterable[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for gate in gates:
        for item in gate.get("evidence_required", []):
            text = str(item).strip()
            if text and text not in out:
                out.append(text)
    return out


def build_response(task_id: str, question: str, mode: str) -> Dict[str, Any]:
    bundle = read_organ_bundle(ORGAN_ROOT)
    gates = bundle.get("gate_catalog", {}).get("gates", [])
    state = bundle.get("state", {})
    evidence_required = _collect_evidence_required(gates if isinstance(gates, list) else [])
    applied_rules = [str(g.get("gate_id", "")) for g in gates if isinstance(g, dict)]

    verdict = str(state.get("default_verdict", "PASS"))
    owner_question = None
    lowered = question.lower()
    if "owner verdict" in lowered or "scope change" in lowered:
        verdict = "OWNER_VERDICT_NEEDED"
        owner_question = "Разрешает ли Owner изменить scope/формат ответа в этой задаче?"
    elif "english" in lowered or "generic pass" in lowered:
        verdict = "BLOCK"

    payload = build_verdict_payload(
        organ_id=ORGAN_ID,
        task_id=task_id,
        mode=mode,
        verdict=verdict,
        applied_rules=applied_rules,
        required_actions=state.get("required_actions", []),
        forbidden_actions=state.get("forbidden_actions", []),
        evidence_required=evidence_required,
        evidence_refs=state.get("evidence_refs", []),
        not_proven=[
            "full multi-agent autonomy",
            "Owner Verdict Needed live UI button",
        ],
        owner_question=owner_question,
    )
    payload["question"] = question
    payload["generated_at_utc"] = utc_now()
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave1 Officio organ query tool.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--question", default="What role and language rules apply to this task?")
    parser.add_argument("--mode", default="SERVITOR_QUERY")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    question = args.question
    if args.sample:
        question = "What role and language rules apply to this task?"
    payload = build_response(task_id=str(args.task_id), question=question, mode=str(args.mode))
    if args.output:
        write_json(Path(args.output), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    verdict = str(payload.get("verdict", "WARN"))
    return 2 if verdict in {"BLOCK", "OWNER_VERDICT_NEEDED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
