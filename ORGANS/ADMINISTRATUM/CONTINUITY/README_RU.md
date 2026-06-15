# Administratum Continuity Center V0.1

Continuity Pack — внутренняя функция Imperial IDE под крылом Administratum.

Назначение:

- собрать безопасный пакет перехода в новый чат;
- дать Logos Prime owner-visible summary;
- сохранить manifest/receipt/sha256;
- не выполнять real execution, commit, push, unsafe shell или live LLM.

Команды:

```powershell
python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --smoke
python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --preview h
python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --build h
```

Через IDE CLI:

```powershell
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-preview h
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-build h
python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py continuity-smoke
```

Пакеты пишутся в `ORGANS/ADMINISTRATUM/CONTINUITY/PACKS/` и игнорируются git-ом.


## Encoding / mojibake guard

Owner-facing Russian text files are written as UTF-8 with BOM (`utf-8-sig`):

- `OWNER_CONTINUITY_SUMMARY_RU.md`
- `LOGOS_PRIME_HANDOFF_SUMMARY_RU.md`
- `NEXT_HANDOFF_CARD.md`
- `ENCODING_README_RU.txt`

Machine files (`CONTINUITY_MANIFEST.json`, `CONTINUITY_RECEIPT.json`) remain plain UTF-8 for parser compatibility.

If WordPad showed mojibake in an older pack, rebuild the pack after this fix.
