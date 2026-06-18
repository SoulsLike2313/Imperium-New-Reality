#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADMINISTRATUM continuity-pack assembler v0_1.

Собирает верный КОНТИНЬЮИТИ-ПАК: живые факты репо (git HEAD/branch/remote,
наличие 9 органов + Трон + governance) + курируемая доктрина
(IMPERIUM_CONTINUITY_SOURCE.md) => CONTINUITY_PACK/ { CONTINUITY_MANIFEST.json, IMPERIUM_HANDOFF.md }.
Цель: в новом чате любой LLM/CLI-агент продолжает без обрывов и грязи.
Чистый stdlib. Evidence: E3_EXECUTED.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

SCHEMA_VERSION = "imperium.continuity_pack.v0_1"
PROVENANCE = "ADMINISTRATUM continuity assembler v0_1; E3_EXECUTED"
CANON_ORGANS = [
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM",
    "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
    "STRATEGIUM",
]
GOV_FILES = [
    "REQUIRED_9_ORGANS_V0_1.json",
    "CORE_SHAPE_CONTRACT_V0_1.md",
    "GOVERNANCE_INDEX.json",
]


def _git(reality_root, args):
    try:
        out = subprocess.run(
            ["git", "-C", reality_root] + args,
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def assemble(reality_root, role, source_path, out_dir, git_url=None):
    reasons = []
    organs_root = os.path.join(reality_root, "ORGANS")
    cg = os.path.join(organs_root, "_CORE_GOVERNANCE")

    head = _git(reality_root, ["rev-parse", "HEAD"])
    branch = _git(reality_root, ["rev-parse", "--abbrev-ref", "HEAD"])
    remote = git_url or _git(reality_root, ["config", "--get", "remote.origin.url"])
    subject = _git(reality_root, ["log", "-1", "--pretty=%s"])
    if not head:
        reasons.append({"gate": "GIT", "code": "GIT_HEAD_UNAVAILABLE",
                        "message": "git HEAD не получен — это не git-репозиторий?"})

    organs = []
    for o in CANON_ORGANS:
        od = os.path.join(organs_root, o)
        present = os.path.isdir(od)
        has_card = os.path.isfile(os.path.join(od, "ORGAN_CARD.json"))
        has_contract = os.path.isfile(os.path.join(od, "ORGAN_CONTRACT.md"))
        organs.append({"organ": o, "present": present,
                       "organ_card": has_card, "organ_contract": has_contract})
        if not present:
            reasons.append({"gate": "ORGANS", "code": "ORGAN_MISSING",
                            "message": "нет директории органа: %s" % o})
        elif not (has_card and has_contract):
            reasons.append({"gate": "ORGANS", "code": "ORGAN_FORM_INCOMPLETE",
                            "message": "%s: нет ORGAN_CARD.json/ORGAN_CONTRACT.md" % o})

    throne_present = (
        os.path.isfile(os.path.join(cg, "THRONE", "THRONE_GATEWAY_CONTRACT_V0_1.md"))
        and os.path.isfile(os.path.join(cg, "THRONE", "throne_gateway_descriptor.json"))
    )
    if not throne_present:
        reasons.append({"gate": "THRONE", "code": "THRONE_BASE_MISSING",
                        "message": "нет базы Трона (contract/descriptor)"})

    gov = {}
    for g in GOV_FILES:
        ok = os.path.isfile(os.path.join(cg, g))
        gov[g] = ok
        if not ok:
            reasons.append({"gate": "GOVERNANCE", "code": "GOV_FILE_MISSING",
                            "message": "нет governance-файла: %s" % g})

    if not os.path.isfile(source_path):
        reasons.append({"gate": "SOURCE", "code": "SOURCE_MISSING",
                        "message": "нет IMPERIUM_CONTINUITY_SOURCE.md"})
        source_text = ""
    else:
        with open(source_path, encoding="utf-8") as f:
            source_text = f.read()

    verdict = "CONTINUITY_OK" if not reasons else "CONTINUITY_INCOMPLETE"
    assembled = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs(out_dir, exist_ok=True)
    header = "\n".join([
        "# IMPERIUM — LLM CONTINUITY HANDOFF",
        "",
        "> Auto-stamped by ADMINISTRATUM continuity assembler v0_1. Do not edit by hand.",
        "",
        "- role: %s" % role,
        "- git_head: %s" % (head or "UNAVAILABLE"),
        "- git_branch: %s" % (branch or "UNAVAILABLE"),
        "- git_remote: %s" % (remote or "UNAVAILABLE"),
        "- head_subject: %s" % (subject or "UNAVAILABLE"),
        "- assembled_utc: %s" % assembled,
        "- completeness: %s" % verdict,
        "",
        "---",
        "",
        "",
    ])
    handoff_path = os.path.join(out_dir, "IMPERIUM_HANDOFF.md")
    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(header + source_text)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "assembled_by": "ADMINISTRATUM",
        "role": role,
        "assembled_utc": assembled,
        "git": {"head": head, "branch": branch, "remote": remote, "head_subject": subject},
        "organs": organs,
        "throne": {"present": throne_present},
        "governance_files": gov,
        "pointers": {
            "handoff": "IMPERIUM_HANDOFF.md",
            "reality_root": reality_root,
            "warp_tools": "HARNESS\\TOOLS\\WARP",
            "astra_gate": "ORGANS\\ASTRONOMICON\\TOOLS\\astra_gate.py",
            "throne_contract": "ORGANS\\_CORE_GOVERNANCE\\THRONE\\THRONE_GATEWAY_CONTRACT_V0_1.md",
        },
        "completeness": {"verdict": verdict, "reasons": reasons},
        "evidence_level": "E3_EXECUTED",
        "provenance": PROVENANCE,
    }
    body = _sha256_file(handoff_path).encode() + json.dumps(
        manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")
    manifest["pack_digest"] = "sha256:" + hashlib.sha256(body).hexdigest()
    manifest_path = os.path.join(out_dir, "CONTINUITY_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return verdict, reasons, manifest, manifest_path


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="ADMINISTRATUM continuity-pack assembler v0_1")
    ap.add_argument("--reality-root", required=True, help="корень IMPERIUM_REALITY")
    ap.add_argument("--role", default="LOGOS_PRIME", help="роль LLM (по умолчанию LOGOS_PRIME)")
    ap.add_argument("--source", default=os.path.join(here, "IMPERIUM_CONTINUITY_SOURCE.md"),
                    help="курируемая доктрина-источник")
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "CONTINUITY_PACK"),
                    help="куда собрать пак")
    ap.add_argument("--git-url", default=None, help="явная git-ссылка (перекрывает remote.origin.url)")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.reality_root):
        sys.stderr.write("ERROR: нет директории reality-root: %s\n" % args.reality_root)
        return 1

    verdict, reasons, manifest, manifest_path = assemble(
        args.reality_root, args.role, args.source, args.out, args.git_url)

    print("=" * 60)
    print("  ADMINISTRATUM CONTINUITY ASSEMBLER v0_1")
    print("  reality : %s" % args.reality_root)
    print("  role    : %s" % args.role)
    print("  git_head: %s" % (manifest["git"]["head"] or "UNAVAILABLE"))
    print("  out     : %s" % args.out)
    print("  digest  : %s" % manifest.get("pack_digest"))
    print("=" * 60)
    if reasons:
        for r in reasons:
            print("  [%-11s] %-22s %s" % (r["gate"], r["code"], r["message"]))
    else:
        print("  все ворота чистые: 9 органов + Трон + governance + источник")
    print("-" * 60)
    print("  VERDICT : %s" % verdict)
    print("  manifest: %s" % manifest_path)
    return 0 if verdict == "CONTINUITY_OK" else 2


if __name__ == "__main__":
    sys.exit(main())
