import { useState } from "react";
import type { CSSProperties } from "react";

type PatchStatus = "pending" | "applied" | "failed";
interface PatchEntry { id: string; version: string; summary: string; status: PatchStatus; }

const MOCK: PatchEntry[] = [
  { id:"v0.10.3", version:"v0.10.3", summary:"Mechanicus passport auto-registrar + VERIFY receipt-JSON fix", status:"applied" },
  { id:"v0.10.4", version:"v0.10.4", summary:"Passport v0_2 auto-drafts (20 passports)",                     status:"applied" },
  { id:"step-6",  version:"step-6",  summary:"Cockpit skeleton + Sanctum tokens",                            status:"applied" },
];

const STATUS_COL: Record<PatchStatus, string> = {
  applied:"var(--pass)", pending:"var(--gold)", failed:"var(--fail)",
};

const S: Record<string, CSSProperties> = {
  section: { padding:"var(--sp-4)" },
  heading: { fontFamily:"var(--font-mono)", color:"var(--gold)",
             fontSize:"var(--text-sm)", marginBottom:"var(--sp-4)", letterSpacing:"0.08em" },
  table:   { width:"100%", borderCollapse:"collapse" },
  th:      { textAlign:"left", padding:"6px 10px", fontSize:"var(--text-xs)",
             color:"var(--muted)", fontFamily:"var(--font-mono)", borderBottom:"var(--border)" },
  td:      { padding:"8px 10px", fontSize:"var(--text-sm)",
             borderBottom:"1px solid rgba(255,255,255,0.04)" },
  tdMono:  { padding:"8px 10px", fontSize:"var(--text-sm)",
             borderBottom:"1px solid rgba(255,255,255,0.04)", fontFamily:"var(--font-mono)" },
};

function rowStyle(sel: boolean): CSSProperties {
  return { background: sel ? "var(--violet-dim)" : "transparent", cursor:"pointer" };
}
function statusTd(s: PatchStatus): CSSProperties {
  return { ...S.tdMono, color: STATUS_COL[s] };
}

export default function PatchManager() {
  const [sel, setSel] = useState<string | null>(null);
  return (
    <section style={S.section}>
      <h2 style={S.heading}>// PATCH MANAGER</h2>
      <table style={S.table}>
        <thead>
          <tr>{["Version","Summary","Status"].map((h)=><th key={h} style={S.th}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {MOCK.map((p) => (
            <tr key={p.id} onClick={()=>setSel(p.id===sel?null:p.id)} style={rowStyle(p.id===sel)}>
              <td style={S.tdMono}>{p.version}</td>
              <td style={S.td}>{p.summary}</td>
              <td style={statusTd(p.status)}>{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
