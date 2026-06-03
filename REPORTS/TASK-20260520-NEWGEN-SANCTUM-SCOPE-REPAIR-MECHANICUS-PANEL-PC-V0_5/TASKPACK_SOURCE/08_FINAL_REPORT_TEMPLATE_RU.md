STEP:
TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

BUNDLE / REPORT PATH:
E:\IMPERIUM\IMPERIUM_NEW_GENERATION\REPORTS\TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

VERDICT:
PASS / WARN / BLOCK

SUMMARY:
- Исправлен scope: task reports/evidence находятся в IMPERIUM_NEW_GENERATION, не в main ORGANS.
- Клик по Mechanicus: PASS/WARN/BLOCK и что именно происходит.
- Operator panel: что видно, что работает, где raw/technical mode.
- SSE/live: CONNECTED/FALLBACK/ERROR/DISABLED, без fake green.

GIT:
HEAD: <hash>
STATUS: clean / dirty with reason
COMMIT: <link or not pushed>

MANUAL CHECK:
```powershell
cd E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_MINI
python server.py --host 127.0.0.1 --port 8765
```

Open:
- Sanctum overview
- click Mechanicus
- run status/tools from panel
- open RAW technical mode
- check Evidence/Reports/Action History
