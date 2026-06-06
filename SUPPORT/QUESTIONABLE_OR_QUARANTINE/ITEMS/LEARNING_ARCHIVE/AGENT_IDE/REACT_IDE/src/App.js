import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
const I18N = {
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
async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}: ${url}`);
    }
    return (await response.json());
}
export function App() {
    const [lang, setLang] = useState("en");
    const [dashboard, setDashboard] = useState(null);
    const [blockModel, setBlockModel] = useState(null);
    const [plugins, setPlugins] = useState(null);
    const [probe, setProbe] = useState(null);
    const [decision, setDecision] = useState(null);
    const [selectedPath, setSelectedPath] = useState("");
    const [preview, setPreview] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const t = (key) => I18N[lang][key] ?? key;
    async function loadAll() {
        setLoading(true);
        setError("");
        try {
            const [vm, block, pluginManifest, toolProbe, desktopDecision] = await Promise.all([
                fetchJson("/api/view-model"),
                fetchJson("/api/block-view-model"),
                fetchJson("/api/plugins"),
                fetchJson("/api/toolchain-probe"),
                fetchJson("/api/desktop-shell-decision"),
            ]);
            setDashboard(vm);
            setBlockModel(block);
            setPlugins(pluginManifest);
            setProbe(toolProbe);
            setDecision(desktopDecision);
            const firstPath = vm.file_passports_projection
                ?.map((item) => item.path || "")
                .find((item) => item && item !== "[RESTRICTED]") ?? "";
            if (firstPath && !selectedPath) {
                setSelectedPath(firstPath);
            }
        }
        catch (err) {
            setError(String(err));
        }
        finally {
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
        fetchJson(`/api/file-preview?path=${encodeURIComponent(selectedPath)}`)
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
    const driftWarnings = dashboard?.language_gate_surface?.["current_drift_warning_surfaces"] ?? [];
    return (_jsxs("div", { className: "app-shell", children: [_jsx("div", { className: "bg-layer", "aria-hidden": "true" }), _jsxs("header", { className: "topbar", children: [_jsxs("div", { children: [_jsx("h1", { children: t("title") }), _jsx("p", { children: t("subtitle") })] }), _jsxs("div", { className: "actions", children: [_jsx("button", { onClick: () => setLang(lang === "en" ? "ru" : "en"), children: t("toggle") }), _jsx("button", { onClick: () => void loadAll(), children: t("refresh") })] })] }), _jsxs("section", { className: "truth-markers", children: [_jsx("span", { "data-truth": "organ-count", children: String(truth.organs) }), _jsx("span", { "data-truth": "passport-count", children: String(truth.passports) }), _jsx("span", { "data-truth": "unknown-file-kind-count", children: String(truth.unknown) }), _jsx("span", { "data-truth": "owner-pain-count", children: String(truth.pain) }), _jsx("span", { "data-truth": "route-alias", children: truth.route }), _jsx("span", { "data-truth": "current-head", children: truth.head }), _jsx("span", { "data-truth": "self-validator-verdict", children: truth.verdict })] }), error ? _jsx("div", { className: "error-strip", children: error }) : null, loading && !dashboard ? _jsx("div", { className: "loading", children: t("loading") }) : null, _jsxs("main", { className: "grid", children: [_jsxs("section", { className: "panel", id: "overview", children: [_jsx("h2", { children: t("overview") }), _jsx("pre", { children: JSON.stringify({
                                    task_id: dashboard?.task_id,
                                    generated_at_utc: dashboard?.generated_at_utc,
                                    branch: dashboard?.truth?.git?.branch,
                                    head: truth.head,
                                    self_validator_verdict: truth.verdict,
                                    warnings: dashboard?.warnings?.length ?? 0,
                                }, null, 2) })] }), _jsxs("section", { className: "panel", id: "organs", children: [_jsx("h2", { children: t("organs") }), _jsx("div", { className: "organ-grid", children: (dashboard?.organs ?? []).map((organ) => (_jsxs("div", { className: "organ-card", children: [_jsx("strong", { children: organ.organ }), _jsx("span", { children: organ.file_count }), _jsx("em", { children: organ.status })] }, `${organ.organ}`))) })] }), _jsxs("section", { className: "panel", id: "file-atlas", children: [_jsx("h2", { children: t("atlas") }), _jsx("pre", { children: JSON.stringify({
                                    passport_count: dashboard?.atlas_summary?.passport_count ?? 0,
                                    unknown_file_kind_count: dashboard?.atlas_summary?.unknown_file_kind_count ?? 0,
                                    classification_counts: dashboard?.["classification_counts"] ?? {},
                                }, null, 2) })] }), _jsxs("section", { className: "panel", id: "viewer", children: [_jsx("h2", { children: t("viewer") }), _jsx("label", { className: "viewer-select", htmlFor: "pathSelect", children: t("selectFile") }), _jsxs("select", { id: "pathSelect", value: selectedPath, onChange: (event) => setSelectedPath(event.target.value), children: [_jsx("option", { value: "", children: t("noFile") }), fileOptions.map((item) => {
                                        const value = item.path || "";
                                        const label = `${item.owner_organ || "UNKNOWN"} | ${item.file_kind || "UNKNOWN"} | ${value}`;
                                        return (_jsx("option", { value: value, children: label }, label));
                                    })] }), _jsx("pre", { children: JSON.stringify({
                                    path: preview?.path,
                                    allowed: preview?.allowed,
                                    truncated: preview?.truncated,
                                    reason: preview?.reason,
                                }, null, 2) }), _jsx("pre", { className: "file-preview", children: preview?.content || "" })] }), _jsxs("section", { className: "panel", id: "officio-language-gate", children: [_jsx("h2", { children: t("languageGate") }), _jsx("pre", { children: JSON.stringify(dashboard?.language_gate_surface ?? {}, null, 2) })] }), _jsxs("section", { className: "panel", id: "owner-pain-map", children: [_jsx("h2", { children: t("pain") }), _jsx("div", { className: "pain-list", children: painItems.map((item) => (_jsxs("div", { className: "pain-item", children: [_jsx("strong", { children: item.pain_id }), _jsx("span", { children: item.severity }), _jsx("span", { children: item.current_status }), _jsx("code", { children: item.next_task_route })] }, `${item.pain_id}-${item.next_task_route}`))) })] }), _jsxs("section", { className: "panel", id: "routes", children: [_jsx("h2", { children: t("routes") }), _jsx("pre", { children: JSON.stringify({
                                    required_alias: dashboard?.route_surface?.required_alias,
                                    imperium_vm3_visible: dashboard?.route_surface?.imperium_vm3_visible,
                                    canonical_commands_file: dashboard?.route_surface?.canonical_commands_file,
                                }, null, 2) }), _jsx("pre", { className: "file-preview", children: dashboard?.route_surface?.canonical_commands_preview || "" })] }), _jsxs("section", { className: "panel", id: "reports", children: [_jsx("h2", { children: t("reports") }), _jsx("pre", { children: JSON.stringify(dashboard?.report_receipt_summary ?? {}, null, 2) })] }), _jsxs("section", { className: "panel", id: "checks", children: [_jsx("h2", { children: t("checks") }), _jsx("pre", { children: JSON.stringify({
                                    self_validator: dashboard?.self_validator_surface,
                                    desktop_shell_decision: decision,
                                    toolchain_probe_status: probe?.status,
                                    playwright_available: probe?.probes?.find((p) => p.name === "npx_playwright")?.exit_code === 0 || false,
                                    checker_tools: dashboard?.checker_tool_surface,
                                    drift_warning_count: driftWarnings.length,
                                    warnings_sample: (dashboard?.warnings ?? []).slice(0, 12),
                                }, null, 2) })] }), _jsxs("section", { className: "panel", id: "block-foundation", children: [_jsx("h2", { children: t("blockFoundation") }), _jsx("pre", { children: JSON.stringify({
                                    block_foundation_preview: dashboard?.block_foundation_preview,
                                    block_model_warnings: blockModel?.warnings ?? [],
                                }, null, 2) })] }), _jsxs("section", { className: "panel", id: "plugins", children: [_jsx("h2", { children: t("plugins") }), _jsx("pre", { children: JSON.stringify({
                                    providers_count: plugins?.providers?.length ?? 0,
                                    providers_sample: (plugins?.providers ?? []).slice(0, 20),
                                }, null, 2) })] })] })] }));
}
