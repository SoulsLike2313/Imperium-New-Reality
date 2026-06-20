#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPERIUM provenance v0_2 — неубиваемая подпись автора.

Модель Warp-Zone Work: всё что идёт в работу — подписано.
Подпись v0_2 = автор + форма + модель + sha256(payload), связанные вместе
(identity_signature). Авторство ДОПОЛНИТЕЛЬНО вшивается в git-историю (author коммитов) и в рецепт —
т.е. «точно не потеряется». Опциональный HMAC-ключ на автора (keystore) — апгрейд против подделки.
Чистый stdlib. Evidence: E3_EXECUTED.
"""
import argparse
import datetime
import hashlib
import hmac
import json
import os
import sys

PROV_SCHEMA = "imperium.provenance.v0_2"
PROV_FILE = "PROVENANCE.json"
MANIFEST_FILE = "TASK_MANIFEST.json"

# Авторы-подписанты (НЕ органы!):
#   NOTION_OPUS  = этот чат-агент (Notion, модель в поле model, напр. "Opus 4.8")
#   CODEX        = GPT
#   GROK         = Grok
#   OWNER_MANUAL = Рука лично владельца
AUTHORS = {"NOTION_OPUS", "CODEX", "GROK", "OWNER_MANUAL"}
FORMS = {"CHAT", "CLI"}

# Опциональный keystore для HMAC: путь из env IMPERIUM_KEYS (напр. E:\IMPERIUM_HARNESS\_KEYS).
# Если ключ автора есть — подпись становится keyed (неподдельной). Если нет — unkeyed фолбэк.


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _keystore_dir():
    return os.environ.get("IMPERIUM_KEYS")


def _author_key(author):
    d = _keystore_dir()
    if not d:
        return None
    p = os.path.join(d, author + ".key")
    if os.path.isfile(p):
        with open(p, "rb") as f:
            return f.read().strip()
    return None


def _ensure_key(author):
    d = _keystore_dir()
    if not d:
        return None
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, author + ".key")
    if not os.path.isfile(p):
        import secrets
        with open(p, "w", encoding="utf-8") as f:
            f.write(secrets.token_hex(32))
    return _author_key(author)


def payload_digest(pack_dir, payload):
    """Детерминированный хэш payload (тот же алгоритм, что в gate)."""
    h = hashlib.sha256()
    for rel in sorted(p for p in payload if isinstance(p, str)):
        fp = os.path.join(pack_dir, rel)
        if os.path.isfile(fp):
            with open(fp, "rb") as f:
                h.update(rel.encode("utf-8"))
                h.update(f.read())
    return "sha256:" + h.hexdigest()


def _identity_material(author, form, model, task_id, pdigest):
    return ("|".join([author, form, model or "", task_id or "", pdigest])).encode("utf-8")


def _identity_sig(author, form, model, task_id, pdigest):
    mat = _identity_material(author, form, model, task_id, pdigest)
    key = _author_key(author)
    if key:
        return "hmac-sha256:" + hmac.new(key, mat, hashlib.sha256).hexdigest(), True
    return "sha256:" + hashlib.sha256(mat).hexdigest(), False


def _load_payload(pack_dir):
    mp = os.path.join(pack_dir, MANIFEST_FILE)
    with open(mp, encoding="utf-8") as f:
        m = json.load(f)
    payload = m.get("payload") if isinstance(m.get("payload"), list) else []
    return m, payload


def sign(pack_dir, author, form, model=None, note=None):
    """Подписать пак: записать PROVENANCE.json."""
    author = str(author).upper()
    form = str(form).upper()
    if author not in AUTHORS:
        raise ValueError("неизвестный автор %r (нужен из %s)" % (author, sorted(AUTHORS)))
    if form not in FORMS:
        raise ValueError("неизвестная форма %r (нужна из %s)" % (form, sorted(FORMS)))
    m, payload = _load_payload(pack_dir)
    task_id = m.get("task_id")
    _ensure_key(author)  # создаст ключ, если настроен keystore
    pdigest = payload_digest(pack_dir, payload)
    isig, keyed = _identity_sig(author, form, model, task_id, pdigest)
    prov = {
        "schema_version": PROV_SCHEMA,
        "author": author,
        "form": form,
        "model": model,
        "task_id": task_id,
        "payload_signature": pdigest,
        "payload_count": len(payload),
        "identity_signature": isig,
        "keyed": keyed,
        "signed_utc": _utc(),
        "note": note,
    }
    with open(os.path.join(pack_dir, PROV_FILE), "w", encoding="utf-8") as f:
        json.dump(prov, f, ensure_ascii=False, indent=2)
    return prov


def verify(pack_dir):
    """Проверить подпись. Возвращает (ok, reasons, prov)."""
    reasons = []
    pf = os.path.join(pack_dir, PROV_FILE)
    if not os.path.isfile(pf):
        return False, ["PROVENANCE_MISSING: нет PROVENANCE.json — пак не подписан"], None
    try:
        with open(pf, encoding="utf-8") as f:
            prov = json.load(f)
    except Exception as exc:
        return False, ["PROVENANCE_UNPARSEABLE: %s" % exc], None
    if prov.get("schema_version") != PROV_SCHEMA:
        reasons.append("PROVENANCE_SCHEMA_BAD: %r" % prov.get("schema_version"))
    author = prov.get("author")
    form = prov.get("form")
    if author not in AUTHORS:
        reasons.append("AUTHOR_UNKNOWN: %r не из %s" % (author, sorted(AUTHORS)))
    if form not in FORMS:
        reasons.append("FORM_UNKNOWN: %r не из %s" % (form, sorted(FORMS)))
    try:
        m, payload = _load_payload(pack_dir)
        actual = payload_digest(pack_dir, payload)
        if prov.get("payload_signature") != actual:
            reasons.append("SIGNATURE_MISMATCH: payload изменён после подписи (tamper)")
        else:
            # проверяем привязку личности
            exp, keyed = _identity_sig(author or "", form or "", prov.get("model"),
                                       prov.get("task_id"), actual)
            if prov.get("keyed") and not keyed:
                reasons.append("KEY_MISSING: подпись keyed, но ключ автора недоступен")
            elif prov.get("identity_signature") != exp:
                reasons.append("IDENTITY_MISMATCH: автор/форма/модель не сходятся с подписью")
    except Exception as exc:
        reasons.append("PAYLOAD_UNREADABLE: %s" % exc)
    return (len(reasons) == 0), reasons, prov


def main(argv=None):
    ap = argparse.ArgumentParser(description="IMPERIUM provenance v0_2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("sign", help="подписать пак")
    ps.add_argument("pack_dir")
    ps.add_argument("--author", required=True)
    ps.add_argument("--form", required=True)
    ps.add_argument("--model")
    ps.add_argument("--note")
    pv = sub.add_parser("verify", help="проверить подпись")
    pv.add_argument("pack_dir")
    args = ap.parse_args(argv)

    if args.cmd == "sign":
        prov = sign(args.pack_dir, args.author, args.form, args.model, args.note)
        print("ПОДПИСАНО:", json.dumps(prov, ensure_ascii=False))
        return 0
    ok, reasons, prov = verify(args.pack_dir)
    print("=" * 56)
    print("  PROVENANCE VERIFY :", args.pack_dir)
    if prov:
        print("  author/form/model :", "%s / %s / %s" % (prov.get("author"), prov.get("form"), prov.get("model")))
        print("  keyed             :", prov.get("keyed"))
    print("  VERDICT           :", "OK" if ok else "FAIL")
    for r in reasons:
        print("    -", r)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
