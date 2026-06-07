# ACCEPTANCE GATES

- H repo author is IMPERIUM_H <imperium_h@local>.
- Patch is delivered as ZIP.
- APPLY_PATCH.ps1 checks it is running inside an _H repo.
- Patch does not commit automatically.
- Rollback path exists.
- Owner manually verifies the result.
- Only accepted changes may be committed in H.
- Mainline receives changes only by reviewed cherry-pick.
- No real execution, live LLM, unsafe shell, VM route, or destructive cleanup is enabled.
