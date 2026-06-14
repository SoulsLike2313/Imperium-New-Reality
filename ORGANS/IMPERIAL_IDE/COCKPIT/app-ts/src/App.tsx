import { useState } from "react";
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

export default function App() {
  const [active, setActive] = useState<PanelId>("patch");

  return (
    <div style=
      display:       "flex",
      flexDirection: "column",
      height:        "100vh",
      background:    "var(--bg)",
    >
      {/* Title bar */}
      <header style=
        display:        "flex",
        alignItems:     "center",
        gap:            "var(--sp-4)",
        padding:        "var(--sp-3) var(--sp-6)",
        borderBottom:   "var(--border)",
        background:     "var(--bg-surface)",
        userSelect:     "none",
        WebkitAppRegion: "drag" as React.CSSProperties["WebkitAppRegion"],
      >
        <span style= color: "var(--gold)", fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)" >
          IMPERIAL IDE
        </span>
        <span style= color: "var(--muted)", fontSize: "var(--text-xs)" >COCKPIT v0.1</span>
      </header>

      {/* Tab bar */}
      <nav style=
        display:      "flex",
        gap:          "var(--sp-1)",
        padding:      "var(--sp-2) var(--sp-4)",
        borderBottom: "var(--border)",
        background:   "var(--bg-surface)",
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setActive(t.id)}
            style=
              padding:      "var(--sp-2) var(--sp-4)",
              borderRadius: "var(--radius-sm)",
              border:       active === t.id ? "var(--border-focus)" : "var(--border)",
              background:   active === t.id ? "var(--bg-raised)" : "transparent",
              color:        active === t.id ? "var(--gold)" : "var(--fg-dim)",
              fontFamily:   "var(--font-sans)",
              fontSize:     "var(--text-sm)",
              cursor:       "pointer",
              transition:   "var(--transition)",
            
          >
            {t.label}
          </button>
        ))}
      </nav>

      {/* Panel area */}
      <main style= flex: 1, overflow: "hidden" >
        {active === "patch" && <PatchManager />}
        {active === "warp"  && <WarpZone />}
        {active === "diff"  && <DiffRoom />}
      </main>
    </div>
  );
}
