#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASTRONOMICON servitor intake v0_1.

Застава допуска Сервитора (GROK / CODEX) к репозиторию REALITY.
Правило: ни один Сервитор не вправе писать в репо без ДОПУЩЕННОГО (ADMIT)
и привязанного по payload-digest таск-пака. Переиспользует канонический
`astra_gate` как единственный источник правды по валидации формы пака
(FORM / COMPLETENESS / CORRECTNESS).

Две команды:
  admit  — прогнать пак через вход Астры; при ADMIT выдать токен допуска;
  check  — проверить, вправе ли сейчас сервитор работать по паку
           (digest-binding: пак не должен меняться после допуска).

Чистый stdlib. Evidence: E3_EXECUTED (реальный запуск).
"""
import argparse
import csv
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import astra_gate  # канонический входной шлюз — единственный источник правды

SCHEMA_VERSION = "imperium.servitor_admission.v0_1"
PROVENANCE = "ASTRONOMICON servitor intake v0_1; E3_EXECUTED; permit deferred to THRONE"
VALID_SERVITORS = {"GROK", "CODEX"}


def _admissions_dir(reality_root):
    return os.path.join(reality_root, "ORGANS", "ASTRONOMICON", "ADMISSIONS")


def _token_path(reality_root, task_id, servitor):
    return os.path.join(_admissions_dir(reality_root),
                        "%s__%s.admission.json" % (task_id, servitor))


def _append_ledger(reality_root, row):
    path = os.path.join(_admissions_dir(reality_root), "LEDGER.csv")
    new = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp_utc", "task_id", "servitor", "verdict", "payload_digest"])
        w.writerow(row)


def _header(title, pack, receipt, servitor):
    print("=" * 60)
    print("  %s" % title)
    print("  servitor : %s" % servitor)
    print("  pack     : %s" % pack)
    print("  task_id  : %s" % receipt.get("task_id"))
    print("  organ    : %s" % receipt.get("target_organ"))
    print("  digest   : %s" % receipt.get("payload_digest"))
    print("=" * 60)


def cmd_admit(args):
    servitor = args.servitor.upper()
    if servitor not in VALID_SERVITORS:
        sys.stderr.write("ERROR: неизвестный сервитор %r (нужно: %s)\n"
                         % (args.servitor, sorted(VALID_SERVITORS)))
        return 1
    if not os.path.isdir(args.pack_dir):
        sys.stderr.write("ERROR: нет директории пака: %s\n" % args.pack_dir)
        return 1

    verdict, reasons, receipt = astra_gate.validate(args.pack_dir)
    receipt["servitor"] = servitor
    receipt["intake_schema"] = SCHEMA_VERSION
    receipt["intake_provenance"] = PROVENANCE
    receipt["pack_dir"] = os.path.abspath(args.pack_dir)

    _header("SERVITOR INTAKE — ADMIT", args.pack_dir, receipt, servitor)
    if reasons:
        for r in reasons:
            print("  [%-12s] %-22s %s" % (r["gate"], r["code"], r["message"]))
    else:
        print("  все ворота чистые")
    print("-" * 60)

    os.makedirs(_admissions_dir(args.reality_root), exist_ok=True)
    if verdict == "ADMIT":
        tok = _token_path(args.reality_root, receipt.get("task_id"), servitor)
        with open(tok, "w", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2)
        _append_ledger(args.reality_root, [receipt["timestamp_utc"],
                       receipt.get("task_id"), servitor, "ADMIT",
                       receipt.get("payload_digest")])
        print("  VERDICT     : ADMIT")
        print("  TOKEN       : %s" % tok)
        print("  -> Сервитор %s ДОПУЩЕН к работе по этому паку (digest привязан)." % servitor)
        return 0

    _append_ledger(args.reality_root, [receipt["timestamp_utc"],
                   receipt.get("task_id"), servitor, "REJECT",
                   receipt.get("payload_digest")])
    print("  VERDICT     : REJECT")
    print("  -> RETURN_TO_SUBMITTER. Токен НЕ выдан. Сервитор работать не вправе.")
    return 2


def cmd_check(args):
    servitor = args.servitor.upper()
    if servitor not in VALID_SERVITORS:
        sys.stderr.write("ERROR: неизвестный сервитор %r\n" % args.servitor)
        return 1
    if not os.path.isdir(args.pack_dir):
        sys.stderr.write("ERROR: нет директории пака: %s\n" % args.pack_dir)
        return 1

    verdict, reasons, cur = astra_gate.validate(args.pack_dir)
    task_id = cur.get("task_id")
    cur_digest = cur.get("payload_digest")

    print("=" * 60)
    print("  SERVITOR WORK-PERMIT CHECK")
    print("  servitor : %s" % servitor)
    print("  pack     : %s" % args.pack_dir)
    print("  task_id  : %s" % task_id)
    print("  digest   : %s" % cur_digest)
    print("=" * 60)

    deny = None
    if verdict != "ADMIT":
        deny = ("PACK_INVALID", "пак не проходит вход Астры (прогони astra_gate)")
    else:
        tok = _token_path(args.reality_root, task_id, servitor)
        if not os.path.isfile(tok):
            deny = ("NO_ADMISSION", "нет admission-токена для task_id+servitor — пак не допускался")
        else:
            with open(tok, encoding="utf-8") as f:
                t = json.load(f)
            if t.get("verdict") != "ADMIT":
                deny = ("NOT_ADMITTED", "токен есть, но verdict != ADMIT")
            elif t.get("servitor") != servitor:
                deny = ("SERVITOR_MISMATCH", "токен выдан другому сервитору: %s" % t.get("servitor"))
            elif t.get("payload_digest") != cur_digest:
                deny = ("DIGEST_MISMATCH", "пак изменён после допуска — digest не совпадает")

    print("-" * 60)
    if deny is None:
        print("  VERDICT : WORK_PERMITTED")
        print("  -> Сервитор %s вправе работать по task_id=%s." % (servitor, task_id))
        return 0
    print("  [DENY] %-18s %s" % (deny[0], deny[1]))
    print("  VERDICT : WORK_DENIED")
    print("  -> Сначала получи ADMIT через 'admit'. Без токена Сервитор не работает.")
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASTRONOMICON servitor intake v0_1")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("admit", help="вход Астры + при ADMIT выдать токен допуска сервитору")
    pa.add_argument("pack_dir")
    pa.add_argument("--servitor", required=True, help="GROK | CODEX")
    pa.add_argument("--reality-root", required=True)
    pa.set_defaults(func=cmd_admit)

    pc = sub.add_parser("check", help="вправе ли сервитор работать по паку (digest-binding)")
    pc.add_argument("pack_dir")
    pc.add_argument("--servitor", required=True)
    pc.add_argument("--reality-root", required=True)
    pc.set_defaults(func=cmd_check)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
