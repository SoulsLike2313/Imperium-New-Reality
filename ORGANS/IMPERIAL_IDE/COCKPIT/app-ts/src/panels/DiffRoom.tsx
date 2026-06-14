import { useState } from "react";

interface DiffLine {
  kind: "+" | "-" | " ";
  text: string;
}

const DEMO_DIFF: DiffLine[] = [
  { kind: " ", text: "  schema_id: \"imperium.tool_passport.v0_1\"," },
  { kind: "-", text: "-  validators: []," },
  { kind: "+", text: "+  validators: [{ id: \"syntax\", type: \"command\", command: \"python -m py_compile {tool_path}\" }]," },
  { kind: "-", text: "-  lang: null," },
  { kind: "+", text: "+  lang: \"python\"," },
  { kind: " ", text: "  exec_mode: \"static\"," },
];

const KIND_COLOR = { "+": "var(--pass)", "-": "var(--fail)", " ": "var(--fg-dim)" } as const;
const KIND_BG    = { "+": "rgba(127,210,164,0.08)", "-": "rgba(229,131,136,0.08)", " ": "transparent" } as const;

export default function DiffRoom() {
  const [file, setFile] = useState("evidence_migration_tool_passport_v0_2.json (draft)");

  return (
    <section style= padding: "var(--sp-6)" >
      <h2 style= color: "var(--gold)", fontFamily: "var(--font-mono)", marginBottom: "var(--sp-3)" >
        // DIFF ROOM
      </h2>

      <div style= color: "var(--fg-dim)", fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)", marginBottom: "var(--sp-3)" >
        file: <span style= color: "var(--gold)" >{file}</span>
      </div>

      <div style= background: "var(--bg-surface)", border: "var(--border)", borderRadius: "var(--radius-sm)", padding: "var(--sp-3)", fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)" >
        {DEMO_DIFF.map((line, i) => (
          <div key={i} style= background: KIND_BG[line.kind], color: KIND_COLOR[line.kind], padding: "1px var(--sp-2)", whiteSpace: "pre" >
            {line.text}
          </div>
        ))}
      </div>

      <p style= marginTop: "var(--sp-4)", color: "var(--muted)", fontSize: "var(--text-sm)" >
        // read-only preview — live diff via Tauri IPC in next iteration
      </p>
    </section>
  );
}
