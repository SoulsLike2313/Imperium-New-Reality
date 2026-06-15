# NEXT COMMANDS H SAFE RU

```powershell
$HRepo = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY_H"
cd $HRepo
git status --short
git log --oneline --decorate -5
```

Apply patch ZIP only in H:

```powershell
$PatchName = "H_PATCH_ADMINISTRATUM_CONTINUITY_AND_SANCTUM_UX_V0_3"
$zip = Get-ChildItem "$env:USERPROFILE\Downloads" -Filter "$PatchName*.zip" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if (-not $zip) { throw "ZIP not found in Downloads: $PatchName.zip" }
Copy-Item -LiteralPath $zip.FullName -Destination "$HRepo\$PatchName.zip" -Force
Remove-Item "$HRepo\$PatchName" -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -LiteralPath "$HRepo\$PatchName.zip" -DestinationPath "$HRepo\$PatchName" -Force
powershell -NoProfile -ExecutionPolicy Bypass -File "$HRepo\$PatchName\APPLY_PATCH.ps1" -RepoRoot $HRepo
```

After owner visual/smoke acceptance:

```powershell
git status --short
git add .\ORGANS\ADMINISTRATUM\CONTINUITY .\ORGANS\IMPERIAL_IDE\LAUNCHER
git -c user.name=IMPERIUM_H -c user.email=imperium_h@local commit -m "IMPERIUM_H: harden continuity and seed Sanctum UX v0.3"
```

Main acceptance happens only after H acceptance:

```powershell
$MainRepo = "E:\IMPERIUM_NEW_GENERATION_NEW_REALITY"
cd $MainRepo
git fetch origin
git status --short
git cherry-pick <H_COMMIT_HASH>
python .\ORGANS\ADMINISTRATUM\CONTINUITY\continuity_pack_builder.py --smoke
python .\ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py --smoke
git push origin master
```
