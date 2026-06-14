import { useState } from "react";

type CommandStatus = "idle" | "running" | "done" | "error";

export default function WarpZone() {
  const [cmd, setCmd]       = useState("");
  const [output, setOutput] = useState<string[]>([]);
  const [status, setStatus] = useState<CommandStatus>("idle");

  const run = () => {
    if (!cmd.trim()) return;
    setStatus("running");
    setOutput((prev) => [...prev, `$ ${cmd}`, "[warp-zone: command queued — Tauri IPC bridge not yet connected]"]);
    setCmd("");
    setTimeout(() => setStatus("done"), 500);
  };

  const statusColor: Record<CommandStatus, string> = {
    idle:    "var(--muted)",
    running: "var(--gold)",
    done:    "var(--pass)",
    error:   "var(--fail)",
  };

  return (
    <section style= padding: "var(--sp-6)", display: "flex", flexDirection: "column", gap: "var(--sp-4)" >
      <h2 style= color: "var(--gold)", fontFamily: "var(--font-mono)" >
        // WARP ZONE
        <span style= marginLeft: "var(--sp-3)", fontSize: "var(--text-sm)", color: statusColor[status] >[{status}]</span>
      </h2>

      {/* Output terminal */}
      <div style= background: "var(--bg-surface)", border: "var(--border)", borderRadius: "var(--radius-sm)", padding: "var(--sp-3)", fontFamily: "var(--font-mono)", fontSize: "var(--text-sm)", minHeight: 240, maxHeight: 400, overflowY: "auto", color: "var(--fg)" >
        {output.length === 0 ? (
          <span style= color: "var(--muted)" >// warp-zone terminal ready. type a command below.</span>
        ) : (
          output.map((line, i) => (
            <div key={i} style= color: line.startsWith("$") ? "var(--gold)" : "var(--fg-dim)" >{line}</div>
          ))
        )}
      </div>

      {/* Input */}
      <div style= display: "flex", gap: "var(--sp-2)" >
        <input
          value={cmd}
          onChange={(e) => setCmd(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          placeholder="command..."
          style=
            flex: 1,
            background: "var(--bg-surface)",
            border: "var(--border)",
            borderRadius: "var(--radius-sm)",
            padding: "var(--sp-2) var(--sp-3)",
            color: "var(--fg)",
            fontFamily: "var(--font-mono)",
            fontSize: "var(--text-sm)",
            outline: "none",
          
        />
        <button
          onClick={run}
          style= background: "var(--violet)", color: "var(--fg)", border: "none", borderRadius: "var(--radius-sm)", padding: "var(--sp-2) var(--sp-4)", cursor: "pointer", fontFamily: "var(--font-mono)" 
        >
          RUN
        </button>
      </div>
    </section>
  );
}
