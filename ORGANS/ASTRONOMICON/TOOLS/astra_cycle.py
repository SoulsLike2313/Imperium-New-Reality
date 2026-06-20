#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASTRONOMICON cycle orchestrator v0_1.

Полный цикл КОНВЕЙЕРА для патч-пака/таск-пака:
  1) INBOUND   — astra_gate.validate (FORM/COMPLETENESS/CORRECTNESS) -> ADMIT|REJECT
  2) PERMIT    — верховный permit Трона (здесь: входной параметр)
  3) WARP_START— git worktree от trunk (изолированная зона)
  4) INTEGRATE — раскладка payload по integration.map
  5) COMMIT    — коммит в ветке задачи
  6) LAND      — merge --squash в trunk (автор WARP/<task>) + push (если есть remote)
  7) RECEIPT   — imperium.astra_work_receipt.v0_1

Чистый stdlib + git. Evidence: E3_EXECUTED (реальный git).
Переносим (любая машина с python+git) — не зависит от pwsh.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import astra_gate  # noqa: E402
import imperium_provenance as prov  # noqa: E402

WORK_RECEIPT_SCHEMA = "imperium.astra_work_receipt.v0_1"
PROVENANCE = "ASTRONOMICON cycle orchestrator v0_1; E3_EXECUTED"


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(s):
    out = re.sub(r"[^A-Z0-9]+", "-", str(s).upper()).strip("-")
    return out[:48].strip("-") or "TASK"


def _git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = r.stdout or ""
    err = r.stderr or ""
    if check and r.returncode != 0:
        raise RuntimeError("git %s -> %s\n%s" % (" ".join(args), r.returncode, err.strip()))
    return out.strip(), r.returncode


def _sha256_file(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as f:
        h.update(f.read())
    return "sha256:" + h.hexdigest()


class Cycle:
    def __init__(self, pack, reality, trunk, throne_permit, apply, log,
                 contour="WINDOWS_PC", memory_index=None):
        self.pack = os.path.abspath(pack)
        self.reality = os.path.abspath(reality)
        self.trunk = trunk
        self.throne_permit = throne_permit
        self.apply = apply
        self.log = log
        self.contour = contour
        self.memory_index = memory_index
        self.stages = []

    def say(self, s):
        self.log.append(str(s))
        print(s)

    def stage(self, name, status, detail=None):
        self.stages.append({"stage": name, "status": status, "detail": detail})
        self.say("  [%-10s] %-10s %s" % (name, status, detail or ""))

    def run(self):
        self.say("=" * 64)
        self.say("  ASTRONOMICON CYCLE v0_1   mode=%s" % ("APPLY" if self.apply else "DRYRUN"))
        self.say("  pack    : %s" % self.pack)
        self.say("  reality : %s   trunk=%s" % (self.reality, self.trunk))
        self.say("=" * 64)

        # 1) INBOUND
        verdict, reasons, adm = astra_gate.validate(self.pack)
        self.admission = adm
        if verdict != "ADMIT":
            self.stage("INBOUND", "REJECT", "%d причин" % len(reasons))
            for r in reasons:
                self.say("      - [%s] %s %s" % (r["gate"], r["code"], r["message"]))
            return self.finish("CYCLE_REJECTED_INBOUND", None, None, [], None)
        self.stage("INBOUND", "ADMIT", "digest=%s" % adm["payload_digest"][:23])

        # 1b) PROVENANCE — подпись автора (Warp-Zone Work)
        ok_sig, sig_reasons, prov_rec = prov.verify(self.pack)
        self.provenance = prov_rec
        if not ok_sig:
            self.stage("PROVENANCE", "REJECT", "; ".join(sig_reasons))
            return self.finish("CYCLE_REJECTED_PROVENANCE", None, None, [], None)
        self.stage("PROVENANCE", "OK", "%s/%s" % (prov_rec.get("author"), prov_rec.get("form")))

        # manifest
        with open(os.path.join(self.pack, "TASK_MANIFEST.json"), encoding="utf-8") as f:
            man = json.load(f)
        self.man = man
        task_id = man["task_id"]
        integ = man.get("integration") or {}
        imap = integ.get("map") or {}
        if not imap:
            self.stage("PRECHECK", "FAIL", "нет integration.map — нечего интегрировать")
            return self.finish("CYCLE_FAIL_NO_INTEGRATION", task_id, None, [], None)

        # 2) PERMIT (Трон)
        if self.throne_permit != "GRANTED":
            self.stage("PERMIT", "DENIED", "throne_permit=%s" % self.throne_permit)
            return self.finish("CYCLE_BLOCKED_NO_PERMIT", task_id, None, [], None)
        self.stage("PERMIT", "GRANTED", "THRONE")

        slug = _slug(task_id)
        branch = "warp/" + slug
        base_sha, _ = _git(self.reality, "rev-parse", self.trunk)

        if not self.apply:
            self.stage("PLAN", "DRYRUN", "branch=%s files=%d" % (branch, len(imap)))
            for s, d in sorted(imap.items()):
                self.say("      %s -> %s" % (s, d))
            return self.finish("CYCLE_DRYRUN_OK", task_id, base_sha, [], branch)

        wt = os.path.join(self.reality, "..", "_warp_" + slug)
        wt = os.path.abspath(wt)
        if os.path.exists(wt):
            shutil.rmtree(wt, ignore_errors=True)
        _git(self.reality, "worktree", "prune")
        _git(self.reality, "branch", "-D", branch, check=False)
        try:
            _git(self.reality, "worktree", "add", wt, "-b", branch, self.trunk)
        except RuntimeError as e:
            self.stage("WARP_START", "FAIL", str(e).splitlines()[0])
            return self.finish("CYCLE_FAIL_WARP_START", task_id, base_sha, [], branch)
        self.stage("WARP_START", "OK", "wt=%s" % os.path.basename(wt))

        # 4) INTEGRATE
        integrated = []
        for src, dst in sorted(imap.items()):
            sp = os.path.join(self.pack, src)
            dp = os.path.join(wt, dst)
            if not os.path.isfile(sp):
                self.stage("INTEGRATE", "FAIL", "нет файла payload: %s" % src)
                self._cleanup(wt, branch)
                return self.finish("CYCLE_FAIL_INTEGRATE", task_id, base_sha, integrated, branch)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(sp, dp)
            integrated.append({"dst": dst, "sha256": _sha256_file(dp)})
        self.stage("INTEGRATE", "OK", "%d файл(ов)" % len(integrated))

        # 4b) WARP_TEST — тесты прямо в warp-зоне (до COMMIT/LAND); FAIL => discard
        verify_spec = self.man.get("verify") or {}
        vcmd = verify_spec.get("cmd")
        if vcmd:
            vcwd = os.path.join(wt, verify_spec.get("cwd", "."))
            try:
                vr = subprocess.run(vcmd, cwd=vcwd, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace")
                self.warp_test_log = ((vr.stdout or "") + (vr.stderr or "")).strip()
                vrc = vr.returncode
            except Exception as exc:
                self.warp_test_log = "EXC: %s" % exc
                vrc = 1
            if vrc != 0:
                self.stage("WARP_TEST", "FAIL", "rc=%s — warp-зона удалена, main чист" % vrc)
                self._cleanup(wt, branch)
                return self.finish("CYCLE_FAIL_WARP_TEST", task_id, base_sha, integrated, branch)
            self.stage("WARP_TEST", "OK", "rc=0")
        else:
            self.stage("WARP_TEST", "SKIP", "нет verify.cmd")

        # 5) COMMIT в ветке (автор = подписант пака)
        _git(wt, "add", "-A")
        pr = getattr(self, "provenance", None) or {}
        author = pr.get("author") or man.get("submitted_by", "OWNER_MANUAL")
        sig_trailer = "Authored-by: %s (%s / %s)" % (
            author, pr.get("form") or "?", pr.get("model") or "-")
        cmsg = "%s: %s" % (slug, man.get("title", task_id))
        _git(wt, "-c", "user.name=%s" % author, "-c", "user.email=%s@imperium.local" % author.lower(),
             "commit", "-m", cmsg, "-m", sig_trailer)
        branch_sha, _ = _git(self.reality, "rev-parse", branch)
        self.stage("COMMIT", "OK", branch_sha[:12])

        # 6) LAND (squash)
        _git(self.reality, "checkout", self.trunk)
        cleared = self._clear_untracked_collisions(base_sha, branch)
        if cleared:
            self.stage("PRE_LAND", "OK", "снято untracked-коллизий: %d" % len(cleared))
        _git(self.reality, "merge", "--squash", branch)
        land_author = author
        body = "task: %s\nbranch: %s\nbase: %s\nlanded: %s\n%s\nidentity_sig: %s" % (
            task_id, branch, base_sha, _utc(), sig_trailer, pr.get("identity_signature") or "-")
        _git(self.reality, "-c", "user.name=%s" % land_author,
             "-c", "user.email=%s@imperium.local" % land_author.lower(),
             "commit", "-m", cmsg, "-m", body)
        land_sha, _ = _git(self.reality, "rev-parse", self.trunk)
        diffstat, _ = _git(self.reality, "diff", "--stat", "%s..%s" % (base_sha, land_sha))
        self.stage("LAND", "OK", "%s -> %s" % (base_sha[:12], land_sha[:12]))

        # push (если есть remote)
        remotes, _ = _git(self.reality, "remote", check=False)
        if remotes.strip():
            _out, rc = _git(self.reality, "push", "origin", self.trunk, check=False)
            self.stage("PUSH", "OK" if rc == 0 else "WARN", "origin %s" % self.trunk)
        else:
            self.stage("PUSH", "SKIP", "нет remote (локальный тест)")

        self._cleanup(wt, branch)
        return self.finish("CYCLE_OK", task_id, base_sha, integrated, branch,
                           land_sha=land_sha, diffstat=diffstat)

    def _clear_untracked_collisions(self, base_sha, branch):
        """Снять untracked-файлы в trunk, которые land перезапишет.
        Ветка warp автор��тетна (trunk + payload), поэтому снятие безопасно.
        Типовой случай — инструменты, заранее сложенные в рабочее дерево до их land."""
        incoming, _ = _git(self.reality, "diff", "--name-only",
                            "%s..%s" % (base_sha, branch), check=False)
        incoming_set = set(p.strip() for p in incoming.splitlines() if p.strip())
        if not incoming_set:
            return []
        status, _ = _git(self.reality, "status", "--porcelain",
                         "--untracked-files=all", check=False)
        removed = []
        for line in status.splitlines():
            if line.startswith("??"):
                rel = line[2:].strip().strip('"')
                if rel in incoming_set:
                    full = os.path.join(self.reality, rel.replace("/", os.sep))
                    try:
                        if os.path.isfile(full):
                            os.remove(full)
                            removed.append(rel)
                    except OSError:
                        pass
        return removed

    def _cleanup(self, wt, branch):
        _git(self.reality, "worktree", "remove", "--force", wt, check=False)
        _git(self.reality, "branch", "-D", branch, check=False)
        self.stage("CLEANUP", "OK", "worktree+branch")

    def finish(self, cycle_verdict, task_id, base_sha, integrated, branch,
               land_sha=None, diffstat=None):
        self.say("-" * 64)
        self.say("  CYCLE_VERDICT : %s" % cycle_verdict)
        receipt = {
            "schema_version": WORK_RECEIPT_SCHEMA,
            "gateway": "ASTRONOMICON",
            "stage": "CYCLE",
            "task_id": task_id,
            "title": getattr(self, "man", {}).get("title") if hasattr(self, "man") else None,
            "target_organ": getattr(self, "man", {}).get("target_organ") if hasattr(self, "man") else None,
            "submitted_by": getattr(self, "man", {}).get("submitted_by") if hasattr(self, "man") else None,
            "timestamp_utc": _utc(),
            "inbound_verdict": self.admission.get("verdict"),
            "payload_digest": self.admission.get("payload_digest"),
            "throne_permit": self.throne_permit,
            "branch": branch,
            "base_sha": base_sha,
            "land_sha": land_sha,
            "integrated": integrated,
            "diffstat": diffstat,
            "stages": self.stages,
            "author_provenance": getattr(self, "provenance", None),
            "warp_test_log": getattr(self, "warp_test_log", None),
            "cycle_verdict": cycle_verdict,
            "evidence_level": "E3_EXECUTED",
            "provenance": PROVENANCE,
        }
        # --- ГОВЕРНАНС: паспорт задачи (цепочка органов) ---
        prv = getattr(self, "provenance", None) or {}
        sender = "%s (%s / %s)" % (prv.get("author") or "?",
                                   prv.get("form") or "?", prv.get("model") or "-")
        landed = ("%s -> %s" % (base_sha[:12], land_sha[:12])) if (base_sha and land_sha) else "—"
        governance = {
            "received_from": prv.get("author"),
            "form": prv.get("form"),
            "model": prv.get("model"),
            "identity_signature": prv.get("identity_signature"),
            "contour": self.contour,
            "permit_by": "THRONE",
            "permit": self.throne_permit,
            "validated_by": "ASTRONOMICON",
            "memory_by": "ADMINISTRATUM",
        }
        receipt["governance"] = governance
        receipt["contour"] = self.contour
        self.say("-" * 64)
        self.say("  ПАСПОРТ ЗАДАЧИ : %s" % (task_id or "—"))
        self.say("    Пришёл от : %s" % sender)
        self.say("    Контур    : %s" % self.contour)
        self.say("    Пермит    : THRONE = %s" % self.throne_permit)
        self.say("    Валидация : ASTRONOMICON (gate INBOUND + WARP_TEST) -> %s" % cycle_verdict)
        self.say("    Память    : ADMINISTRATUM (индекс рецептов)")
        self.say("    Land      : %s" % landed)
        self.say("    Итог      : %s" % cycle_verdict)
        self.receipt = receipt
        # --- ПАМЯТЬ ADMINISTRATUM: append-only индекс ---
        if self.memory_index and task_id:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.memory_index)), exist_ok=True)
                mem = {
                    "timestamp_utc": receipt["timestamp_utc"],
                    "task_id": task_id,
                    "title": receipt.get("title"),
                    "received_from": governance["received_from"],
                    "form": governance["form"],
                    "model": governance["model"],
                    "contour": self.contour,
                    "target_organ": receipt.get("target_organ"),
                    "cycle_verdict": cycle_verdict,
                    "land_sha": land_sha,
                    "payload_digest": receipt.get("payload_digest"),
                }
                with open(self.memory_index, "a", encoding="utf-8") as mf:
                    mf.write(json.dumps(mem, ensure_ascii=False) + "\n")
                self.say("  ADMINISTRATUM memory += %s" % self.memory_index)
            except Exception as exc:
                self.say("  ADMINISTRATUM memory WARN: %s" % exc)
        return cycle_verdict, receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description="ASTRONOMICON cycle orchestrator v0_1")
    ap.add_argument("pack", help="корень патч/таск-пака (TASK_MANIFEST.json)")
    ap.add_argument("--reality", required=True, help="git-репо REALITY")
    ap.add_argument("--trunk", default="master")
    ap.add_argument("--throne-permit", default="GRANTED", help="GRANTED|DENIED (верховный permit Трона)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--receipt", help="куда записать WORK_RECEIPT.json")
    ap.add_argument("--receipt-txt", help="куда записать читаемый рецепт")
    ap.add_argument("--contour", default="WINDOWS_PC", help="исполнительный контур (где выполнена работа)")
    ap.add_argument("--memory-index", help="append-only индекс памяти ADMINISTRATUM (.jsonl)")
    args = ap.parse_args(argv)

    log = []
    c = Cycle(args.pack, args.reality, args.trunk, args.throne_permit, args.apply, log,
              contour=args.contour, memory_index=args.memory_index)
    cycle_verdict, receipt = c.run()

    if args.receipt:
        with open(args.receipt, "w", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2)
        print("  receipt     : %s" % args.receipt)
    if args.receipt_txt:
        with open(args.receipt_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(log) + "\n")
        print("  receipt_txt : %s" % args.receipt_txt)

    return 0 if cycle_verdict in ("CYCLE_OK", "CYCLE_DRYRUN_OK") else 2


if __name__ == "__main__":
    sys.exit(main())
