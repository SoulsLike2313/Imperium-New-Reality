#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP EVENT LOG (V0.1)

Append-only JSONL ledger for a WARP session. Every state change in the warp
zone is recorded here so the IDE can replay stages, diffs, metrics and gate
decisions. Append-only => you cannot silently rewrite history (anti fake-green).
"""
import json
import os
import time


class EventLog:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8"):
                pass

    def append(self, event_type, **fields):
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event_type}
        rec.update(fields)
        line = json.dumps(rec, ensure_ascii=False)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return rec

    def read(self):
        out = []
        if not os.path.exists(self.path):
            return out
        with open(self.path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def by_type(self, event_type):
        return [e for e in self.read() if e.get("event") == event_type]
