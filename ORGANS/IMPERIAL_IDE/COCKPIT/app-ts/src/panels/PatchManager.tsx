import { useState } from "react";

type PatchStatus = "pending" | "applied" | "failed";

interface PatchEntry {
  id: string;
  version: string;
  summary: string;
  status: PatchStatus;
}

const MOCK_PATCHES: PatchEntry[] = [
  { id: "v0.10.3", version: "v0.10.3", summary: "Mechanicus passport auto-registrar + VERIFY receipt-JSON fix", status: "applied" },
  { id: "v0.10.4", version: "v0.10.4", summary: "Passport v0_2 auto-drafts (20 passports)", status: "applied" },
  { id: "step-6",  version: "step-6",  summary: "Cockpit skeleton + Sanctum tokens", status: "pending" },
];

const STATUS_COLOR: Record<PatchStatus, string> = {
  applied: "var(--pass)",
  pending: "var(--gold)",
  failed:  "var(--fail)",
};

export default function PatchManager() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <section style= padding: "var(--sp-6)" >
      <h2 style= color: "var(--gold)", fontFamily: "var(--font-mono)", marginBottom: "var(--sp-4)" >
        // PATCH MANAGER
      </h2>
      <table style= width: "100%", borderCollapse: "collapse" >
        <thead>
          <tr style= borderBottom: "var(--border)" >
            {["Version", "Summary", "Status"].map((h) => (
              <th key={h} style= padding: "var(--sp-2) var(--sp-3)", textAlign: "left", color: "var(--fg-dim)", fontSize: "var(--text-sm)", fontFamily: "var(--font-mono)" >{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {MOCK_PATCHES.map((p) => (
            <tr
              key={p.id}
              onClick={() => setSelected(p.id === selected ? null : p.id)}
              style=
                cursor: "pointer",
                background: selected === p.id ? "var(--bg-raised)" : "transparent",
                borderBottom: "var(--border)",
              
            >
              <td style= padding: "var(--sp-2) var(--sp-3)", fontFamily: "var(--font-mono)", color: "var(--gold)" >{p.version}</td>
              <td style= padding: "var(--sp-2) var(--sp-3)", fontSize: "var(--text-sm)" >{p.summary}</td>
              <td style= padding: "var(--sp-2) var(--sp-3)", fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)", color: STATUS_COLOR[p.status] >{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
