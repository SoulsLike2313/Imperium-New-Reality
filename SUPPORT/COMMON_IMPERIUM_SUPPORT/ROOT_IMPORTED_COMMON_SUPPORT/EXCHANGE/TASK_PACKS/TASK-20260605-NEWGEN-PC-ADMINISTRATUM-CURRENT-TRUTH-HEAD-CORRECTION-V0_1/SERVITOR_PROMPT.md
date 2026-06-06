# SERVITOR PROMPT — TASK-20260605-NEWGEN-PC-ADMINISTRATUM-CURRENT-TRUTH-HEAD-CORRECTION-V0_1

You are operating inside `E:/IMPERIUM_NEW_GENERATION_NEW_REALITY` only.

## Mission
Repair Administratum current truth HEAD drift only. The observed actual HEAD is `d61edfd08dbc69919645cec827aaa2c899089ae9`; the current truth card may still point to stale HEAD `892ae8a6f5452c55211da4748bed3b1d9d3f9326`.

## Hard rules
- Work only inside New Reality root.
- Do not access Ancient Empire, parent folders, or private paths.
- Do not build the post-work organ admission ring in this task.
- Do not refactor unrelated files.
- No fake green: missing measurement or validator output is `UNKNOWN_WITH_REASON`, not `PASS`.
- Use Astronomicon task essence and route packet from this task pack.
- Use Administratum registration card as the task session seed.

## Expected flow
1. Register task through Administratum using `REGISTER_TASKPACK_THROUGH_ADMINISTRATUM.ps1`.
2. Read Astronomicon task essence and route packet.
3. Inspect `ADMINISTRATUM/CURRENT_TRUTH/current_head_card_v0_1.json` and linked current truth files.
4. Apply minimal correction only.
5. Run available validators.
6. Produce Russian owner summary and evidence receipts.
7. Commit with normal non-force git flow; prove local/remote equality only if push is performed.
