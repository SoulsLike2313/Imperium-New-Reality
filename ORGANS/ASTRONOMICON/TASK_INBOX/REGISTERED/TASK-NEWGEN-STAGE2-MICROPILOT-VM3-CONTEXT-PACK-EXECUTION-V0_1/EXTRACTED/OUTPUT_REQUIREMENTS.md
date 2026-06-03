# OUTPUT_REQUIREMENTS

Required output files:

1. `context_pack_consumption_receipt.json`
2. `before_after_context_economy_delta.json`
3. `organ_block_usage_receipt.json`
4. `manual_read_log.jsonl`
5. `llm_focus_claim_ledger.jsonl`
6. `cap_carry_forward_receipt.json`
7. `hard_red_team_verdict.json`
8. `final_owner_summary_ru.md`
9. `commit_push_receipt.json`

All machine files must be English-only, UTF-8 no BOM, and schema-friendly.

The only Russian output allowed by this taskpack is `final_owner_summary_ru.md` and the short Owner-facing final answer.

The final Owner-facing answer must be short and include:

- Step name.
- Full path to produced bundle or evidence folder.
- Verdict.
- 3-4 Russian lines explaining what was proven or why it blocked.
- HEAD, clean worktree, and remote sync status when applicable.
