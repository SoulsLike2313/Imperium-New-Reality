# Acceptance gates

## Hard gates

- Do not collect secrets.
- Do not include broad private/local context files.
- Do not claim full continuity if stale-context audit is missing.
- Do not claim IDE or WARP release.
- Do not fake a clean PASS while global caps remain active.
- Do not modify unrelated organs except minimal integration receipts/links.

## Required checks

- JSON parse check for all produced JSON files.
- ZIP readability check for continuity pack.
- SHA256 generation for continuity pack and key files.
- Git truth probe.
- Private-data exclusion receipt.
- Stale-context audit.
- Hard red-team verdict.
