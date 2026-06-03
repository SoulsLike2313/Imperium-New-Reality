# Administratum-Agent V1 Hardened

Administratum-Agent V1 is the first full Organ-Agent implementation in IMPERIUM_NEW_GENERATION.
Current state is hardened toward reference-grade local execution.

Mission:
- inspect repository structure;
- classify zones/artifacts;
- build provenance index;
- detect dirty runtime outputs;
- produce useful candidate and merge-preparation intelligence;
- route findings to relevant organs;
- scan/classify IMPERIUM_CONTEXT in metadata-only mode;
- collect continuity pack and reality snapshot artifacts;
- build KPD/thinking-quality and Control Unit (цушки) summary;
- verify, stamp, push, fetch, ledger, quarantine, and prove manual PC-to-VM2 transfer bundles.

Scope:
- sandbox-only (`IMPERIUM_NEW_GENERATION`);
- no canon fusion;
- no direct deletion/merge/promotion.

Runtime discipline:
- all command outputs go to `IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/<run_id>/` by default;
- Transfer Gate runtime bundles/ledgers stay outside Git under `ADMINISTRATUM_TRANSFER`;
- PC-side `transfer-push-vm2` requires fresh remote SHA256 and size proof before PASS;
- machine truth remains JSON/JSONL receipts and reports.

Interactive shell:
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py shell`

Transfer Gate:
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-verify-pack --pack-zip <prompt_pack.zip>`
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-send-vm2 --pack-zip <prompt_pack.zip> --step-name "<human step name>"`
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-push-vm2 --pack-zip <prompt_pack.zip> --step-name "<human step name>"`
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color transfer-fetch-vm2 --pc-remote --task-id <TASK_ID> --expected-filename <TASK_ID>__VM2_RESPONSE_BUNDLE.zip`
