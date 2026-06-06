# Important Six Organ-Centered Cockpit Skeleton V0.1

Task: `TASK-NEWGEN-SANCTUM-ORGAN-CENTERED-COCKPIT-SKELETON-PC-V0_1`

This file set introduces a NewGen Sanctum cockpit skeleton where:

- first screen is organ-centered;
- L2 action layer is secondary;
- Owner Decision Queue is explicit;
- evidence/history zone is explicit;
- values are static seed/read-only and marked honestly.

## Files

- `important_six_organ_cockpit_v0_1.html`
- `important_six_organ_cockpit_v0_1.css`
- `important_six_organ_cockpit_v0_1.js`
- `important_six_organ_cockpit_manifest_v0_1.json`

## Launch (static)

From repository root:

```powershell
python -m http.server 8767 --directory IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD
```

Open:

- `http://127.0.0.1:8767/important_six_organ_cockpit_v0_1.html`

## Scope boundary

- No new mutating endpoints.
- No uncontrolled PTY/browser terminal.
- No claim of production readiness.
- No fake green: static seed data is labeled `SEED_DATA_NOT_PROVEN`.

## Bilingual support

- RU and EN UI labels are available.
- Language switch is local (client-side toggle).
