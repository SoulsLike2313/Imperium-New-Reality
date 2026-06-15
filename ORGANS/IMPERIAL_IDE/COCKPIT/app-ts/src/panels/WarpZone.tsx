import { useState } from "react";
import type { CSSProperties } from "react";

type CmdStatus = "idle" | "running" | "done" | "error";
const STATUS_COL: Record<CmdStatus,string> = {
  idle:"var(--muted)", running:"var(--gold)", done:"var(--pass)", error:"var(--fail)",
};

const S: Record<string,CSSProperties> = {
  section:  { padding:"var(--sp-4)", display:"flex", flexDirection:"column", gap:"var(--sp-3)" },
  heading:  { fontFamily:"var(--font-mono)", color:"var(--gold)", fontSize:"var(--text-sm)",
              letterSpacing:"0.08em", display:"flex", alignItems:"center", gap:"var(--sp-4)" },
  terminal: { background:"var(--bg-raised)", borderRadius:"var(--radius)", border:"var(--border)",
              padding:"var(--sp-3)", overflowY:"auto", fontFamily:"var(--font-mono)",
              fontSize:"var(--text-sm)", minHeight:"240px" },
  ghost:    { color:"var(--muted)", fontStyle:"italic" },
  line:     { color:"var(--fg-dim)", lineHeight:"1.6" },
  row:      { display:"flex", gap:"var(--sp-2)" },
  input:    { flex:1, background:"var(--bg-raised)", border:"var(--border)",
              borderRadius:"var(--radius-sm)", padding:"6px 12px",
              color:"var(--fg)", fontFamily:"var(--font-mono)", fontSize:"var(--text-sm)", outline:"none" },
  btn:      { background:"var(--violet-dim)", border:"var(--border)", borderRadius:"var(--radius-sm)",
              padding:"6px 18px", color:"var(--fg)", fontFamily:"var(--font-mono)",
              fontSize:"var(--text-sm)", cursor:"pointer", letterSpacing:"0.06em" },
};

function badge(s: CmdStatus): CSSProperties {
  return { color: STATUS_COL[s], fontSize:"var(--text-xs)", fontFamily:"var(--font-mono)" };
}

export default function WarpZone() {
  const [cmd, setCmd]   = useState("");
  const [log, setLog]   = useState<string[]>([]);
  const [st,  setSt]    = useState<CmdStatus>("idle");

  const run = () => {
    if (!cmd.trim()) return;
    setSt("running");
    setLog((p) => [...p, `$ ${cmd}`, "[warp-zone: Tauri IPC not yet wired — skeleton]"]);
    setCmd("");
    setTimeout(() => setSt("done"), 400);
  };

  return (
    <section style={S.section}>
      <h2 style={S.heading}>
        // WARP ZONE <span style={badge(st)}>[{st}]</span>
      </h2>
      <div style={S.terminal}>
        {log.length === 0
          ? <span style={S.ghost}>// warp-zone terminal ready</span>
          : log.map((l,i) => <div key={i} style={S.line}>{l}</div>)
        }
      </div>
      <div style={S.row}>
        <input value={cmd} onChange={(e)=>setCmd(e.target.value)}
               onKeyDown={(e)=>e.key==="Enter"&&run()}
               placeholder="command..." style={S.input} />
        <button onClick={run} style={S.btn}>RUN</button>
      </div>
    </section>
  );
}
