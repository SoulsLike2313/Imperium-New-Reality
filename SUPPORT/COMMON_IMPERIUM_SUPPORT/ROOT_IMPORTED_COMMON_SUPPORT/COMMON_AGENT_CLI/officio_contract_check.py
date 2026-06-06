from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object expected: {path}")
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains_cyrillic(text: str) -> bool:
    return re.search(r"[А-Яа-яЁё]", text) is not None


def contains_latin(text: str) -> bool:
    return re.search(r"[A-Za-z]", text) is not None


def looks_like_machine_artifact(text: str) -> bool:
    blob = text.strip()
    if not blob:
        return False
    if blob.startswith("{") and blob.endswith("}"):
        return True
    if blob.startswith("[") and blob.endswith("]"):
        return True
    if "python3 " in blob or "git " in blob:
        return True
    if "/" in blob and "." in blob:
        return True
    return False


def extract_owner_comments(final_response: str) -> str:
    lines = final_response.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().upper().startswith("OWNER COMMENTS:"):
            start = idx + 1
            break
    if start is None:
        return ""

    block: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if re.match(r"^(STEP|BUNDLE|VERDICT|OWNER COMMENTS)\s*:", stripped, flags=re.IGNORECASE):
            break
        if not stripped:
            continue
        block.append(stripped)
    return "\n".join(block).strip()


def required_sections_from_contract(contract_json: dict[str, Any]) -> list[str]:
    machine_rule = contract_json.get("machine_rule", {})
    if isinstance(machine_rule, dict):
        sections = machine_rule.get("required_sections", [])
        if isinstance(sections, list):
            return [str(item).strip() for item in sections if str(item).strip()]
    return ["STEP", "BUNDLE", "VERDICT", "OWNER COMMENTS"]


def section_headers_present(text: str, required_sections: list[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for section in required_sections:
        pattern = re.compile(rf"^{re.escape(section)}\s*:", flags=re.IGNORECASE | re.MULTILINE)
        if not pattern.search(text):
            missing.append(section)
    return len(missing) == 0, missing


def evaluate_owner_live(text: str, officio_ack: bool) -> dict[str, Any]:
    if not officio_ack:
        return {
            "verdict": "WARN",
            "code": "WARN_OFFICIO_ACK_NOT_ACTIVE",
            "reason": "Officio ACK not active; owner language rule not enforced.",
        }
    if contains_cyrillic(text):
        return {
            "verdict": "PASS",
            "code": "PASS_OFFICIO_ACTIVE_AUTHORITY_V0_1",
            "reason": "Russian owner-facing live commentary detected after ACK.",
        }
    if contains_latin(text):
        return {
            "verdict": "WARN",
            "code": "WARN_RESPONSE_LANGUAGE_CONTRACT",
            "reason": "English owner-facing live commentary detected after ACK.",
        }
    return {
        "verdict": "WARN",
        "code": "WARN_RESPONSE_LANGUAGE_CONTRACT",
        "reason": "Unable to detect Russian owner-facing live commentary after ACK.",
    }


def evaluate_machine_artifact(text: str) -> dict[str, Any]:
    if looks_like_machine_artifact(text):
        return {
            "verdict": "PASS",
            "code": "PASS_MACHINE_ARTIFACT_ENGLISH_ALLOWED",
            "reason": "Machine artifact heuristic matched; English technical text is allowed.",
        }
    return {
        "verdict": "PASS",
        "code": "PASS_MACHINE_ARTIFACT_ENGLISH_ALLOWED",
        "reason": "No owner-facing enforcement triggered for machine-artifact surface.",
    }


def evaluate_final_response(text: str, officio_ack: bool, required_sections: list[str]) -> dict[str, Any]:
    headers_ok, missing_headers = section_headers_present(text, required_sections)
    if not headers_ok:
        return {
            "verdict": "FAIL",
            "code": "FAIL_RESPONSE_CONTRACT",
            "reason": "Final response is missing required sections.",
            "missing_sections": missing_headers,
        }

    owner_comments = extract_owner_comments(text)
    if not owner_comments:
        return {
            "verdict": "FAIL",
            "code": "FAIL_RESPONSE_CONTRACT",
            "reason": "OWNER COMMENTS block is missing or empty.",
        }
    if not officio_ack:
        return {
            "verdict": "WARN",
            "code": "WARN_OFFICIO_ACK_NOT_ACTIVE",
            "reason": "Officio ACK not active; OWNER COMMENTS language rule not enforced.",
        }
    if contains_cyrillic(owner_comments):
        return {
            "verdict": "PASS",
            "code": "PASS_OFFICIO_ACTIVE_AUTHORITY_V0_1",
            "reason": "Russian OWNER COMMENTS detected after ACK.",
        }
    if contains_latin(owner_comments):
        return {
            "verdict": "FAIL",
            "code": "FAIL_RESPONSE_CONTRACT",
            "reason": "English OWNER COMMENTS detected after ACK.",
        }
    return {
        "verdict": "FAIL",
        "code": "FAIL_RESPONSE_CONTRACT",
        "reason": "Unable to validate OWNER COMMENTS language as Russian after ACK.",
    }


def load_contract_context(repo_root: Path) -> dict[str, Any]:
    officio_root = repo_root / "IMPERIUM_NEW_GENERATION" / "ORGAN_AGENTS" / "OFFICIO_AGENTIS_AGENT"
    response_contract_json_path = officio_root / "RESPONSE_CONTRACTS" / "SERVITOR_EXECUTOR_RESPONSE_CONTRACT.json"
    language_contract_json_path = officio_root / "SETTINGS_REGISTRY" / "communication" / "language_execution_contract.json"
    ack_protocol_json_path = officio_root / "RESPONSE_CONTRACTS" / "ROLE_SETTINGS_ACK_PROTOCOL.json"

    return {
        "response_contract_json_path": str(response_contract_json_path),
        "language_execution_contract_json_path": str(language_contract_json_path),
        "role_settings_ack_protocol_json_path": str(ack_protocol_json_path),
        "response_contract": read_json(response_contract_json_path),
        "language_execution_contract": read_json(language_contract_json_path),
        "role_settings_ack_protocol": read_json(ack_protocol_json_path),
    }


def load_text_from_args(text_value: str | None, file_value: str | None) -> str:
    if text_value and file_value:
        raise ValueError("Use either --text or --file, not both.")
    if file_value:
        return read_text(Path(file_value).resolve())
    if text_value is not None:
        return text_value
    raise ValueError("Provide --text or --file.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Officio language/response contract checker V0.1.")
    parser.add_argument("--surface", choices=["owner_live", "machine_artifact", "final_response"], required=True)
    parser.add_argument("--text", help="Inline sample text to evaluate.")
    parser.add_argument("--file", help="Sample file path to evaluate.")
    parser.add_argument("--officio-ack", choices=["true", "false"], default="true")
    args = parser.parse_args()

    try:
        sample_text = load_text_from_args(args.text, args.file)
    except Exception as error:
        print(f"INPUT_ERROR: {error}", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[2]
    try:
        ctx = load_contract_context(repo_root)
    except Exception as error:
        print(f"CONTRACT_LOAD_ERROR: {error}", file=sys.stderr)
        return 2

    officio_ack = args.officio_ack.lower() == "true"
    required_sections = required_sections_from_contract(ctx["response_contract"])

    if args.surface == "owner_live":
        result = evaluate_owner_live(sample_text, officio_ack)
    elif args.surface == "machine_artifact":
        result = evaluate_machine_artifact(sample_text)
    else:
        result = evaluate_final_response(sample_text, officio_ack, required_sections)

    payload = {
        "checker_version": "OFFICIO_CONTRACT_CHECK_V0_1",
        "surface": args.surface,
        "officio_ack": officio_ack,
        "result": result,
        "contract_paths": {
            "response_contract_json_path": ctx["response_contract_json_path"],
            "language_execution_contract_json_path": ctx["language_execution_contract_json_path"],
            "role_settings_ack_protocol_json_path": ctx["role_settings_ack_protocol_json_path"],
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    verdict = str(result.get("verdict", "FAIL")).upper()
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
