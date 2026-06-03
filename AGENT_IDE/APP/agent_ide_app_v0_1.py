from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import tkinter as tk
from tkinter import ttk

from agent_ide_data_loader_v0_1 import build_view_model


I18N: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "IMPERIUM Agent IDE V0.1 (Read-only)",
        "language": "Language",
        "reload": "Reload Data",
        "session": "Current Truth / Session",
        "organs": "Organs",
        "atlas": "File Atlas",
        "details": "Selected File",
        "surfaces": "Role / Rule / Language / Tools",
        "routes": "Routes / Reports / Receipts",
        "pain": "Problems / Pain / Gaps",
        "warnings": "Warnings",
        "unknown_count": "Unknown file kind count",
        "filter_query": "Query",
        "filter_organ": "Organ",
        "filter_kind": "Kind",
        "filter_status": "Status",
        "filter_pain": "Pain",
        "all": "ALL",
        "route_alias": "Route alias",
        "route_visible": "Visible",
        "route_missing": "Missing",
    },
    "ru": {
        "app_title": "IMPERIUM Agent IDE V0.1 (Только чтение)",
        "language": "Язык",
        "reload": "Перезагрузить данные",
        "session": "Текущая истина / Сессия",
        "organs": "Органы",
        "atlas": "Атлас файлов",
        "details": "Выбранный файл",
        "surfaces": "Роли / Правила / Language gate / Tools",
        "routes": "Маршруты / Отчёты / Квитанции",
        "pain": "Проблемы / Боли / Gaps",
        "warnings": "Предупреждения",
        "unknown_count": "Количество UNKNOWN kind",
        "filter_query": "Поиск",
        "filter_organ": "Орган",
        "filter_kind": "Kind",
        "filter_status": "Статус",
        "filter_pain": "Боль",
        "all": "ВСЕ",
        "route_alias": "Route alias",
        "route_visible": "Виден",
        "route_missing": "Не найден",
    },
}


class AgentIdeApp(tk.Tk):
    def __init__(self, model: Dict[str, Any], language: str = "en") -> None:
        super().__init__()
        self.model = model
        self.language = language if language in I18N else "en"
        self.filtered_passports: List[Dict[str, Any]] = []
        self.selected_path: str = ""

        self.query_var = tk.StringVar(value="")
        self.organ_var = tk.StringVar(value="")
        self.kind_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")
        self.pain_var = tk.StringVar(value="")
        self.language_var = tk.StringVar(value=self.language)

        self.title(self._t("app_title"))
        self.geometry("1400x900")
        self.minsize(1100, 720)
        self._build_ui()

    def _t(self, key: str) -> str:
        return I18N.get(self.language, I18N["en"]).get(key, key)

    def _build_ui(self) -> None:
        for child in list(self.winfo_children()):
            child.destroy()

        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text=f"{self._t('language')}:").pack(side=tk.LEFT)
        lang_picker = ttk.Combobox(
            top,
            textvariable=self.language_var,
            values=["en", "ru"],
            width=6,
            state="readonly",
        )
        lang_picker.pack(side=tk.LEFT, padx=(6, 10))
        lang_picker.bind("<<ComboboxSelected>>", self._on_language_changed)

        ttk.Button(top, text=self._t("reload"), command=self._reload_data).pack(side=tk.LEFT)

        self.warning_label = ttk.Label(top, text="")
        self.warning_label.pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.session_tab = ttk.Frame(notebook, padding=10)
        self.organs_tab = ttk.Frame(notebook, padding=10)
        self.atlas_tab = ttk.Frame(notebook, padding=10)
        self.details_tab = ttk.Frame(notebook, padding=10)
        self.surfaces_tab = ttk.Frame(notebook, padding=10)
        self.routes_tab = ttk.Frame(notebook, padding=10)
        self.pain_tab = ttk.Frame(notebook, padding=10)

        notebook.add(self.session_tab, text=self._t("session"))
        notebook.add(self.organs_tab, text=self._t("organs"))
        notebook.add(self.atlas_tab, text=self._t("atlas"))
        notebook.add(self.details_tab, text=self._t("details"))
        notebook.add(self.surfaces_tab, text=self._t("surfaces"))
        notebook.add(self.routes_tab, text=self._t("routes"))
        notebook.add(self.pain_tab, text=self._t("pain"))

        self._build_session_tab()
        self._build_organs_tab()
        self._build_atlas_tab()
        self._build_details_tab()
        self._build_surfaces_tab()
        self._build_routes_tab()
        self._build_pain_tab()

        self._refresh_warning_label()
        self._apply_filters()

    def _build_session_tab(self) -> None:
        truth = self.model.get("truth", {})
        git_truth = truth.get("git", {})
        lines = [
            f"task_id: {self.model.get('task_id', '')}",
            f"repo_root: {truth.get('repo_root', '')}",
            f"branch: {git_truth.get('branch', 'UNKNOWN')}",
            f"head: {git_truth.get('head', 'UNKNOWN')}",
            f"loaded_sources: {len(truth.get('loaded_sources', {}))}",
            f"missing_sources: {len(truth.get('missing_sources', []))}",
            f"{self._t('unknown_count')}: {self.model.get('unknown_file_kind_count', 0)}",
        ]
        box = tk.Text(self.session_tab, wrap="word", height=18)
        box.insert("1.0", "\n".join(lines))
        box.configure(state="disabled")
        box.pack(fill=tk.BOTH, expand=True)

        warnings = self.model.get("warnings", [])
        warn = tk.Text(self.session_tab, wrap="word", height=10)
        warn.insert("1.0", "\n".join(warnings) if warnings else "NO_WARNINGS")
        warn.configure(state="disabled")
        warn.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _build_organs_tab(self) -> None:
        cols = ("organ", "file_count", "status")
        tree = ttk.Treeview(self.organs_tab, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=220 if col == "organ" else 140, anchor=tk.W)
        for row in self.model.get("organs", []):
            tree.insert("", tk.END, values=(row.get("organ"), row.get("file_count"), row.get("status")))
        tree.pack(fill=tk.BOTH, expand=True)
        self.organs_tree = tree

    def _build_atlas_tab(self) -> None:
        filter_row = ttk.Frame(self.atlas_tab)
        filter_row.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_row, text=f"{self._t('filter_query')}:").pack(side=tk.LEFT)
        query_entry = ttk.Entry(filter_row, textvariable=self.query_var, width=26)
        query_entry.pack(side=tk.LEFT, padx=(4, 8))
        query_entry.bind("<KeyRelease>", lambda _event: self._apply_filters())

        ttk.Label(filter_row, text=f"{self._t('filter_organ')}:").pack(side=tk.LEFT)
        self.organ_combo = ttk.Combobox(filter_row, textvariable=self.organ_var, width=20, state="readonly")
        self.organ_combo.pack(side=tk.LEFT, padx=(4, 8))
        self.organ_combo.bind("<<ComboboxSelected>>", lambda _event: self._apply_filters())

        ttk.Label(filter_row, text=f"{self._t('filter_kind')}:").pack(side=tk.LEFT)
        self.kind_combo = ttk.Combobox(filter_row, textvariable=self.kind_var, width=18, state="readonly")
        self.kind_combo.pack(side=tk.LEFT, padx=(4, 8))
        self.kind_combo.bind("<<ComboboxSelected>>", lambda _event: self._apply_filters())

        ttk.Label(filter_row, text=f"{self._t('filter_status')}:").pack(side=tk.LEFT)
        self.status_combo = ttk.Combobox(filter_row, textvariable=self.status_var, width=14, state="readonly")
        self.status_combo.pack(side=tk.LEFT, padx=(4, 8))
        self.status_combo.bind("<<ComboboxSelected>>", lambda _event: self._apply_filters())

        ttk.Label(filter_row, text=f"{self._t('filter_pain')}:").pack(side=tk.LEFT)
        self.pain_combo = ttk.Combobox(filter_row, textvariable=self.pain_var, width=28, state="readonly")
        self.pain_combo.pack(side=tk.LEFT, padx=(4, 8))
        self.pain_combo.bind("<<ComboboxSelected>>", lambda _event: self._apply_filters())

        cols = ("path", "owner_organ", "file_kind", "status", "edit_surface", "warnings")
        tree = ttk.Treeview(self.atlas_tab, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            width = 480 if col == "path" else 120
            tree.column(col, width=width, anchor=tk.W)
        tree.bind("<<TreeviewSelect>>", self._on_passport_select)
        tree.pack(fill=tk.BOTH, expand=True)
        self.passports_tree = tree

        passports = self.model.get("file_passports", [])
        organs = sorted({str(p.get("owner_organ", "UNKNOWN")) for p in passports})
        kinds = sorted({str(p.get("file_kind", "UNKNOWN")) for p in passports})
        statuses = sorted({str(p.get("status", "UNKNOWN")) for p in passports})
        pains = sorted({pain for p in passports for pain in p.get("related_owner_pains", [])})
        all_value = self._t("all")

        self.organ_combo["values"] = [all_value, *organs]
        self.kind_combo["values"] = [all_value, *kinds]
        self.status_combo["values"] = [all_value, *statuses]
        self.pain_combo["values"] = [all_value, *pains]

        self.organ_var.set(all_value)
        self.kind_var.set(all_value)
        self.status_var.set(all_value)
        self.pain_var.set(all_value)

    def _build_details_tab(self) -> None:
        self.details_text = tk.Text(self.details_tab, wrap="word")
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self._render_selected_file()

    def _build_surfaces_tab(self) -> None:
        surfaces_notebook = ttk.Notebook(self.surfaces_tab)
        surfaces_notebook.pack(fill=tk.BOTH, expand=True)

        tabs = {
            "role_rule_surface": "Role/Rule",
            "language_gate_surface": "Language Gate",
            "checker_tool_surface": "Tools/Checkers",
            "tui_surface": "TUI",
        }

        for key, label in tabs.items():
            tab = ttk.Frame(surfaces_notebook, padding=8)
            surfaces_notebook.add(tab, text=label)
            text = tk.Text(tab, wrap="none")
            text.insert("1.0", json.dumps(self.model.get(key, {}), indent=2, ensure_ascii=False))
            text.configure(state="disabled")
            text.pack(fill=tk.BOTH, expand=True)

    def _build_routes_tab(self) -> None:
        route = self.model.get("route_surface", {})
        report = self.model.get("report_receipt_surface", {})

        alias = str(route.get("required_alias", "imperium-vm3"))
        visible = bool(route.get("imperium_vm3_visible", False))
        visible_text = self._t("route_visible") if visible else self._t("route_missing")
        summary = f"{self._t('route_alias')}: {alias} | {visible_text}"
        ttk.Label(self.routes_tab, text=summary).pack(anchor="w", pady=(0, 8))

        paned = ttk.Panedwindow(self.routes_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=4)
        right = ttk.Frame(paned, padding=4)
        paned.add(left, weight=1)
        paned.add(right, weight=1)

        route_text = tk.Text(left, wrap="none")
        route_text.insert("1.0", json.dumps(route, indent=2, ensure_ascii=False))
        route_text.configure(state="disabled")
        route_text.pack(fill=tk.BOTH, expand=True)

        right_notebook = ttk.Notebook(right)
        right_notebook.pack(fill=tk.BOTH, expand=True)

        report_tab = ttk.Frame(right_notebook, padding=6)
        commands_tab = ttk.Frame(right_notebook, padding=6)
        right_notebook.add(report_tab, text="Reports/Receipts")
        right_notebook.add(commands_tab, text="Canonical Commands")

        report_text = tk.Text(report_tab, wrap="none")
        report_text.insert("1.0", json.dumps(report, indent=2, ensure_ascii=False))
        report_text.configure(state="disabled")
        report_text.pack(fill=tk.BOTH, expand=True)

        cmd_preview = route.get("canonical_commands_preview", "")
        if not cmd_preview:
            cmd_preview = "canonical_transfer_commands.md not found in route surfaces."
        cmd_text = tk.Text(commands_tab, wrap="word")
        cmd_text.insert("1.0", cmd_preview)
        cmd_text.configure(state="disabled")
        cmd_text.pack(fill=tk.BOTH, expand=True)

    def _build_pain_tab(self) -> None:
        pain = self.model.get("owner_pain_map", {})
        gap_success = self.model.get("gap_success", {})

        top_line = f"{self._t('unknown_count')}: {self.model.get('unknown_file_kind_count', 0)}"
        ttk.Label(self.pain_tab, text=top_line).pack(anchor="w", pady=(0, 8))

        paned = ttk.Panedwindow(self.pain_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(paned, padding=4)
        right = ttk.Frame(paned, padding=4)
        paned.add(left, weight=1)
        paned.add(right, weight=1)

        pain_text = tk.Text(left, wrap="none")
        pain_text.insert("1.0", json.dumps(pain, indent=2, ensure_ascii=False))
        pain_text.configure(state="disabled")
        pain_text.pack(fill=tk.BOTH, expand=True)

        gap_text = tk.Text(right, wrap="none")
        gap_text.insert("1.0", json.dumps(gap_success, indent=2, ensure_ascii=False))
        gap_text.configure(state="disabled")
        gap_text.pack(fill=tk.BOTH, expand=True)

    def _apply_filters(self) -> None:
        passports = self.model.get("file_passports", [])
        query = self.query_var.get().strip().lower()
        organ_filter = self.organ_var.get().strip()
        kind_filter = self.kind_var.get().strip()
        status_filter = self.status_var.get().strip()
        pain_filter = self.pain_var.get().strip()
        all_value = self._t("all")

        self.filtered_passports = []
        for item in passports:
            path = str(item.get("path", ""))
            organ = str(item.get("owner_organ", ""))
            kind = str(item.get("file_kind", ""))
            status = str(item.get("status", ""))
            pains = [str(x) for x in item.get("related_owner_pains", [])]

            if query and query not in path.lower() and query not in str(item.get("purpose_short", "")).lower():
                continue
            if organ_filter and organ_filter != all_value and organ != organ_filter:
                continue
            if kind_filter and kind_filter != all_value and kind != kind_filter:
                continue
            if status_filter and status_filter != all_value and status != status_filter:
                continue
            if pain_filter and pain_filter != all_value and pain_filter not in pains:
                continue

            self.filtered_passports.append(item)

        self.passports_tree.delete(*self.passports_tree.get_children())
        for item in self.filtered_passports:
            self.passports_tree.insert(
                "",
                tk.END,
                values=(
                    item.get("path", ""),
                    item.get("owner_organ", ""),
                    item.get("file_kind", ""),
                    item.get("status", ""),
                    item.get("edit_surface", ""),
                    ",".join(item.get("warnings", [])),
                ),
            )

        if self.filtered_passports:
            self.selected_path = str(self.filtered_passports[0].get("path", ""))
        else:
            self.selected_path = ""
        self._render_selected_file()

    def _on_passport_select(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.passports_tree.selection()
        if not selected:
            return
        values = self.passports_tree.item(selected[0], "values")
        if values:
            self.selected_path = str(values[0])
            self._render_selected_file()

    def _render_selected_file(self) -> None:
        selected = None
        for item in self.model.get("file_passports", []):
            if item.get("path") == self.selected_path:
                selected = item
                break
        if selected is None and self.model.get("file_passports"):
            selected = self.model["file_passports"][0]
            self.selected_path = str(selected.get("path", ""))

        payload = selected if selected is not None else {"note": "No file selected"}
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert("1.0", json.dumps(payload, indent=2, ensure_ascii=False))
        self.details_text.configure(state="disabled")

    def _refresh_warning_label(self) -> None:
        warning_count = len(self.model.get("warnings", []))
        text = f"{self._t('warnings')}: {warning_count} | {self._t('unknown_count')}: {self.model.get('unknown_file_kind_count', 0)}"
        self.warning_label.configure(text=text)

    def _on_language_changed(self, _event: tk.Event[tk.Misc]) -> None:
        new_lang = self.language_var.get().strip().lower()
        if new_lang in I18N and new_lang != self.language:
            self.language = new_lang
            self.title(self._t("app_title"))
            self._build_ui()

    def _reload_data(self) -> None:
        self.model = build_view_model().to_dict()
        self._build_ui()


def run_smoke(repo_root: Path | None = None) -> Dict[str, Any]:
    model = build_view_model(repo_root).to_dict()
    summary = {
        "task_id": model.get("task_id"),
        "organs_visible": len(model.get("organs", [])),
        "passports": len(model.get("file_passports", [])),
        "warnings": len(model.get("warnings", [])),
        "unknown_file_kind_count": model.get("unknown_file_kind_count", 0),
        "route_alias_required": model.get("route_surface", {}).get("required_alias", ""),
        "route_alias_visible": model.get("route_surface", {}).get("imperium_vm3_visible", False),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM Agent IDE V0.1 (read-only)")
    parser.add_argument("--lang", choices=["en", "ru"], default="en")
    parser.add_argument("--smoke", action="store_true", help="Run non-GUI smoke check and exit.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else None

    if args.smoke:
        result = run_smoke(repo_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    model = build_view_model(repo_root).to_dict()
    app = AgentIdeApp(model=model, language=args.lang)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
