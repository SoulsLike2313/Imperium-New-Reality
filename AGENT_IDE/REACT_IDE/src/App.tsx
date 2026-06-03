import { useEffect, useMemo, useState } from "react";

type Lang = "en" | "ru";

type AnyRecord = Record<string, unknown>;

type DashboardModel = {
  task_id?: string;
  generated_at_utc?: string;
  truth?: {
    git?: { branch?: string; head?: string };
    required_route_alias?: string;
  };
  organs?: Array<{ organ?: string; file_count?: number; status?: string }>;
  atlas_summary?: { passport_count?: number; unknown_file_kind_count?: number };
  warnings?: string[];
  language_gate_surface?: AnyRecord;
  owner_pain_surface?: {
    pain_count?: number;
    pain_items?: Array<{
      pain_id?: string;
      severity?: string;
      current_status?: string;
      next_task_route?: string;
    }>;
  };
  route_surface?: {
    required_alias?: string;
    imperium_vm3_visible?: boolean;
    canonical_commands_file?: string;
    canonical_commands_preview?: string;
  };
  report_receipt_summary?: {
    report_paths_count?: number;
    receipt_paths_count?: number;
    report_paths_sample?: string[];
    receipt_paths_sample?: string[];
  };
  self_validator_surface?: {
    status?: string;
    summary_receipt_path?: string;
    last_timestamp_utc?: string;
  };
  block_foundation_preview?: AnyRecord;
  checker_tool_surface?: AnyRecord;
  plugin_surface?: {
    providers?: Array<{ source_key?: string; relative_path?: string; parse_mode?: string; required?: boolean }>;
  };
  file_passports_projection?: Array<{
    path?: string;
    owner_organ?: string;
    file_kind?: string;
    status?: string;
    classification?: string;
    projection_visibility?: string;
  }>;
};

type BlockModel = {
  warnings?: string[];
};

type FilePreview = {
  allowed?: boolean;
  path?: string;
  truncated?: boolean;
  content?: string;
  reason?: string;
};

type ProbeItem = {
  name?: string;
  command?: string;
  available?: boolean;
  exit_code?: number | null;
  stdout?: string;
  stderr?: string;
};

type ToolchainProbe = {
  status?: string;
  probes?: ProbeItem[];
};

type DesktopDecision = {
  decision?: string;
  status?: string;
  note?: string;
};

type PluginManifest = {
  providers?: Array<{ source_key?: string; relative_path?: string; parse_mode?: string; required?: boolean }>;
};

const I18N: Record<Lang, Record<string, string>> = {
  en: {
    title: "IMPERIUM Agent IDE",
    subtitle: "React + TypeScript web-shell parity surface",
    refresh: "Refresh",
    toggle: "RU",
    overview: "Overview",
    organs: "Project / Organ Explorer",
    atlas: "File Atlas",
    viewer: "Read-only Viewer",
    languageGate: "Officio Language Gate",
    pain: "Owner Pain Map",
    routes: "Routes",
    reports: "Reports / Receipts",
    checks: "Toolchain / Checks",
    blockFoundation: "Block Foundation",
    plugins: "Plugins / Extensions",
    selectFile: "Select file",
    noFile: "No safe file selected",
    loading: "Loading...",
  },
  ru: {
    title: "IMPERIUM Agent IDE",
    subtitle: "React + TypeScript поверхность parity для web-shell",
    refresh: "Обновить",
    toggle: "EN",
    overview: "Обзор",
    organs: "Project / Organ Explorer",
    atlas: "Атлас файлов",
    viewer: "Просмотр (только чтение)",
    languageGate: "Officio Language Gate",
    pain: "Карта болей Owner",
    routes: "Маршруты",
    reports: "Отчёты / Квитанции",
    checks: "Toolchain / Checks",
    blockFoundation: "Block Foundation",
    plugins: "Плагины / Расширения",
    selectFile: "Выберите файл",
    noFile: "Безопасный файл не выбран",
    loading: "Загрузка...",
  },
};

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${url}`);
  }
  return (await response.json()) as T;
}

export function App() {
  const [lang, setLang] = useState<Lang>("en");
  const [dashboard, setDashboard] = useState<DashboardModel | null>(null);
  const [blockModel, setBlockModel] = useState<BlockModel | null>(null);
  const [plugins, setPlugins] = useState<PluginManifest | null>(null);
  const [probe, setProbe] = useState<ToolchainProbe | null>(null);
  const [decision, setDecision] = useState<DesktopDecision | null>(null);
  const [selectedPath, setSelectedPath] = useState<string>("");
  const [preview, setPreview] = useState<FilePreview | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  const t = (key: string) => I18N[lang][key] ?? key;

  async function loadAll() {
    setLoading(true);
    setError("");
    try {
      const [vm, block, pluginManifest, toolProbe, desktopDecision] = await Promise.all([
        fetchJson<DashboardModel>("/api/view-model"),
        fetchJson<BlockModel>("/api/block-view-model"),
        fetchJson<PluginManifest>("/api/plugins"),
        fetchJson<ToolchainProbe>("/api/toolchain-probe"),
        fetchJson<DesktopDecision>("/api/desktop-shell-decision"),
      ]);
      setDashboard(vm);
      setBlockModel(block);
      setPlugins(pluginManifest);
      setProbe(toolProbe);
      setDecision(desktopDecision);

      const firstPath =
        vm.file_passports_projection
          ?.map((item) => item.path || "")
          .find((item) => item && item !== "[RESTRICTED]") ?? "";
      if (firstPath && !selectedPath) {
        setSelectedPath(firstPath);
      }
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!selectedPath) {
      setPreview(null);
      return;
    }
    let cancelled = false;
    fetchJson<FilePreview>(`/api/file-preview?path=${encodeURIComponent(selectedPath)}`)
      .then((payload) => {
        if (!cancelled) {
          setPreview(payload);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setPreview({ allowed: false, path: selectedPath, reason: String(err), content: "" });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPath]);

  const truth = useMemo(() => {
    const organs = dashboard?.organs ?? [];
    const passports = dashboard?.atlas_summary?.passport_count ?? 0;
    const unknown = dashboard?.atlas_summary?.unknown_file_kind_count ?? 0;
    const pain = dashboard?.owner_pain_surface?.pain_count ?? 0;
    const route = dashboard?.truth?.required_route_alias ?? "imperium-vm3";
    const head = dashboard?.truth?.git?.head ?? "UNKNOWN";
    const verdict = dashboard?.self_validator_surface?.status ?? "UNPROVEN";
    return { organs: organs.length, passports, unknown, pain, route, head, verdict };
  }, [dashboard]);

  const fileOptions = dashboard?.file_passports_projection ?? [];
  const painItems = dashboard?.owner_pain_surface?.pain_items ?? [];
  const driftWarnings =
    (dashboard?.language_gate_surface?.["current_drift_warning_surfaces"] as string[] | undefined) ?? [];

  return (
    <div className="app-shell">
      <div className="bg-layer" aria-hidden="true" />
      <header className="topbar">
        <div>
          <h1>{t("title")}</h1>
          <p>{t("subtitle")}</p>
        </div>
        <div className="actions">
          <button onClick={() => setLang(lang === "en" ? "ru" : "en")}>{t("toggle")}</button>
          <button onClick={() => void loadAll()}>{t("refresh")}</button>
        </div>
      </header>

      <section className="truth-markers">
        <span data-truth="organ-count">{String(truth.organs)}</span>
        <span data-truth="passport-count">{String(truth.passports)}</span>
        <span data-truth="unknown-file-kind-count">{String(truth.unknown)}</span>
        <span data-truth="owner-pain-count">{String(truth.pain)}</span>
        <span data-truth="route-alias">{truth.route}</span>
        <span data-truth="current-head">{truth.head}</span>
        <span data-truth="self-validator-verdict">{truth.verdict}</span>
      </section>

      {error ? <div className="error-strip">{error}</div> : null}
      {loading && !dashboard ? <div className="loading">{t("loading")}</div> : null}

      <main className="grid">
        <section className="panel" id="overview">
          <h2>{t("overview")}</h2>
          <pre>
            {JSON.stringify(
              {
                task_id: dashboard?.task_id,
                generated_at_utc: dashboard?.generated_at_utc,
                branch: dashboard?.truth?.git?.branch,
                head: truth.head,
                self_validator_verdict: truth.verdict,
                warnings: dashboard?.warnings?.length ?? 0,
              },
              null,
              2
            )}
          </pre>
        </section>

        <section className="panel" id="organs">
          <h2>{t("organs")}</h2>
          <div className="organ-grid">
            {(dashboard?.organs ?? []).map((organ) => (
              <div className="organ-card" key={`${organ.organ}`}>
                <strong>{organ.organ}</strong>
                <span>{organ.file_count}</span>
                <em>{organ.status}</em>
              </div>
            ))}
          </div>
        </section>

        <section className="panel" id="file-atlas">
          <h2>{t("atlas")}</h2>
          <pre>
            {JSON.stringify(
              {
                passport_count: dashboard?.atlas_summary?.passport_count ?? 0,
                unknown_file_kind_count: dashboard?.atlas_summary?.unknown_file_kind_count ?? 0,
                classification_counts: (dashboard as AnyRecord)?.["classification_counts"] ?? {},
              },
              null,
              2
            )}
          </pre>
        </section>

        <section className="panel" id="viewer">
          <h2>{t("viewer")}</h2>
          <label className="viewer-select" htmlFor="pathSelect">
            {t("selectFile")}
          </label>
          <select
            id="pathSelect"
            value={selectedPath}
            onChange={(event) => setSelectedPath(event.target.value)}
          >
            <option value="">{t("noFile")}</option>
            {fileOptions.map((item) => {
              const value = item.path || "";
              const label = `${item.owner_organ || "UNKNOWN"} | ${item.file_kind || "UNKNOWN"} | ${value}`;
              return (
                <option key={label} value={value}>
                  {label}
                </option>
              );
            })}
          </select>
          <pre>
            {JSON.stringify(
              {
                path: preview?.path,
                allowed: preview?.allowed,
                truncated: preview?.truncated,
                reason: preview?.reason,
              },
              null,
              2
            )}
          </pre>
          <pre className="file-preview">{preview?.content || ""}</pre>
        </section>

        <section className="panel" id="officio-language-gate">
          <h2>{t("languageGate")}</h2>
          <pre>{JSON.stringify(dashboard?.language_gate_surface ?? {}, null, 2)}</pre>
        </section>

        <section className="panel" id="owner-pain-map">
          <h2>{t("pain")}</h2>
          <div className="pain-list">
            {painItems.map((item) => (
              <div className="pain-item" key={`${item.pain_id}-${item.next_task_route}`}>
                <strong>{item.pain_id}</strong>
                <span>{item.severity}</span>
                <span>{item.current_status}</span>
                <code>{item.next_task_route}</code>
              </div>
            ))}
          </div>
        </section>

        <section className="panel" id="routes">
          <h2>{t("routes")}</h2>
          <pre>
            {JSON.stringify(
              {
                required_alias: dashboard?.route_surface?.required_alias,
                imperium_vm3_visible: dashboard?.route_surface?.imperium_vm3_visible,
                canonical_commands_file: dashboard?.route_surface?.canonical_commands_file,
              },
              null,
              2
            )}
          </pre>
          <pre className="file-preview">{dashboard?.route_surface?.canonical_commands_preview || ""}</pre>
        </section>

        <section className="panel" id="reports">
          <h2>{t("reports")}</h2>
          <pre>{JSON.stringify(dashboard?.report_receipt_summary ?? {}, null, 2)}</pre>
        </section>

        <section className="panel" id="checks">
          <h2>{t("checks")}</h2>
          <pre>
            {JSON.stringify(
              {
                self_validator: dashboard?.self_validator_surface,
                desktop_shell_decision: decision,
                toolchain_probe_status: probe?.status,
                playwright_available:
                  probe?.probes?.find((p) => p.name === "npx_playwright")?.exit_code === 0 || false,
                checker_tools: dashboard?.checker_tool_surface,
                drift_warning_count: driftWarnings.length,
                warnings_sample: (dashboard?.warnings ?? []).slice(0, 12),
              },
              null,
              2
            )}
          </pre>
        </section>

        <section className="panel" id="block-foundation">
          <h2>{t("blockFoundation")}</h2>
          <pre>
            {JSON.stringify(
              {
                block_foundation_preview: dashboard?.block_foundation_preview,
                block_model_warnings: blockModel?.warnings ?? [],
              },
              null,
              2
            )}
          </pre>
        </section>

        <section className="panel" id="plugins">
          <h2>{t("plugins")}</h2>
          <pre>
            {JSON.stringify(
              {
                providers_count: plugins?.providers?.length ?? 0,
                providers_sample: (plugins?.providers ?? []).slice(0, 20),
              },
              null,
              2
            )}
          </pre>
        </section>
      </main>
    </div>
  );
}
