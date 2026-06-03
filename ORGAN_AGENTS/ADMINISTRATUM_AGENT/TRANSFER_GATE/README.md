# Administratum Transfer Gate V0.1

Administratum Transfer Gate V0.1 is a manual, script-first transfer clerk for
Logos prompt packs and VM2 response bundles.

It does not move private context into Git. Runtime packages, receipts, ledgers,
quarantine copies, and fetched response evidence belong under the configurable
transfer root. On VM2 the default root is:

```text
/home/vboxuser2/IMPERIUM_CONTEXT/LOCAL/ADMINISTRATUM_TRANSFER/
```

Required runtime folders:

```text
INBOX/PC_TO_VM2/
OUTBOX/VM2_TO_PC/
RECEIVED/VM2/
LEDGER/
QUARANTINE/
```

## Commands

Standalone scripts:

```bash
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_verify_bundle_v0_1.py <prompt_pack.zip>
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_send_vm2_v0_1.py <prompt_pack.zip> --step-name "<human step name>"
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TRANSFER_GATE/SCRIPTS/transfer_fetch_vm2_v0_1.py --task-id <TASK_ID> --expected-filename <TASK_ID>__VM2_RESPONSE_BUNDLE.zip
```

Administratum runner aliases:

```bash
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-verify-pack --pack-zip <prompt_pack.zip>
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-send-vm2 --pack-zip <prompt_pack.zip> --step-name "<human step name>"
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-fetch-vm2 --task-id <TASK_ID> --expected-filename <TASK_ID>__VM2_RESPONSE_BUNDLE.zip
python3 IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-status
```

## V0.1 Behavior

- Verify prompt pack ZIP membership and SHA256SUMS.
- Check `task_pack.json.creation_gate.owner_trigger_phrase_exact == "Пиши промт"` and
  `trigger_phrase_verified_by_logos == true`. Missing gate metadata is WARN in
  V0.1, not an automatic hard fail.
- Stamp a transfer receipt with transfer ID, correlation ID, source/target actors,
  step name, payload hash, source HEAD, and UTC signing time.
- Copy signed prompt packs into `RECEIVED/VM2/<task_id>/`.
- Append compact JSONL ledger entries under `LEDGER/transfer_ledger_v0_1.jsonl`.
- Fetch VM2 response bundles only by exact expected filename.
- Verify response bundle metadata against task ID and optional correlation ID.
- Copy invalid or mismatched bundles to `QUARANTINE/<task_id>/`.

## Script Maturity

The V0.1 scripts are classified as `TASK_LOCAL` moving toward `REUSABLE_TOOL`.
They are typed, stdlib-only, and covered by a synthetic end-to-end test, but no
strict type checker evidence is claimed in this task.
