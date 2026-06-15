# ENCODING README RU

Owner-facing Russian markdown files in this continuity pack are written as UTF-8 with BOM (utf-8-sig).
This prevents Windows WordPad/legacy viewers from displaying mojibake like `РќРѕРІ...`.

Machine JSON remains UTF-8 without BOM for parser compatibility.

Recommended files for next Logos Prime:
- LOGOS_PRIME_HANDOFF_SUMMARY_RU.md
- OWNER_CONTINUITY_SUMMARY_RU.md
- CONTINUITY_MANIFEST.json
- CONTINUITY_RECEIPT.json

If an old pack still shows mojibake, rebuild it after this fix:
`python ORGANS/ADMINISTRATUM/CONTINUITY/continuity_pack_builder.py --build h`
