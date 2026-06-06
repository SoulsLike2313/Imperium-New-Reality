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

TASK_ID_DEFAULT = "TASK-20260524-NEWGEN-METAOS-LAW-AND-CORE-ORGAN-WAVE2-VM3-V0_1"
ORGAN_ID = "INQUISITION"
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
    owner_q = None
    lowered = question.lower()

    block_terms = [
        "skip",
        "without evidence",
        "generic pass",
        "dirty",
        "duplicate",
        "unregistered",
        "no stage",
    ]
    if any(term in lowered for term in block_terms):
        verdict = "BLOCK"

    if "owner verdict" in lowered or "owner decision" in lowered or "override" in lowered:
        verdict = "OWNER_VERDICT_NEEDED"
        owner_q = "Требуется ли Owner override при критическом конфликте между скоростью и полнотой аудита?"

    if "partial" in lowered or "not run" in lowered:
        verdict = "WARN" if verdict == "PASS" else verdict

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
            "Strategium/Schola/Custodes/Throne implementation",
            "live Owner Verdict Needed UI button",
            "production autonomy",
            "full organ intelligence",
            "full external adapter layer",
        ],
        owner_question=owner_q,
    )
    payload["question"] = question
    payload["generated_at_utc"] = utc_now()
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave2 INQUISITION organ query tool.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--question", default="What is this organ's required control path?")
    parser.add_argument("--mode", default="SERVITOR_QUERY")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    question = args.question
    if args.sample:
        question = "What checks must pass before we can continue?"
    payload = build_response(task_id=str(args.task_id), question=question, mode=str(args.mode))
    if args.output:
        write_json(Path(args.output), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    verdict = str(payload.get("verdict", "WARN"))
    return 2 if verdict in {"BLOCK", "OWNER_VERDICT_NEEDED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
