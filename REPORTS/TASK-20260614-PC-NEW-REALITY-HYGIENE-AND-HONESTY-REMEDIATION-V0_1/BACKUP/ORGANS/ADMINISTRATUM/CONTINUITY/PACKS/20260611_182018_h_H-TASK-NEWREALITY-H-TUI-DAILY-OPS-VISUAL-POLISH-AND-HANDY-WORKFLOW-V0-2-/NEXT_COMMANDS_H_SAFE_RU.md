# NEXT COMMANDS H SAFE RU

## H-зона: применить patch ZIP только тут

```powershell
$HRepo = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H"
cd $HRepo
git status --short
git log --oneline --decorate -5
# затем APPLY_PATCH.ps1 -RepoRoot $HRepo
```

## После owner acceptance в H

```powershell
git status --short
git add <accepted files>
git -c user.name=IMPERIUM_H -c user.email=imperium_h@local commit -m "IMPERIUM_H: <accepted patch title>"
```

## Main: только принять уже проверенный H-коммит

```powershell
$MainRepo = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
cd $MainRepo
git fetch origin
git status --short
git cherry-pick <H_COMMIT_HASH>
python .\ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py --smoke
git push origin master
```
