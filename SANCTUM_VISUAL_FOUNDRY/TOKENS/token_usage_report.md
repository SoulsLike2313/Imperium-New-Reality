# Token usage report

## Token sources
- JSON file: `TOKENS/design_tokens_mechanicus_console_v0_2.json`
- CSS export: `TOKENS/design_tokens_mechanicus_console_v0_2.css`

## Consumed by
- `LAB/index.html` links `../TOKENS/design_tokens_mechanicus_console_v0_2.css`
- `LAB/styles.css` consumes `--vf2-*` variables for color, spacing, radius, border, shadow, and motion
- `LAB/app.js` keeps semantic state classes (`ok`, `warn`, `error`) that map onto token-driven styles

## Mapped areas
- background surfaces: `--vf2-color-bg-*`
- panel borders: `--vf2-border-panel`, `--vf2-border-holo`, `--vf2-border-chip`
- accent colors: `--vf2-color-accent-*`
- text hierarchy: `--vf2-color-text-*`, `--vf2-size-*`, `--vf2-font-*`
- spacing/radius: `--vf2-space-*`, `--vf2-radius-*`
- motion timing: `--vf2-motion-*`

## Known gaps
- Token generation is still manual; no automated JSON->CSS generator yet.
- Some inline shadow mixes remain stylesheet-authored but built from tokenized palette values.

