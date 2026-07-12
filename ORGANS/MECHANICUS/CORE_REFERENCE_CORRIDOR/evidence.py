"""HEAD-bound evidence envelopes with JSON/Markdown pairing and sealing."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
import uuid


REQUIRED_PROOF_FIELDS = (
    "schema_version",
    "evidence_id",
    "task_id",
    "warp_id",
    "event_id",
    "base_head",
    "result_head_or_tree_hash",
    "branch",
    "timestamp_utc",
    "host_fingerprint",
    "toolchain",
    "exact_argv",
    "executable_path",
    "executable_sha256",
    "cwd",
    "environment_profile",
    "input_hashes",
    "output_hashes",
    "stdout_hash",
    "stderr_hash",
    "exit_code",
    "timeout",
    "pre_git_state",
    "post_git_state",
    "filesystem_diff",
    "validator_ids",
    "acceptance_results",
    "organ_verdict_refs",
    "owner_decision_ref",
    "parent_evidence_ids",
)

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_OR_TREE_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")


class EvidenceError(RuntimeError):
    """Invalid, incomplete, or unsafe evidence."""


class EvidenceTamperError(EvidenceError):
    """Stored bytes no longer agree with their finalized index."""


class EvidenceFinalizedError(EvidenceError):
    """A caller attempted to mutate finalized evidence or a sealed index."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_bytes(value: Any) -> bytes:
    try:
        rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"evidence is not canonical JSON: {exc}") from exc
    return (rendered + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _validate_timestamp(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise EvidenceError("timestamp_utc must be a non-empty UTC timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise EvidenceError("timestamp_utc is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise EvidenceError("timestamp_utc must carry UTC timezone information")


def _validate_hash_mapping(value: Any, field: str) -> None:
    if not isinstance(value, Mapping):
        raise EvidenceError(f"{field} must be an object")
    for name, digest in value.items():
        if not isinstance(name, str) or not isinstance(digest, str) or not _HEX_RE.fullmatch(digest.lower()):
            raise EvidenceError(f"{field} must map string names to sha256 digests")


def validate_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a detached JSON-compatible proof dictionary."""
    if not isinstance(envelope, Mapping):
        raise EvidenceError("evidence envelope must be an object")
    missing = [field for field in REQUIRED_PROOF_FIELDS if field not in envelope]
    if missing:
        raise EvidenceError(f"missing proof tuple fields: {', '.join(missing)}")
    if "_finalization" in envelope:
        raise EvidenceError("_finalization is store-owned metadata")
    for field in ("schema_version", "evidence_id", "task_id", "warp_id", "event_id", "branch", "executable_path", "cwd"):
        if not isinstance(envelope[field], str):
            raise EvidenceError(f"{field} must be a string")
    for field in ("evidence_id", "task_id", "warp_id", "event_id"):
        if not envelope[field] or (field == "evidence_id" and not _ID_RE.fullmatch(envelope[field])):
            raise EvidenceError(f"invalid {field}")
    for field in ("base_head", "result_head_or_tree_hash"):
        value = envelope[field]
        if not isinstance(value, str) or not _GIT_OR_TREE_RE.fullmatch(value.lower()):
            raise EvidenceError(f"{field} must be a full Git oid or sha256 tree hash")
    for field in ("executable_sha256", "stdout_hash", "stderr_hash"):
        value = envelope[field]
        if not isinstance(value, str) or not _HEX_RE.fullmatch(value.lower()):
            raise EvidenceError(f"{field} must be a sha256 digest")
    _validate_timestamp(envelope["timestamp_utc"])
    if not isinstance(envelope["host_fingerprint"], (str, Mapping)):
        raise EvidenceError("host_fingerprint must be a string or object")
    if not isinstance(envelope["toolchain"], (str, Mapping, list, tuple)):
        raise EvidenceError("toolchain must be structured")
    if not _sequence(envelope["exact_argv"]) or not all(isinstance(item, str) for item in envelope["exact_argv"]):
        raise EvidenceError("exact_argv must be an array of strings")
    if not isinstance(envelope["environment_profile"], (str, Mapping)):
        raise EvidenceError("environment_profile must be a string or object")
    _validate_hash_mapping(envelope["input_hashes"], "input_hashes")
    _validate_hash_mapping(envelope["output_hashes"], "output_hashes")
    if envelope["exit_code"] is not None and (
        not isinstance(envelope["exit_code"], int) or isinstance(envelope["exit_code"], bool)
    ):
        raise EvidenceError("exit_code must be an integer or null")
    if not isinstance(envelope["timeout"], (int, float)) or isinstance(envelope["timeout"], bool) or envelope["timeout"] < 0:
        raise EvidenceError("timeout must be a non-negative number")
    for field in ("pre_git_state", "post_git_state"):
        if not isinstance(envelope[field], Mapping):
            raise EvidenceError(f"{field} must be an object")
    if not isinstance(envelope["filesystem_diff"], (Mapping, list, tuple)):
        raise EvidenceError("filesystem_diff must be an object or array")
    for field in ("validator_ids", "organ_verdict_refs", "parent_evidence_ids"):
        if not _sequence(envelope[field]) or not all(isinstance(item, str) for item in envelope[field]):
            raise EvidenceError(f"{field} must be an array of strings")
    if not isinstance(envelope["acceptance_results"], (Mapping, list, tuple)):
        raise EvidenceError("acceptance_results must be an object or array")
    if envelope["owner_decision_ref"] is not None and not isinstance(envelope["owner_decision_ref"], str):
        raise EvidenceError("owner_decision_ref must be a string or null")
    return json.loads(_canonical_bytes(dict(envelope)))


def _markdown_value(value: Any) -> str:
    if isinstance(value, str):
        rendered = value
    else:
        rendered = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return rendered.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def render_compact_markdown(envelope: Mapping[str, Any], finalization: Mapping[str, Any]) -> str:
    lines = [
        f"# Evidence `{envelope['evidence_id']}`",
        "",
        f"Finalization: `{finalization['state']}`  ",
        f"Proof SHA-256: `{finalization['proof_sha256']}`",
        "",
        "| Proof field | Value |",
        "|---|---|",
    ]
    lines.extend(f"| `{field}` | {_markdown_value(envelope[field])} |" for field in REQUIRED_PROOF_FIELDS)
    lines.append("")
    return "\n".join(lines)


class EvidenceStore:
    """Atomic evidence pair writer with a self-hashed, sealable index."""

    def __init__(self, root: str | Path, *, index_name: str = "EVIDENCE_INDEX.json") -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / index_name
        if not self.index_path.exists():
            self._write_index(
                {
                    "schema_version": "imperium.evidence_index.v1",
                    "state": "OPEN",
                    "entries": {},
                    "finalized_at_utc": None,
                }
            )

    @staticmethod
    def _index_hash(index: Mapping[str, Any]) -> str:
        core = {key: value for key, value in index.items() if key != "content_sha256"}
        return _sha256(_canonical_bytes(core))

    def _write_index(self, index: Mapping[str, Any]) -> dict[str, Any]:
        materialized = dict(index)
        materialized["content_sha256"] = self._index_hash(materialized)
        _atomic_write(self.index_path, _canonical_bytes(materialized))
        return materialized

    def _load_index(self) -> dict[str, Any]:
        try:
            index = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceTamperError(f"evidence index cannot be read: {exc}") from exc
        if index.get("schema_version") != "imperium.evidence_index.v1" or not isinstance(index.get("entries"), dict):
            raise EvidenceTamperError("evidence index schema is invalid")
        if index.get("content_sha256") != self._index_hash(index):
            raise EvidenceTamperError("evidence index hash mismatch")
        return index

    def _paths(self, evidence_id: str) -> tuple[Path, Path]:
        if not _ID_RE.fullmatch(evidence_id):
            raise EvidenceError("unsafe evidence_id")
        return self.root / f"{evidence_id}.json", self.root / f"{evidence_id}.md"

    def write(self, envelope: Mapping[str, Any], *, finalize: bool = False) -> dict[str, Any]:
        proof = validate_envelope(envelope)
        evidence_id = proof["evidence_id"]
        index = self._load_index()
        if index["state"] == "FINALIZED":
            raise EvidenceFinalizedError("evidence index is finalized")
        previous = index["entries"].get(evidence_id)
        if previous and previous.get("state") == "FINALIZED":
            raise EvidenceFinalizedError(f"evidence {evidence_id} is finalized")
        proof_hash = _sha256(_canonical_bytes(proof))
        finalization = {
            "state": "FINALIZED" if finalize else "DRAFT",
            "proof_sha256": proof_hash,
            "finalized_at_utc": _utc_now() if finalize else None,
        }
        document = dict(proof)
        document["_finalization"] = finalization
        json_bytes = _canonical_bytes(document)
        markdown_bytes = render_compact_markdown(proof, finalization).encode("utf-8")
        json_path, markdown_path = self._paths(evidence_id)
        _atomic_write(json_path, json_bytes)
        _atomic_write(markdown_path, markdown_bytes)
        index["entries"][evidence_id] = {
            "state": finalization["state"],
            "json_path": json_path.name,
            "markdown_path": markdown_path.name,
            "proof_sha256": proof_hash,
            "json_sha256": _sha256(json_bytes),
            "markdown_sha256": _sha256(markdown_bytes),
            "indexed_at_utc": _utc_now(),
        }
        self._write_index(index)
        return dict(index["entries"][evidence_id])

    def finalize(self, evidence_id: str) -> dict[str, Any]:
        verification = self.verify(evidence_id, require_finalized=False)
        if verification["state"] == "FINALIZED":
            return verification
        json_path, _ = self._paths(evidence_id)
        document = json.loads(json_path.read_text(encoding="utf-8"))
        document.pop("_finalization", None)
        self.write(document, finalize=True)
        return self.verify(evidence_id, require_finalized=True)

    def verify(self, evidence_id: str, *, require_finalized: bool = True) -> dict[str, Any]:
        index = self._load_index()
        try:
            entry = index["entries"][evidence_id]
        except KeyError as exc:
            raise EvidenceError(f"evidence is not indexed: {evidence_id}") from exc
        json_path, markdown_path = self._paths(evidence_id)
        try:
            json_bytes = json_path.read_bytes()
            markdown_bytes = markdown_path.read_bytes()
        except OSError as exc:
            raise EvidenceTamperError(f"indexed evidence pair is missing: {exc}") from exc
        if _sha256(json_bytes) != entry.get("json_sha256") or _sha256(markdown_bytes) != entry.get("markdown_sha256"):
            raise EvidenceTamperError(f"evidence pair hash mismatch: {evidence_id}")
        try:
            document = json.loads(json_bytes)
        except json.JSONDecodeError as exc:
            raise EvidenceTamperError("evidence JSON is invalid") from exc
        finalization = document.pop("_finalization", None)
        if not isinstance(finalization, Mapping):
            raise EvidenceTamperError("evidence finalization metadata is missing")
        proof = validate_envelope(document)
        proof_hash = _sha256(_canonical_bytes(proof))
        if proof_hash != finalization.get("proof_sha256") or proof_hash != entry.get("proof_sha256"):
            raise EvidenceTamperError("proof payload hash mismatch")
        if finalization.get("state") != entry.get("state"):
            raise EvidenceTamperError("finalization state disagrees with index")
        expected_markdown = render_compact_markdown(proof, finalization).encode("utf-8")
        if expected_markdown != markdown_bytes:
            raise EvidenceTamperError("Markdown pair does not represent JSON proof")
        if require_finalized and finalization.get("state") != "FINALIZED":
            raise EvidenceError(f"evidence is not finalized: {evidence_id}")
        return {
            "verdict": "PASS_PROVEN",
            "evidence_id": evidence_id,
            "state": finalization["state"],
            "proof_sha256": proof_hash,
            "json_sha256": entry["json_sha256"],
            "markdown_sha256": entry["markdown_sha256"],
        }

    def finalize_index(self) -> dict[str, Any]:
        index = self._load_index()
        if index["state"] == "FINALIZED":
            return index
        if not index["entries"]:
            raise EvidenceError("cannot finalize an empty evidence index")
        for evidence_id in sorted(index["entries"]):
            self.verify(evidence_id, require_finalized=True)
        index["state"] = "FINALIZED"
        index["finalized_at_utc"] = _utc_now()
        return self._write_index(index)

    def verify_all(self, *, require_finalized_index: bool = False) -> dict[str, Any]:
        index = self._load_index()
        if require_finalized_index and index["state"] != "FINALIZED":
            raise EvidenceError("evidence index is not finalized")
        results = [self.verify(evidence_id, require_finalized=True) for evidence_id in sorted(index["entries"])]
        return {
            "verdict": "PASS_PROVEN",
            "index_state": index["state"],
            "index_sha256": index["content_sha256"],
            "evidence_count": len(results),
            "results": results,
        }
