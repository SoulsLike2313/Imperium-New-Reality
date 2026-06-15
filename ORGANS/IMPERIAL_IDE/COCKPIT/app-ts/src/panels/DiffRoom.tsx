import type { CSSProperties } from "react";

type Kind = "+" | "-" | " ";
interface DL { kind: Kind; text: string; }

const DEMO: DL[] = [
  { kind:" ", text:'  "schema_id": "imperium.tool_passport.v0_1",' },
  { kind:"-", text:'-  "validators": [],' },
  { kind:"+", text:'+  "validators": [{"id":"syntax","command":"python -m py_compile {tool_path}"}],' },
  { kind:"-", text:'-  "lang": null,' },
  { kind:"+", text:'+  "lang": "python",' },
  { kind:" ", text:'  "exec_mode": "static",' },
];

const K_FG: Record<Kind,string> = { "+":"var(--pass)",  "-":"var(--fail)",  " ":"var(--fg-dim)" };
const K_BG: Record<Kind,string> = { "+":"rgba(127,210,164,0.07)", "-":"rgba(229,131,136,0.07)", " ":"transparent" };

const S: Record<string,CSSProperties> = {
  section: { padding:"var(--sp-4)" },
  heading: { fontFamily:"var(--font-mono)", color:"var(--gold)",
             fontSize:"var(--text-sm)", marginBottom:"var(--sp-4)", letterSpacing:"0.08em" },
  filebar: { fontSize:"var(--text-xs)", color:"var(--muted)",
             fontFamily:"var(--font-mono)", marginBottom:"var(--sp-3)" },
  fname:   { color:"var(--gold-dim)" },
  block:   { background:"var(--bg-raised)", border:"var(--border)",
             borderRadius:"var(--radius)", overflow:"hidden", marginBottom:"var(--sp-3)" },
  footer:  { fontSize:"var(--text-xs)", color:"var(--muted)",
             fontFamily:"var(--font-mono)", fontStyle:"italic" },
};

function lineS(k: Kind): CSSProperties {
  return { padding:"2px 12px", fontFamily:"var(--font-mono)", fontSize:"var(--text-sm)",
           color:K_FG[k], background:K_BG[k], lineHeight:"1.7", whiteSpace:"pre" };
}

export default function DiffRoom() {
  const file = "evidence_migration_tool_passport_v0_2.json (draft)";
  return (
    <section style={S.section}>
      <h2 style={S.heading}>// DIFF ROOM</h2>
      <div style={S.filebar}>file: <span style={S.fname}>{file}</span></div>
      <div style={S.block}>
        {DEMO.map((l,i)=><div key={i} style={lineS(l.kind)}>{l.text}</div>)}
      </div>
      <p style={S.footer}>// read-only preview -- live diff via Tauri IPC in next iteration</p>
    </section>
  );
}
