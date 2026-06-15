# Owner Quickstart V0.1

## Goal
Use the hardened Administratum operator contract with compact default outputs and machine-stable JSON.

## Fast checks
1. Status (compact operator contract)
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color status`

2. Machine JSON
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --plain-json --no-color status`

3. Verbose diagnostics
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --verbose --no-color status`

4. Rich diagnosis
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color doctor-rich`

5. Continuity maturity capsule
- `python IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/TOOLS/administratum_agent_runner.py --no-color collect-continuity-pack --include-context true --inventory-max-files 900 --provenance-limit 220`

## Compact output contract shape (human mode)
```text
STATUS: PASS|WARN|FAIL|BLOCKED
COMMAND: <name>
SUMMARY:
  - <1..3 lines>
PRIMARY_REFS:
  - <path/ref>
ARTIFACTS_WRITTEN:
  - <path>
WARNINGS:
  - <warning or NONE>
WHY_TRUST:
  - <evidence lines>
NEXT_ACTIONS:
  - <next step>
LIMITATIONS:
  - <none or limitations>
```

## Machine JSON minimum fields
```json
{
  "status": "...",
  "command": "...",
  "summary": "...",
  "primary_refs": [],
  "artifacts_written": [],
  "warnings": [],
  "why_trust": [],
  "next_actions": [],
  "metrics": {},
  "limitations": []
}
```

## Continuity maturity capsule file
- Path:
  - `<run_dir>/continuity_pack/continuity_maturity_capsule.json`
- Key field:
  - `self_verdict` in:
    - `NOT_READY_FOR_SOLE_HANDOFF`
    - `PARTIAL`
    - `READY_CANDIDATE`
