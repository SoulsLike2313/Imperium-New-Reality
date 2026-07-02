# PATCH PACK — IMPERIUM-APP-TAURI-PROOF-RUN-NPM-CMD-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `ASTRONOMICON + SUPPORT/APP_TAURI`  
mode: `WINDOWS_NPM_CMD_HOTFIX`

## Purpose

Close the failed Tauri proof run:

```text
command failed: npm --version
```

## Diagnosis

On Windows, npm is commonly exposed as `npm.cmd`.

The proof validator v0.1 ran npm as a plain subprocess command. This hotfix makes npm execution Windows-aware and uses:

```text
cmd.exe /d /s /c npm ...
```

for:

```text
npm --version
npm install
npm run check:fps
npm run check:parity
npm run build
```

## Expected verdict

```text
PASS_IMPERIUM_APP_TAURI_PROOF_RUN_NPM_CMD_HOTFIX_READY
```

and the proof-run receipt should become:

```text
PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY
```
