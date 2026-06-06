from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Tuple

from operator_shell_skin import MECHANICUS_COLORS, SHELL_VERSION_V0_5
from operator_shell_widgets import (
    activity_panel,
    bottom_event_panel,
    command_palette_panel,
    mission_panel,
    raw_detail_panel,
    tool_registry_panel,
    top_status_panel,
)

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Static

    HAVE_TEXTUAL = True
except Exception:
    HAVE_TEXTUAL = False

PayloadLoader = Callable[[str, bool], dict[str, Any]]


if HAVE_TEXTUAL:

    class MechanicusTextualShellApp(App[None]):
        CSS = f"""
        Screen {{
            background: {MECHANICUS_COLORS["bg"]};
            color: {MECHANICUS_COLORS["text_main"]};
        }}
        #root {{
            layout: vertical;
            height: 100%;
        }}
        #main_row {{
            layout: horizontal;
            height: 1fr;
        }}
        #left_col {{
            width: 1fr;
            margin-right: 1;
        }}
        #right_col {{
            width: 1fr;
        }}
        #raw_panel {{
            height: 12;
            margin-top: 1;
        }}
        .hidden {{
            display: none;
        }}
        """

        BINDINGS = [
            Binding("f1", "show_status", "Status"),
            Binding("f2", "show_tools", "Tools"),
            Binding("f3", "show_identity", "Identity"),
            Binding("f4", "show_check", "Check"),
            Binding("f5", "show_where", "Where"),
            Binding("f6", "show_pack", "Pack"),
            Binding("f7", "show_help", "Help"),
            Binding("d", "show_status", "Dashboard"),
            Binding("r", "toggle_raw", "Raw"),
            Binding("s", "save_screenshot", "Screenshot"),
            Binding("escape", "quit_shell", "Exit"),
        ]

        def __init__(
            self,
            *,
            organ_name: str,
            mission: str,
            payload_loader: PayloadLoader,
            shell_version: str = SHELL_VERSION_V0_5,
            screenshot_dir: str | None = None,
        ) -> None:
            super().__init__()
            self.organ_name = organ_name
            self.mission = mission
            self.payload_loader = payload_loader
            self.shell_version = shell_version
            self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else (Path.cwd() / "SCREENSHOTS")
            self.active_command = "status"
            self.detail_mode = False

        def compose(self) -> ComposeResult:
            with Vertical(id="root"):
                yield Static(id="top_status")
                with Horizontal(id="main_row"):
                    with Vertical(id="left_col"):
                        yield Static(id="activity_panel")
                        yield Static(id="mission_panel")
                    with Vertical(id="right_col"):
                        yield Static(id="command_panel")
                        yield Static(id="tools_panel")
                yield Static(id="bottom_panel")
                yield Static(id="raw_panel", classes="hidden")
                yield Footer()

        def on_mount(self) -> None:
            self._render("status", detail=False)

        def _render(self, command: str, detail: bool) -> None:
            payload = self.payload_loader(command, detail)
            self.active_command = command
            self.detail_mode = detail

            self.query_one("#top_status", Static).update(
                top_status_panel(payload, organ_name=self.organ_name, mission=self.mission, shell_version=self.shell_version)
            )
            self.query_one("#activity_panel", Static).update(activity_panel(payload))
            self.query_one("#mission_panel", Static).update(mission_panel(payload, self.mission))
            self.query_one("#command_panel", Static).update(command_palette_panel(payload))
            self.query_one("#tools_panel", Static).update(tool_registry_panel(payload))
            self.query_one("#bottom_panel", Static).update(bottom_event_panel(payload))

            raw_node = self.query_one("#raw_panel", Static)
            if detail:
                raw_node.remove_class("hidden")
                raw_node.update(raw_detail_panel(payload))
            else:
                raw_node.add_class("hidden")
                raw_node.update("")

        def _switch(self, command: str) -> None:
            self._render(command, detail=False)

        def action_show_status(self) -> None:
            self._switch("status")

        def action_show_tools(self) -> None:
            self._switch("tools")

        def action_show_identity(self) -> None:
            self._switch("identity")

        def action_show_check(self) -> None:
            self._switch("check")

        def action_show_where(self) -> None:
            self._switch("where")

        def action_show_pack(self) -> None:
            self._switch("pack")

        def action_show_help(self) -> None:
            self._switch("help")

        def action_toggle_raw(self) -> None:
            self._render(self.active_command, detail=True)

        def _mode_token(self) -> str:
            if self.detail_mode:
                return "raw"
            if self.active_command == "status":
                return "dashboard"
            return self.active_command

        def action_save_screenshot(self) -> None:
            mode = self._mode_token()
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            filename = f"mechanicus_{mode}_{self.shell_version}_{stamp}.svg".replace(" ", "_")
            target = self.screenshot_dir / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                saved = self.save_screenshot(str(target))
                self.notify(f"Screenshot saved: {saved}")
            except Exception as exc:
                self.notify(f"Screenshot failed: {exc}", severity="error")

        def action_quit_shell(self) -> None:
            self.exit()

else:

    class MechanicusTextualShellApp:  # pragma: no cover - runtime fallback type only
        pass


def textual_runtime_available() -> bool:
    return HAVE_TEXTUAL


def launch_textual_operator_shell(
    *,
    organ_name: str,
    mission: str,
    payload_loader: PayloadLoader,
    shell_version: str = SHELL_VERSION_V0_5,
    screenshot_dir: str | None = None,
) -> Tuple[bool, str]:
    if not HAVE_TEXTUAL:
        return False, "textual_runtime_unavailable"
    try:
        app = MechanicusTextualShellApp(
            organ_name=organ_name,
            mission=mission,
            payload_loader=payload_loader,
            shell_version=shell_version,
            screenshot_dir=screenshot_dir,
        )
        app.run()
        return True, "textual_runtime_ok"
    except Exception as exc:
        return False, f"textual_runtime_error:{exc}"
