# COMMON_AGENT_CLI Check Spec

## Required checks
1. Required directory structure exists.
2. All policy JSON files parse successfully.
3. Mode files contain required fields.
4. Command palette contains required short commands.
5. Shell boundary policy contains dedicated message.
6. Color theme includes required palette entries.
7. Heraldry files exist and no external logo policy exists.
8. Bad shell anti-example transcript exists.
9. Renderer truth contract exists.
10. Visual evidence policy exists.

## Suggested command
```powershell
python -m json.tool <json_file>
```

## PASS rule
All required checks pass and requirement matrix marks each REQ-CLIREF item with evidence.
