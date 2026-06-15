#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP ZONE ENGINE (V0.1)

The warp zone is the hot workroom. When any task starts, a WarpSession is
opened. EVERYTHING that participates — organs, servitors, kernel reads, API,
CLI — is registered as a participant and operates inside this session's
workdir. The kernel stays clean because:

  * the kernel is a READ-ONLY baseline,
  * writes land in  WARP/runtime/<session>/artifacts/ ,
  * a staged change carries its target zone + diff, but is NEVER applied to the
    kernel by the warp; only a gated RELEASE plan can promote it (owner-gated).

Stages:  INTAKE -> PLAN -> BUILD -> VALIDATE -> GATE -> (RELEASED | HELD | DISCARDED)

Stdlib only.
"""
import json
import os
import time
import uuid

from warp_eventlog import EventLog
import warp_overlay as overlay
import warp_gate as gate

STAGES = ["INTAKE", "PLAN", "BUILD", "VALIDATE", "GATE", "RELEASED", "HELD", "DISCARDED"]
KINDS = ["CORE_CHANGE", "IMPERIUM_FORCE", "THIRD_PARTY"]


class WarpSession:
    def __init__(self, task, kind="THIRD_PARTY", core_root=None, warp_root=None,
                 trigger="manual"):
        if kind not in KINDS:
            raise ValueError("unknown kind: %s" % kind)
        self.id = "WARP-" + time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.task = task
        self.kind = kind
        self.trigger = trigger  # 'manual' (button) or 'auto' (task-start hook)
        self.core_root = core_root  # read-only baseline; may be None in sample
        package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.warp_root = warp_root or os.path.join(package_root, "runtime")
        self.workdir = os.path.join(self.warp_root, self.id)
        self.artifacts = os.path.join(self.workdir, "artifacts")
        os.makedirs(self.artifacts, exist_ok=True)
        self.log = EventLog(os.path.join(self.workdir, "events.jsonl"))
        self.stage = "INTAKE"
        self.participants = []      # organs, servitors, api, cli, kernel-read
        self.plan = []              # ordered steps
        self.criteria = []          # definition-of-done
        self.metrics = {}           # metric_id -> {value, evidence_level, ...}
        self.changes = []           # staged diffs
        self.gate_result = None
        self.release_plan = None
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.log.append("session_open", id=self.id, task=task, kind=kind,
                        trigger=trigger, core_root=core_root)

    # ---- participants -------------------------------------------------
    def register(self, kind, name, mode="read", detail=None):
        """kind: organ|servitor|kernel|api|cli|tool ; mode: read|dry-run|real"""
        p = {"kind": kind, "name": name, "mode": mode, "detail": detail}
        self.participants.append(p)
        self.log.append("participant_register", **p)
        return p

    # ---- plan & criteria ---------------------------------------------
    def set_plan(self, steps):
        self.plan = list(steps)
        self.log.append("plan_set", steps=self.plan)

    def set_criteria(self, criteria):
        self.criteria = list(criteria)
        self.log.append("criteria_set", criteria=self.criteria)

    def record_metric(self, metric_id, value, evidence_level="E1",
                      claimed_pass=None, note=None, source=None, **extra):
        m = {"value": value, "evidence_level": evidence_level}
        if claimed_pass is not None:
            m["claimed_pass"] = claimed_pass
        if note is not None:
            m["note"] = note
        if source is not None:
            m["source"] = source
        if extra:
            m.update(extra)
        self.metrics[metric_id] = m
        self.log.append("metric", metric=metric_id, **m)
        return m

    # ---- the only way to 'write' -------------------------------------
    def write_artifact(self, relpath, content, target_zone=None):
        """Write a product/waste artifact INTO the warp workdir only.
        If target_zone is provided we stage a diff vs the kernel baseline,
        but we DO NOT touch the kernel. CORE-zone targets can only ever be
        promoted later through a gated release plan.
        """
        safe = relpath.replace("\\", "/").lstrip("/")
        dest = os.path.abspath(os.path.join(self.artifacts, safe))
        artifacts_root = os.path.abspath(self.artifacts)
        if os.path.commonpath([artifacts_root, dest]) != artifacts_root:
            raise ValueError("artifact path escapes WARP runtime")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(content)
        zone = target_zone or overlay.classify_zone(safe)
        old = overlay.baseline_text(self.core_root, safe) if self.core_root else ""
        change = {
            "path": safe,
            "zone": zone,
            "stats": overlay.diff_stats(old, content),
            "new_sha256": overlay.sha256_text(content),
            "diff": overlay.unified_diff(old, content, safe),
            "applied_to_kernel": False,
        }
        self.changes.append(change)
        self.log.append("artifact_write", path=safe, zone=zone,
                        stats=change["stats"])
        return change

    # ---- stage machine -----------------------------------------------
    def advance(self, stage):
        if stage not in STAGES:
            raise ValueError("unknown stage: %s" % stage)
        self.stage = stage
        self.log.append("stage", stage=stage)

    # ---- gate --------------------------------------------------------
    def run_gate(self, min_evidence="E3"):
        self.advance("GATE")
        res = gate.evaluate(self.criteria, self.metrics, min_evidence=min_evidence)
        self.gate_result = res
        self.log.append("gate", **res)
        return res

    def release(self):
        """Emit a gated promotion plan. Does NOT modify the kernel: produces a
        release_manifest the owner/Mechanicus must approve and apply."""
        if not self.gate_result or self.gate_result["verdict"] != "RELEASE":
            raise RuntimeError("release blocked: gate verdict is %s" %
                               (self.gate_result or {}).get("verdict"))
        self.advance("RELEASED")
        plan = {
            "release_id": "REL-" + self.id,
            "session": self.id,
            "task": self.task,
            "kind": self.kind,
            "status": "MANIFEST_ONLY_PENDING_FUTURE_OWNER_GATE",
            "kernel_touched": False,
            "automatic_kernel_promotion": False,
            "promotions": [
                {"path": c["path"], "zone": c["zone"],
                 "new_sha256": c["new_sha256"], "stats": c["stats"]}
                for c in self.changes
            ],
            "requires": ["OWNER_APPROVAL",
                         "MOVE_DELETE_APPROVAL_GATE if CORE zone"],
        }
        path = os.path.join(self.workdir, "release_manifest.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False, indent=2)
        self.release_plan = plan
        self.log.append("release_plan", release_id=plan["release_id"],
                        promotions=len(plan["promotions"]))
        return plan

    def discard(self, reason=""):
        """Reject the product and retain runtime evidence. Kernel stays clean."""
        self.advance("DISCARDED")
        receipt = {
            "session": self.id, "task": self.task, "reason": reason,
            "gate": self.gate_result, "kernel_touched": False,
            "discarded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        path = os.path.join(self.workdir, "discard_receipt.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, ensure_ascii=False, indent=2)
        self.log.append("discard", reason=reason)
        return receipt

    def hold(self, reason=""):
        self.advance("HELD")
        self.log.append("hold", reason=reason)

    # ---- manifest ----------------------------------------------------
    def manifest(self):
        return {
            "id": self.id, "task": self.task, "kind": self.kind,
            "trigger": self.trigger, "stage": self.stage,
            "created_at": self.created_at, "core_root": self.core_root,
            "workdir": self.workdir,
            "participants": self.participants, "plan": self.plan,
            "criteria": self.criteria, "metrics": self.metrics,
            "changes": [{k: v for k, v in c.items() if k != "diff"}
                        for c in self.changes],
            "gate_result": self.gate_result,
            "release": self.release_plan,
        }

    def save_manifest(self):
        path = os.path.join(self.workdir, "session_manifest.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.manifest(), fh, ensure_ascii=False, indent=2)
        return path
