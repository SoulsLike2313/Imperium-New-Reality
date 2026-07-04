# TESTS — MECHANICUS-COCKPIT-PATCH-REGISTRY-AND-LANGUAGE-CODEX-0001

The validator checks:

- Tauri Rust backend has patch registry commands;
- Tauri frontend has working cockpit markers;
- app style exists;
- Mechanicus language codex exists;
- language schema/matrix parse;
- Python/Rust/Go/C++/TypeScript/PowerShell are represented;
- each language has proof commands.

Manual test after pass:

```powershell
cd E:\IMPERIUM_REALITY\SUPPORT\APP_TAURI
npm run tauri:dev
```

Then use the cockpit buttons:

1. Refresh
2. Select a patch pack
3. Register
4. Run registered
5. Load language powers
