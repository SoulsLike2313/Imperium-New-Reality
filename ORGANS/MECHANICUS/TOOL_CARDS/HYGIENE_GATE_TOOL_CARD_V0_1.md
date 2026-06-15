# MECHANICUS - Hygiene Gate Tool Card (CANDIDATE_V0_1)

Status: CANDIDATE_NOT_CANON
Destination: ORGANS/MECHANICUS/TOOL_CARDS/HYGIENE_GATE_TOOL_CARD_V0_1.md

## Tools delivered (capability_tag: LOCAL_SCRIPT_FIRST)

| Tool | Purpose | Verdict / output |
| --- | --- | --- |
| imperium_hygiene_gate_v0_1.py | Scan repo for artifacts, zip, BOM, CRLF, malformed JSON, empty, secrets | exit 0/1/2 + report JSON |
| fix_encoding_bom_crlf_v0_1.py | Strip BOM and convert CRLF->LF (dry-run default) | change list |
| remove_build_artifacts_v0_1.py | Purge target/, node_modules, caches (dry-run default) | reclaimed MB |
| verify_git_truth_v0_1.py | Prove clean tree + HEAD==origin/master, else AUTHORITY_GAP | receipt JSON |

## Replay commands

```
python tools/imperium_hygiene_gate_v0_1.py --repo-root . --report-out HYGIENE_GATE_REPORT_BEFORE.json
python tools/remove_build_artifacts_v0_1.py --repo-root . --apply
python tools/fix_encoding_bom_crlf_v0_1.py --repo-root . --apply
python tools/verify_git_truth_v0_1.py --repo-root . --report-out GIT_TRUTH_RECEIPT.json
python tools/imperium_hygiene_gate_v0_1.py --repo-root . --report-out HYGIENE_GATE_REPORT_AFTER.json
```

## Install as a guard (recommended)

Wire imperium_hygiene_gate_v0_1.py as a pre-commit and pre-push hook. A BLOCK (exit 2)
stops the commit/push. This is how doctrine becomes enforced instead of advisory.

## Boundaries

- All tools are stdlib-only and cross-platform.
- Tools never delete FIXTURES/ content.
- History rewrite (dropping the 885 MB from past commits) is OUT OF SCOPE: FUTURE_CAPABILITY_GAP.
