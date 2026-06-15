/**
 * IMPERIUM THEME TOKENS (V0.1)
 * Purple Dark Nebula Metallic Warhammer Imperium style.
 *
 * WHY TYPESCRIPT FOR THE TOKENS:
 *  - A single typed source of truth that any future web / Electron / native
 *    surface can import, while Python and C# read the generated JSON twin
 *    (imperium_theme.json). Keeping tokens in one place stops the GUI, TUI and
 *    any native shell from drifting apart visually.
 *
 * Build the JSON twin:  tsx imperium_theme.ts > imperium_theme.generated.json
 */

export const palette = {
  void: "#05030B",
  void2: "#0A0616",
  panel: "#0F0A1C",
  panelRaised: "#171029",
  panelHi: "#1F1638",
  nebulaDeep: "#2A1248",
  nebula: "#3A1E5C",
  nebulaBright: "#5B2E8A",
  plasma: "#9A4FE8",
  plasmaHot: "#B96BFF",
  metalDark: "#3C3C50",
  metal: "#6E6E86",
  metalBright: "#A8A8C0",
  chrome: "#D6D6E6",
  gold: "#C9A24B",
  goldBright: "#E8C66A",
  bronze: "#8A6A2E",
  alertRed: "#B5354A",
  warnAmber: "#D8923A",
  okGreen: "#4FB58A",
  text: "#ECEAF6",
  textMuted: "#9A93B5",
  textFaint: "#675F84",
  line: "#2A2142",
  lineBright: "#463A66",
} as const

export const statusColors = {
  PASS: palette.okGreen,
  PASS_WITH_WARNINGS: palette.warnAmber,
  BLOCKED: palette.alertRed,
  PENDING: palette.textMuted,
  ACTIVE: palette.plasmaHot,
  IDLE: palette.metal,
  DRY_RUN: palette.nebulaBright,
} as const

export const typography = {
  display: "Trajan Pro, Times New Roman, Georgia, serif",
  ui: "Segoe UI, Verdana, sans-serif",
  mono: "Cascadia Mono, Consolas, Courier New, monospace",
} as const

export const theme = { themeId: "PURPLE_DARK_NEBULA_METALLIC_IMPERIUM", version: "0.1", palette, statusColors, typography }

// When run directly, emit JSON (used to regenerate the JSON twin).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const isMain = typeof require !== "undefined" && (require as any).main === module
if (isMain) {
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(theme, null, 2))
}
