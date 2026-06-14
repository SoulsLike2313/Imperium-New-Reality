import { useState } from "react";
import type { CSSProperties } from "react";
import PatchManager from "./panels/PatchManager";
import WarpZone    from "./panels/WarpZone";
import DiffRoom    from "./panels/DiffRoom";
import "./styles/sanctum.css";

type PanelId = "patch" | "warp" | "diff";

const TABS: { id: PanelId; label: string }[] = [
  { id: "patch", label: "Patch Manager" },
  { id: "warp",  label: "Warp Zone" },
  { id: "diff",  label: "Diff Room" },
];

const S: Record<string, CSSProperties> = {
  root: {
    display: "flex", flexDirection: "column", height: "100vh",
    background: "var(--bg)", color: "var(--fg)",
    fontFamily: "var(--font-sans)", overflow: "hidden",
  },
  header: {
    display: "flex", alignItems: "center", padding: "0 var(--sp-4)",
    height: "44px", borderBottom: "var(--border)",
    flexShrink: 0, userSelect: "none",
  },
  title: {
    fontFamily: "var(--font-serif)", color: "var(--gold)",
    fontWeight: 700, fontSize: "var(--text-lg)", letterSpacing: "0.12em",
  },
  version: {
    marginLeft: "auto", fontSize: "var(--text-xs)",
    color: "var(--muted)", fontFamily: "var(--font-mono)",
  },
  nav: {
    display: "flex", gap: "var(--sp-1)", padding: "var(--sp-2) var(--sp-4)",
    borderBottom: "var(--border)", flexShrink: 0,
    background: "var(--bg-surface)",
  },
  main: { flex: 1, overflow: "auto", padding: "var(--sp-4)" },
};

function tabStyle(active: boolean): CSSProperties {
  return {
    background:    active ? "var(--violet-dim)" : "transparent",
    color:         active ? "var(--fg)"         : "var(--fg-dim)",
    border:        "var(--border)",
    borderRadius:  "var(--radius-sm)",
    padding:       "4px 14px",
    cursor:        "pointer",
    fontFamily:    "var(--font-mono)",
    fontSize:      "var(--text-sm)",
    transition:    "var(--transition)",
  };
}

export default function App() {
  const [active, setActive] = useState<PanelId>("patch");
  return (
    <div style={S.root}>
      <header style={S.header}>
        <span style={S.title}>IMPERIAL IDE</span>
        <span style={S.version}>COCKPIT v0.1</span>
      </header>
      <nav style={S.nav}>
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setActive(t.id)}
                  style={tabStyle(active === t.id)}>
            {t.label}
          </button>
        ))}
      </nav>
      <main style={S.main}>
        {active === "patch" && <PatchManager />}
        {active === "warp"  && <WarpZone />}
        {active === "diff"  && <DiffRoom />}
      </main>
    </div>
  );
}
