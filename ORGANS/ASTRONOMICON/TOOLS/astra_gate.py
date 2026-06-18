#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASTRONOMICON inbound gate v0_1.

Первый входной шлюз Империума. Валидирует task-pack/patch по трём воротам
(FORM / COMPLETENESS / CORRECTNESS) и выдаёт вердикт ADMIT|REJECT с причинами.
НА ADMIT пак не исполняется сразу — он передаётся Трону на верховный permit.
Чистый stdlib. Evidence: E3_EXECUTED (реальный запуск).
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

SCHEMA_VERSION = "imperium.astra_task_pack.v0_1"
RECEIPT_SCHEMA = "imperium.astra_admission_receipt.v0_1"
PROVENANCE = "ASTRONOMICON inbound gate v0_1; E3_EXECUTED; supreme permit deferred to THRONE"

CANON_ORGANS = {
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM",
    "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
    "STRATEGIUM",
}
VALID_SUBMITTERS = {"OWNER_MANUAL", "SERVITOR"}
VALID_CHANGE_KINDS = {"PATCH", "NEW_FILE", "DELETE", "REFACTOR", "DOC"}
EVIDENCE_LEVELS = ["E1", "E2", "E3", "E4", "E5", "E6"]
REQUIRED_FIELDS = [
    "schema_version", "task_id", "title", "submitted_by", "target_organ",
    "intent", "change_kind", "payload", "declared_evidence_level",
]


def _add(reasons, gate, code, message):
    reasons.append({"gate": gate, "code": code, "message": message})


def _payload_digest(pack_dir, payload):
    h = hashlib.sha256()
    for rel in sorted(p for p in payload if isinstance(p, str)):
        fp = os.path.join(pack_dir, rel)
        if os.path.isfile(fp):
            with open(fp, "rb") as f:
                h.update(rel.encode("utf-8"))
                h.update(f.read())
    return "sha256:" + h.hexdigest()


def validate(pack_dir):
    reasons = []
    manifest_path = os.path.join(pack_dir, "TASK_MANIFEST.json")

    # --- FORM ---
    if not os.path.isfile(manifest_path):
        _add(reasons, "FORM", "MANIFEST_MISSING",
             "TASK_MANIFEST.json не найден в корне пака")
        return _finish(reasons, None, pack_dir, [])
    try:
        with open(manifest_path, encoding="utf-8") as f:
            m = json.load(f)
    except Exception as exc:
        _add(reasons, "FORM", "MANIFEST_UNPARSEABLE",
             "TASK_MANIFEST.json не парсится: %s" % exc)
        return _finish(reasons, None, pack_dir, [])
    if not isinstance(m, dict):
        _add(reasons, "FORM", "MANIFEST_NOT_OBJECT", "TASK_MANIFEST.json должен быть объектом")
        return _finish(reasons, None, pack_dir, [])

    sv = m.get("schema_version")
    if sv != SCHEMA_VERSION:
        _add(reasons, "FORM", "SCHEMA_VERSION_BAD",
             "schema_version ожидается %r, получено %r" % (SCHEMA_VERSION, sv))
    for k in REQUIRED_FIELDS:
        if k not in m or m.get(k) in (None, "", []):
            _add(reasons, "FORM", "FIELD_MISSING", "нет обязательного поля: %s" % k)
    if "payload" in m and not isinstance(m.get("payload"), list):
        _add(reasons, "FORM", "PAYLOAD_TYPE", "payload должен быть массивом путей")

    payload = m.get("payload") if isinstance(m.get("payload"), list) else []

    # --- COMPLETENESS ---
    if not payload:
        _add(reasons, "COMPLETENESS", "PAYLOAD_EMPTY", "payload пуст — нечего исполнять")
    for rel in payload:
        if not isinstance(rel, str):
            _add(reasons, "COMPLETENESS", "PAYLOAD_ENTRY_TYPE",
                 "элемент payload не строка: %r" % (rel,))
            continue
        if not os.path.isfile(os.path.join(pack_dir, rel)):
            _add(reasons, "COMPLETENESS", "PAYLOAD_FILE_MISSING",
                 "файл payload отсутствует в паке: %s" % rel)
    intent = m.get("intent")
    if isinstance(intent, str) and len(intent.strip()) < 8:
        _add(reasons, "COMPLETENESS", "INTENT_TOO_THIN",
             "intent слишком короткий — нужно осмысленное описание")

    # --- CORRECTNESS ---
    org = m.get("target_organ")
    if org is not None and org not in CANON_ORGANS:
        _add(reasons, "CORRECTNESS", "TARGET_ORGAN_UNKNOWN",
             "target_organ %r не входит в 9 канонических органов" % (org,))
    sb = m.get("submitted_by")
    if sb is not None and sb not in VALID_SUBMITTERS:
        _add(reasons, "CORRECTNESS", "SUBMITTER_UNKNOWN",
             "submitted_by %r не из %s" % (sb, sorted(VALID_SUBMITTERS)))
    ck = m.get("change_kind")
    if ck is not None and ck not in VALID_CHANGE_KINDS:
        _add(reasons, "CORRECTNESS", "CHANGE_KIND_UNKNOWN",
             "change_kind %r не из %s" % (ck, sorted(VALID_CHANGE_KINDS)))
    el = m.get("declared_evidence_level")
    if el is not None and el not in EVIDENCE_LEVELS:
        _add(reasons, "CORRECTNESS", "EVIDENCE_LEVEL_BAD",
             "declared_evidence_level %r вне %s" % (el, EVIDENCE_LEVELS))
    if el in ("E3", "E4", "E5", "E6") and not (m.get("execution_log") or m.get("replay")):
        _add(reasons, "CORRECTNESS", "CLAIM_WITHOUT_REPLAY",
             "declared_evidence_level=%s без execution_log/replay — потенциальный fake-green" % el)

    return _finish(reasons, m, pack_dir, payload)


def _finish(reasons, m, pack_dir, payload):
    verdict = "ADMIT" if not reasons else "REJECT"
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "gateway": "ASTRONOMICON",
        "stage": "INBOUND",
        "task_id": (m or {}).get("task_id"),
        "title": (m or {}).get("title"),
        "target_organ": (m or {}).get("target_organ"),
        "submitted_by": (m or {}).get("submitted_by"),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "reasons": reasons,
        "payload_digest": _payload_digest(pack_dir, payload),
        "next_action": "FORWARD_TO_THRONE_PERMIT" if verdict == "ADMIT" else "RETURN_TO_SUBMITTER",
        "evidence_level": "E3_EXECUTED",
        "provenance": PROVENANCE,
    }
    return verdict, reasons, receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASTRONOMICON inbound gate v0_1")
    ap.add_argument("pack_dir", help="корень task-pack (с TASK_MANIFEST.json)")
    ap.add_argument("--receipt", help="куда записать admission-рецепт (JSON)")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.pack_dir):
        sys.stderr.write("ERROR: нет директории пака: %s\n" % args.pack_dir)
        return 1

    verdict, reasons, receipt = validate(args.pack_dir)

    print("=" * 60)
    print("  ASTRONOMICON INBOUND GATE v0_1")
    print("  pack    : %s" % args.pack_dir)
    print("  task_id : %s" % receipt.get("task_id"))
    print("  organ   : %s" % receipt.get("target_organ"))
    print("  digest  : %s" % receipt.get("payload_digest"))
    print("=" * 60)
    if reasons:
        for r in reasons:
            print("  [%-12s] %-22s %s" % (r["gate"], r["code"], r["message"]))
    else:
        print("  все ворота чистые")
    print("-" * 60)
    print("  VERDICT     : %s" % verdict)
    print("  NEXT_ACTION : %s" % receipt.get("next_action"))

    if args.receipt:
        with open(args.receipt, "w", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2)
        print("  receipt     : %s" % args.receipt)

    return 0 if verdict == "ADMIT" else 2


if __name__ == "__main__":
    sys.exit(main())
