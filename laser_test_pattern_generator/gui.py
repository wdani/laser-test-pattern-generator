from __future__ import annotations

import copy
from pathlib import Path
from typing import Dict, Optional

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None
    ttk = None
    filedialog = None
    messagebox = None

from .generator_mks import generate_mks
from .generator_nc import fmt_num, generate_generic_nc, profile_for_nc_s_max
from .geometry import computed_layout, linspace, validate_layout
from .paths import expected_output_suffix_for_format, sync_output_suffix_for_format
from .presets import (
    PRESET_METADATA_FIELDS,
    export_preset_file,
    find_preset_path,
    import_preset_file,
    list_presets,
    preset_dir,
    preset_path,
    read_preset_file,
    save_preset_data,
    write_preset_file,
)
from .settings import (
    APP_VERSION,
    DEFAULT_NC_POWER_PROFILE,
    GeneratorSettings,
    LASER_MODES,
    NC_POWER_PROFILES,
)
from .ui_settings import THEME_CHOICES, load_ui_settings, normalize_theme_name, save_ui_settings


THEME_PALETTES = {
    "Light": {
        "bg": "#f4f6f8",
        "panel": "#ffffff",
        "panel_alt": "#eef2f6",
        "text": "#1f2933",
        "muted": "#52616f",
        "border": "#cfd8e3",
        "entry_bg": "#ffffff",
        "entry_text": "#1f2933",
        "select_bg": "#dbeafe",
        "select_text": "#111827",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "accent_text": "#ffffff",
        "subtle_button": "#e5eaf0",
        "success": "#166534",
        "warning": "#9a3412",
        "error": "#b91c1c",
        "preview_bg": "#ffffff",
        "preview_stock": "#1f2933",
        "preview_text": "#334155",
        "preview_bounds": "#cc7a00",
        "preview_grid": "#0f4c81",
        "preview_tile_fill": "#eef6ff",
        "preview_label_zone": "#d7a35d",
        "status_bg": "#ffffff",
        "tooltip_bg": "#ffffe6",
        "tooltip_text": "#1f2933",
    },
    "Dark": {
        "bg": "#111827",
        "panel": "#1f2937",
        "panel_alt": "#273445",
        "text": "#e5e7eb",
        "muted": "#a7b0bd",
        "border": "#3b4656",
        "entry_bg": "#111827",
        "entry_text": "#f3f4f6",
        "select_bg": "#1d4ed8",
        "select_text": "#ffffff",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "accent_text": "#ffffff",
        "subtle_button": "#374151",
        "success": "#86efac",
        "warning": "#fdba74",
        "error": "#fca5a5",
        "preview_bg": "#0f172a",
        "preview_stock": "#e5e7eb",
        "preview_text": "#cbd5e1",
        "preview_bounds": "#fbbf24",
        "preview_grid": "#93c5fd",
        "preview_tile_fill": "#1e3a5f",
        "preview_label_zone": "#c084fc",
        "status_bg": "#0f172a",
        "tooltip_bg": "#1f2937",
        "tooltip_text": "#f3f4f6",
    },
}


class Tooltip:
    def __init__(self, widget, text: str, bg: str, fg: str, delay_ms: int = 600) -> None:
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.delay_ms = delay_ms
        self._after_id: Optional[str] = None
        self._window = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None) -> None:
        self._cancel()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _cancel(self) -> None:
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self) -> None:
        self._after_id = None
        if self._window or not self.text:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self._window = tk.Toplevel(self.widget)
        self._window.wm_overrideredirect(True)
        self._window.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            self._window,
            text=self.text,
            justify="left",
            background=self.bg,
            foreground=self.fg,
            relief="solid",
            borderwidth=1,
            padding=(6, 4),
            wraplength=320,
        )
        label.pack()

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._window:
            self._window.destroy()
            self._window = None


class GeneratorGui:
    def __init__(self) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available")

        self.root = tk.Tk()
        self.root.title(f"Makera Material Test Generator {APP_VERSION}")
        self.root.geometry("1280x820")
        self.root.minsize(980, 700)
        self.style = ttk.Style(self.root)
        self.theme_name = normalize_theme_name(load_ui_settings().get("theme"))
        self.palette = THEME_PALETTES[self.theme_name]
        self.vars: Dict[str, tk.Variable] = {}
        self.preset_names_var = tk.StringVar(value="")
        self._preview_after_id: Optional[str] = None
        self._side_preview_visible = True
        self._apply_theme(self.theme_name)
        self._build()
        self._refresh_presets()
        self._bind_auto_preview_updates()
        self._schedule_preview_refresh()

    def _var(self, name: str, default, cls=tk.StringVar):
        v = cls(value=default)
        self.vars[name] = v
        return v

    def _tooltip(self, widget, text: str):
        if text:
            Tooltip(widget, text, self.palette["tooltip_bg"], self.palette["tooltip_text"])
        return widget

    def _hint(self, parent, text: str, row: int, column: int = 0, columnspan: int = 4):
        label = ttk.Label(parent, text=text, style="Hint.TLabel", wraplength=760)
        label.grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=6, pady=(2, 10))
        return label

    def _entry(
        self,
        parent,
        label: str,
        varname: str,
        default,
        row: int,
        col: int = 0,
        width: int = 12,
        tooltip: str = "",
        spin: bool = False,
        from_: float = 0,
        to: float = 100000,
        increment: float = 1,
        format_: Optional[str] = None,
    ):
        lbl = ttk.Label(parent, text=label)
        lbl.grid(row=row, column=col, sticky="w", padx=6, pady=4)
        var = self._var(varname, default)
        if spin:
            wrapper = ttk.Frame(parent, style="Numeric.TFrame")
            ent = ttk.Entry(wrapper, textvariable=var, width=width)
            ent.pack(side="left", fill="x")
            minus = ttk.Button(
                wrapper,
                text="-",
                width=2,
                style="Numeric.TButton",
                command=lambda: self._step_numeric_var(var, -increment, from_, to, increment, format_),
            )
            plus = ttk.Button(
                wrapper,
                text="+",
                width=2,
                style="Numeric.TButton",
                command=lambda: self._step_numeric_var(var, increment, from_, to, increment, format_),
            )
            minus.pack(side="left", padx=(4, 1))
            plus.pack(side="left", padx=(1, 0))
            wrapper.grid(row=row, column=col + 1, sticky="w", padx=6, pady=4)
            if tooltip:
                self._tooltip(minus, tooltip)
                self._tooltip(plus, tooltip)
        else:
            ent = ttk.Entry(parent, textvariable=var, width=width)
            ent.grid(row=row, column=col + 1, sticky="w", padx=6, pady=4)
        if tooltip:
            self._tooltip(lbl, tooltip)
            self._tooltip(ent, tooltip)
        return ent

    def _step_numeric_var(self, var, delta: float, minimum: float, maximum: float, increment: float, format_: Optional[str]) -> None:
        current_text = str(var.get()).strip()
        try:
            current = float(current_text)
        except ValueError:
            current = minimum if delta > 0 else maximum

        value = min(max(current + delta, minimum), maximum)
        var.set(self._format_numeric_value(value, increment, format_))

    def _format_numeric_value(self, value: float, increment: float, format_: Optional[str] = None) -> str:
        if format_:
            return format_ % value
        if float(increment).is_integer() and float(value).is_integer():
            return str(int(round(value)))
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text or "0"

    def _apply_theme(self, theme_name: str, persist: bool = False) -> None:
        self.theme_name = normalize_theme_name(theme_name)
        self.palette = THEME_PALETTES[self.theme_name]
        if persist:
            try:
                save_ui_settings({"theme": self.theme_name})
            except Exception as exc:
                if hasattr(self, "status"):
                    self._log("WARNING: Could not save UI theme setting: " + str(exc))

        p = self.palette
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(background=p["bg"])
        self.root.option_add("*TCombobox*Listbox.background", p["entry_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", p["entry_text"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", p["select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", p["select_text"])

        self.style.configure(".", background=p["bg"], foreground=p["text"], font=("Segoe UI", 9))
        self.style.configure("TFrame", background=p["bg"])
        self.style.configure("TLabel", background=p["bg"], foreground=p["text"])
        self.style.configure("Hint.TLabel", background=p["bg"], foreground=p["muted"])
        self.style.configure("Safety.TLabel", background=p["bg"], foreground=p["warning"])
        self.style.configure("TLabelframe", background=p["bg"], bordercolor=p["border"], relief="solid")
        self.style.configure("TLabelframe.Label", background=p["bg"], foreground=p["text"], font=("Segoe UI", 9, "bold"))
        self.style.configure("TNotebook", background=p["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=p["panel_alt"], foreground=p["muted"], padding=(14, 7))
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", p["panel"]), ("active", p["panel"])],
            foreground=[("selected", p["text"]), ("active", p["text"])],
        )
        self.style.configure("TEntry", fieldbackground=p["entry_bg"], foreground=p["entry_text"], bordercolor=p["border"], insertcolor=p["entry_text"], padding=4)
        self.style.configure("TCombobox", fieldbackground=p["entry_bg"], foreground=p["entry_text"], bordercolor=p["border"], arrowcolor=p["muted"], padding=4)
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", p["entry_bg"])],
            selectbackground=[("readonly", p["entry_bg"])],
            selectforeground=[("readonly", p["entry_text"])],
            foreground=[("readonly", p["entry_text"])],
        )
        self.style.configure("TCheckbutton", background=p["bg"], foreground=p["text"], padding=4)
        self.style.configure("TButton", background=p["subtle_button"], foreground=p["text"], padding=(12, 7), borderwidth=1)
        self.style.map("TButton", background=[("active", p["panel_alt"])], foreground=[("disabled", p["muted"])])
        self.style.configure("Accent.TButton", background=p["accent"], foreground=p["accent_text"], padding=(14, 8), borderwidth=1)
        self.style.map("Accent.TButton", background=[("active", p["accent_hover"])], foreground=[("active", p["accent_text"])])
        self.style.configure("Subtle.TButton", background=p["subtle_button"], foreground=p["muted"], padding=(10, 6), borderwidth=1)
        self.style.configure("Numeric.TFrame", background=p["bg"])
        self.style.configure("Numeric.TButton", background=p["panel_alt"], foreground=p["text"], padding=(4, 2), borderwidth=1, relief="flat")
        self.style.map(
            "Numeric.TButton",
            background=[("active", p["subtle_button"])],
            foreground=[("active", p["text"]), ("disabled", p["muted"])],
        )

        self._style_tk_widgets()
        if hasattr(self, "side_preview_canvas") or hasattr(self, "preview_canvas"):
            self._refresh_preview(log_warning=True)

    def _style_tk_widgets(self) -> None:
        p = self.palette
        if hasattr(self, "status"):
            self.status.configure(
                bg=p["status_bg"],
                fg=p["text"],
                insertbackground=p["text"],
                selectbackground=p["select_bg"],
                selectforeground=p["select_text"],
                relief="flat",
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=p["border"],
            )
            self.status.tag_configure("warning", foreground=p["warning"])
            self.status.tag_configure("error", foreground=p["error"])
            self.status.tag_configure("success", foreground=p["success"])

        if hasattr(self, "preview_text"):
            self.preview_text.configure(
                bg=p["panel"],
                fg=p["text"],
                insertbackground=p["text"],
                selectbackground=p["select_bg"],
                selectforeground=p["select_text"],
                relief="flat",
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=p["border"],
            )
            self.preview_text.tag_configure("heading", foreground=p["text"], font=("Segoe UI", 10, "bold"))
            self.preview_text.tag_configure("warning", foreground=p["warning"])
            self.preview_text.tag_configure("ok", foreground=p["success"])

        for name in ("preview_canvas", "side_preview_canvas"):
            if hasattr(self, name):
                getattr(self, name).configure(bg=p["preview_bg"], highlightbackground=p["border"])

    def _on_theme_changed(self, _event=None) -> None:
        theme = normalize_theme_name(self.vars["ui_theme"].get())
        self.vars["ui_theme"].set(theme)
        self._apply_theme(theme, persist=True)
        self._log(f"Theme set to {theme}.")

    def _build(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        output = ttk.LabelFrame(main, text="Output")
        output.pack(fill="x", pady=(0, 8))

        self._var("output", str(Path.cwd() / "makera_material_test_generated.mks"))
        output_entry = ttk.Entry(output, textvariable=self.vars["output"], width=78)
        output_entry.grid(row=0, column=0, columnspan=5, padx=6, pady=6, sticky="we")
        self._tooltip(output_entry, "Known generated suffixes .mks and .nc follow the selected format.")
        ttk.Button(output, text="Browse...", command=self._browse_output, style="Subtle.TButton").grid(row=0, column=5, padx=6, pady=6)

        self._var("output_format", "MKS")
        ttk.Label(output, text="Format").grid(row=1, column=0, sticky="w", padx=6, pady=3)
        format_combo = ttk.Combobox(output, textvariable=self.vars["output_format"], values=["MKS", "NC", "Both"], state="readonly", width=10)
        format_combo.grid(row=1, column=1, sticky="w", padx=6, pady=3)
        format_combo.bind("<<ComboboxSelected>>", self._on_output_format_changed)
        self._tooltip(format_combo, "MKS is a Makera Studio project. NC is generic G-code. Both creates both files.")

        self.vars["overwrite_existing"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(output, text="Overwrite existing file", variable=self.vars["overwrite_existing"]).grid(row=1, column=2, sticky="w", padx=6, pady=3)

        self.vars["auto_filename"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(output, text="Auto filename", variable=self.vars["auto_filename"]).grid(row=1, column=3, sticky="w", padx=6, pady=3)
        ttk.Label(output, text="Material").grid(row=1, column=4, sticky="e", padx=6, pady=3)
        ttk.Entry(output, textvariable=self._var("material_name", "material"), width=16).grid(row=1, column=5, sticky="w", padx=6, pady=3)
        ttk.Label(
            output,
            text="MKS = Makera Studio project. NC = generic G-code / NC. Both keeps .mks as the visible base path.",
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))
        ttk.Label(output, text="Theme").grid(row=2, column=4, sticky="e", padx=6, pady=(0, 6))
        self._var("ui_theme", self.theme_name)
        theme_combo = ttk.Combobox(output, textvariable=self.vars["ui_theme"], values=list(THEME_CHOICES), state="readonly", width=10)
        theme_combo.grid(row=2, column=5, sticky="w", padx=6, pady=(0, 6))
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)
        self._tooltip(theme_combo, "Switch between Light and Dark UI themes. The choice is saved locally.")
        output.columnconfigure(0, weight=1)

        safety = ttk.Label(
            main,
            text="Safety / verify: presets are starting points. Always preview generated files before running the laser.",
            style="Safety.TLabel",
            wraplength=1100,
        )
        safety.pack(fill="x", pady=(0, 8))

        work = ttk.Frame(main)
        work.pack(fill="both", expand=True)
        work.rowconfigure(0, weight=1)
        work.columnconfigure(0, weight=3, minsize=620)
        work.columnconfigure(1, weight=1, minsize=290)
        self.work_area = work

        left = ttk.Frame(work)
        left.grid(row=0, column=0, sticky="nsew")

        tabs = ttk.Notebook(left)
        tabs.pack(fill="both", expand=True)
        self.tabs = tabs

        self.tab_grid = ttk.Frame(tabs, padding=10)
        self.tab_params = ttk.Frame(tabs, padding=10)
        self.tab_laser = ttk.Frame(tabs, padding=10)
        self.tab_labels = ttk.Frame(tabs, padding=10)
        self.tab_preview = ttk.Frame(tabs, padding=10)
        self.tab_presets = ttk.Frame(tabs, padding=10)

        tabs.add(self.tab_grid, text="Grid / Stock")
        tabs.add(self.tab_params, text="Parameters")
        tabs.add(self.tab_laser, text="Laser / NC")
        tabs.add(self.tab_labels, text="Labels")
        tabs.add(self.tab_preview, text="Preview")
        tabs.add(self.tab_presets, text="Presets")

        self._build_grid_tab()
        self._build_params_tab()
        self._build_laser_tab()
        self._build_labels_tab()
        self._build_preview_tab()
        self._build_presets_tab()
        tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed, add="+")

        self._build_bottom_bar(main)

        self._build_side_preview(work)
        self.root.bind("<Configure>", self._update_side_preview_visibility, add="+")
        self._style_tk_widgets()

    def _build_bottom_bar(self, parent):
        buttons = ttk.Frame(parent)
        buttons.pack(fill="x", pady=(8, 4))
        ttk.Button(buttons, text="Generate", command=self._generate, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Label(buttons, text="Flow: choose output, set grid and laser values, preview, generate, verify.", style="Hint.TLabel").pack(side="left", padx=6)

        self.status = tk.Text(parent, height=7, wrap="word")
        self.status.pack(fill="x", expand=False)
        self.status.tag_configure("warning", foreground="#9a3412")
        self.status.tag_configure("error", foreground="#b91c1c")
        self.status.tag_configure("success", foreground="#166534")
        self._log("Ready. Choose output, preview the layout, generate files, then verify them before running.")

    def _build_grid_tab(self):
        f = self.tab_grid
        f.columnconfigure(0, weight=1)

        grid = ttk.LabelFrame(f, text="Test grid")
        grid.grid(row=0, column=0, sticky="we", padx=2, pady=(0, 10))
        self._entry(grid, "Rows", "rows", "6", 0, 0, tooltip="Rows vary the speed range from bottom to top.", spin=True, from_=1, to=100, increment=1)
        self._entry(grid, "Columns", "cols", "6", 0, 2, tooltip="Columns vary the power range from left to right.", spin=True, from_=1, to=100, increment=1)
        self._entry(grid, "Tile size (mm)", "tile_size", "8.0", 1, 0, spin=True, from_=0.5, to=500, increment=0.5)
        self._entry(grid, "Gap (mm)", "gap", "2.0", 1, 2, spin=True, from_=0, to=200, increment=0.5)
        self._hint(grid, "Rows and columns define the experiment grid. Tile size and gap only affect layout.", 2)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        position = ttk.LabelFrame(f, text="Grid position")
        position.grid(row=1, column=0, sticky="we", padx=2, pady=(0, 10))
        self.vars["auto_position"] = tk.BooleanVar(value=True)
        auto = ttk.Checkbutton(position, text="Auto position inside stock", variable=self.vars["auto_position"])
        auto.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self._tooltip(auto, "When enabled, the grid is placed inside the stock with room for labels.")
        self._entry(position, "Grid X manual", "grid_x", "18.0", 1, 0, tooltip="Used only when Auto position is disabled.", spin=True, from_=-1000, to=1000, increment=1)
        self._entry(position, "Grid Y manual", "grid_y", "8.0", 1, 2, tooltip="Used only when Auto position is disabled.", spin=True, from_=-1000, to=1000, increment=1)
        self._hint(position, "Manual Grid X/Y are used only when Auto position is disabled.", 2)

        stock = ttk.LabelFrame(f, text="Stock")
        stock.grid(row=2, column=0, sticky="we", padx=2, pady=(0, 10))
        self._entry(stock, "Stock X (mm)", "stock_x", "100", 0, 0, spin=True, from_=1, to=2000, increment=1)
        self._entry(stock, "Stock Y (mm)", "stock_y", "100", 0, 2, spin=True, from_=1, to=2000, increment=1)
        self._entry(stock, "Stock Z (mm)", "stock_z", "20", 1, 0, spin=True, from_=0, to=500, increment=1)
        self._hint(stock, "Stock dimensions are used for layout checks and Makera project stock metadata.", 2)

    def _build_params_tab(self):
        f = self.tab_params
        f.columnconfigure(0, weight=1)

        ranges = ttk.LabelFrame(f, text="Speed and power ranges")
        ranges.grid(row=0, column=0, sticky="we", padx=2, pady=(0, 10))
        self._entry(ranges, "Speed min (mm/min)", "speed_min", "2200", 0, 0, tooltip="Lowest generated tile speed.", spin=True, from_=1, to=50000, increment=50)
        self._entry(ranges, "Speed max (mm/min)", "speed_max", "2800", 0, 2, tooltip="Highest generated tile speed.", spin=True, from_=1, to=50000, increment=50)
        self._entry(ranges, "Power min (%)", "power_min", "20", 1, 0, tooltip="Lowest generated tile power.", spin=True, from_=0, to=100, increment=1)
        self._entry(ranges, "Power max (%)", "power_max", "40", 1, 2, tooltip="Highest generated tile power.", spin=True, from_=0, to=100, increment=1)
        self._hint(ranges, "Speed is interpolated across rows. Power is interpolated across columns.", 2)

        rounding = ttk.LabelFrame(f, text="Rounding")
        rounding.grid(row=1, column=0, sticky="we", padx=2, pady=(0, 10))
        self.vars["round_speed_values"] = tk.BooleanVar(value=True)
        self.vars["round_power_values"] = tk.BooleanVar(value=True)
        speed_round = ttk.Checkbutton(rounding, text="Round speed values and labels to integers", variable=self.vars["round_speed_values"])
        speed_round.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        power_round = ttk.Checkbutton(rounding, text="Round power values and labels to integers", variable=self.vars["round_power_values"])
        power_round.grid(row=0, column=2, columnspan=2, sticky="w", padx=6, pady=4)
        self._tooltip(speed_round, "Rounding affects generated tile values, labels, and NC metadata.")
        self._tooltip(power_round, "Rounding affects generated tile values, labels, and NC metadata.")
        self._hint(rounding, "Tip: integer rounding avoids long labels like 1942.857 and documents the generated values more clearly.", 1)

    def _build_laser_tab(self):
        f = self.tab_laser
        f.columnconfigure(0, weight=1)

        tile = ttk.LabelFrame(f, text="Tile laser pattern")
        tile.grid(row=0, column=0, sticky="we", padx=2, pady=(0, 10))
        ttk.Label(tile, text="Tile mode").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["mode"] = tk.StringVar(value="Offset Fill")
        mode_combo = ttk.Combobox(tile, textvariable=self.vars["mode"], values=list(LASER_MODES), state="readonly", width=18)
        mode_combo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        self._tooltip(mode_combo, "Line outlines tiles. Fill scans lines. Offset Fill creates inward contours.")
        self._entry(tile, "Line interval (mm)", "line_interval", "0.10", 0, 2, tooltip="Spacing between fill lines or offset contours.", spin=True, from_=0.01, to=10, increment=0.01, format_="%.2f")
        self._entry(tile, "Passes", "passes", "1", 1, 0, tooltip="Repeat each tile pattern this many times.", spin=True, from_=1, to=20, increment=1)
        self._entry(tile, "Scan angle", "scan_angle", "0", 1, 2, tooltip="Fill-line angle in degrees for Fill mode.", spin=True, from_=-180, to=180, increment=5)
        self.vars["bidirectional"] = tk.BooleanVar(value=True)
        bidirectional = ttk.Checkbutton(tile, text="Bi-directional Fill", variable=self.vars["bidirectional"])
        bidirectional.grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self._tooltip(bidirectional, "Fill mode alternates scan direction between lines.")
        self._hint(tile, "Mode hints: Line = outline, Fill = scan lines, Offset Fill = contour-like fill.", 3)

        nc = ttk.LabelFrame(f, text="Generic NC power scale")
        nc.grid(row=1, column=0, sticky="we", padx=2, pady=(0, 10))
        ttk.Label(nc, text="NC power profile").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["nc_power_profile"] = tk.StringVar(value=DEFAULT_NC_POWER_PROFILE)
        profile_combo = ttk.Combobox(nc, textvariable=self.vars["nc_power_profile"], values=list(NC_POWER_PROFILES), state="readonly", width=18)
        profile_combo.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        profile_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_nc_s_max_from_profile())
        self._tooltip(profile_combo, "Select the S-value scale your NC controller expects.")
        self._entry(nc, "NC S max", "nc_s_max", "1", 1, 0, tooltip="Maximum laser S value for generic NC output. Custom keeps manual input.", spin=True, from_=0, to=100000, increment=0.1)
        self._hint(nc, "Generic NC only: Makera uses S0.0-S1.0; GRBL often uses S0-S1000; 8-bit uses S0-S255.", 2)

    def _build_labels_tab(self):
        f = self.tab_labels
        f.columnconfigure(0, weight=1)
        labels = ttk.LabelFrame(f, text="Generated labels")
        labels.grid(row=0, column=0, sticky="we", padx=2, pady=(0, 10))
        self.vars["labels_enabled"] = tk.BooleanVar(value=True)
        enabled = ttk.Checkbutton(labels, text="Enable labels", variable=self.vars["labels_enabled"])
        enabled.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self._tooltip(enabled, "Labels are generated as simple stroke geometry.")
        ttk.Label(labels, text="Language").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.vars["language"] = tk.StringVar(value="English")
        ttk.Combobox(labels, textvariable=self.vars["language"], values=["English", "Deutsch"], state="readonly", width=12).grid(row=0, column=3, sticky="w", padx=6, pady=4)
        self._entry(labels, "Label speed", "label_speed", "2500", 1, 0, tooltip="Feed rate used for label strokes.", spin=True, from_=1, to=50000, increment=50)
        self._entry(labels, "Label power (%)", "label_power", "25", 1, 2, tooltip="Laser power used for label strokes.", spin=True, from_=0, to=100, increment=1)
        ttk.Label(labels, text="Label mode").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.vars["label_mode"] = tk.StringVar(value="Line")
        label_mode = ttk.Combobox(labels, textvariable=self.vars["label_mode"], values=list(LASER_MODES), state="readonly", width=18)
        label_mode.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        self._tooltip(label_mode, "Label strokes can use the same mode names as tile geometry.")
        self._entry(labels, "Label thickness", "label_thickness", "0.06", 2, 2, tooltip="Approximate stroke width for label geometry.", spin=True, from_=0.01, to=5, increment=0.01, format_="%.2f")
        self._hint(labels, "Labels are simple built-in stroke text. Geometry behavior is unchanged.", 3)

    def _build_preview_tab(self):
        f = self.tab_preview
        top = ttk.Frame(f)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(
            top,
            text="Preview updates automatically. Generated files must still be verified before running.",
            style="Hint.TLabel",
            wraplength=680,
        ).pack(side="left", padx=6)

        body = ttk.Frame(f)
        body.pack(fill="both", expand=True)
        self.preview_canvas = tk.Canvas(body, width=560, height=460, bg="white", highlightthickness=1, highlightbackground="#aaa")
        self.preview_canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.preview_canvas.bind("<Configure>", lambda _event: self._schedule_preview_refresh())
        self.preview_text = tk.Text(body, width=38, height=22, wrap="word")
        self.preview_text.pack(side="right", fill="y")
        self.preview_text.tag_configure("heading", font=("TkDefaultFont", 10, "bold"))
        self.preview_text.tag_configure("warning", foreground="#9a3412")
        self.preview_text.tag_configure("ok", foreground="#166534")

    def _build_side_preview(self, parent):
        frame = ttk.LabelFrame(parent, text="Quick Preview")
        frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        self.side_preview_frame = frame
        ttk.Label(
            frame,
            text="Live approximate layout. Use the Preview tab for details.",
            style="Hint.TLabel",
            wraplength=280,
        ).grid(row=0, column=0, sticky="we", padx=8, pady=(8, 4))
        self.side_preview_canvas = tk.Canvas(frame, width=300, height=360, bg="white", highlightthickness=1, highlightbackground="#aaa")
        self.side_preview_canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        self.side_preview_canvas.bind("<Configure>", lambda _event: self._schedule_preview_refresh())
        self.side_preview_note = tk.StringVar(value="Preview updates automatically as layout values change.")
        ttk.Label(frame, textvariable=self.side_preview_note, style="Hint.TLabel", wraplength=280).grid(row=2, column=0, sticky="we", padx=8, pady=4)

    def _build_presets_tab(self):
        f = self.tab_presets
        f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Preset").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["preset_name"] = tk.StringVar(value="")
        self.preset_combo = ttk.Combobox(f, textvariable=self.vars["preset_name"], values=[], width=42)
        self.preset_combo.grid(row=0, column=1, columnspan=4, sticky="we", padx=6, pady=4)
        self._tooltip(self.preset_combo, "This top field is the only editable preset name. Type a new name, then click Save preset.")

        ttk.Button(f, text="Load preset", command=self._load_selected_preset, style="Accent.TButton").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Save preset", command=self._save_named_preset, style="Accent.TButton").grid(row=1, column=1, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Delete selected", command=self._delete_selected_preset, style="Subtle.TButton").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Refresh", command=self._refresh_presets, style="Subtle.TButton").grid(row=1, column=3, padx=6, pady=6, sticky="w")

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=5, sticky="we", pady=12)
        ttk.Button(f, text="Import preset...", command=self._load_preset_file, style="Subtle.TButton").grid(row=3, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Export preset...", command=self._save_preset_file, style="Subtle.TButton").grid(row=3, column=1, padx=6, pady=6, sticky="w")

        meta = ttk.LabelFrame(f, text="Preset metadata")
        meta.grid(row=4, column=0, columnspan=5, sticky="we", padx=6, pady=(10, 6))
        metadata_labels = [
            ("Material", "material"),
            ("Machine", "machine"),
            ("Laser module", "laser_module"),
            ("Notes", "notes"),
            ("Safety note", "safety_note"),
        ]
        for row, (label, key) in enumerate(metadata_labels):
            ttk.Label(meta, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=3)
            ttk.Entry(meta, textvariable=self._var(key, ""), width=58).grid(row=row, column=1, columnspan=4, sticky="we", padx=6, pady=3)
        ref_row = len(metadata_labels)
        ttk.Label(meta, text="Reference image").grid(row=ref_row, column=0, sticky="w", padx=6, pady=3)
        ttk.Entry(meta, textvariable=self._var("reference_image", ""), width=44).grid(row=ref_row, column=1, columnspan=2, sticky="we", padx=6, pady=3)
        ttk.Button(meta, text="Browse...", command=self._browse_reference_image, style="Subtle.TButton").grid(row=ref_row, column=3, sticky="w", padx=6, pady=3)
        ttk.Button(meta, text="Clear", command=self._clear_reference_image, style="Subtle.TButton").grid(row=ref_row, column=4, sticky="w", padx=6, pady=3)
        meta.columnconfigure(1, weight=1)
        self._hint(f, "Typing a new preset name and clicking Save preset creates a new preset. Existing files ask before overwrite.", 5, column=0, columnspan=5)

    def _update_side_preview_visibility(self, _event=None):
        if not hasattr(self, "side_preview_frame") or not hasattr(self, "work_area"):
            return
        should_show = self.root.winfo_width() >= 1060 and not self._is_preview_tab_selected()
        if should_show == self._side_preview_visible:
            return
        self._side_preview_visible = should_show
        if should_show:
            self.work_area.columnconfigure(1, weight=1, minsize=290)
            self.side_preview_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            self._schedule_preview_refresh()
        else:
            self.side_preview_frame.grid_remove()
            self.work_area.columnconfigure(1, weight=0, minsize=0)

    def _is_preview_tab_selected(self) -> bool:
        if not hasattr(self, "tabs"):
            return False
        try:
            selected = self.tabs.select()
            return bool(selected) and self.tabs.nametowidget(selected) is self.tab_preview
        except Exception:
            return False

    def _on_tab_changed(self, _event=None):
        self._update_side_preview_visibility()
        self._refresh_preview(log_warning=True)

    def _browse_output(self):
        suffix = expected_output_suffix_for_format(self.vars["output_format"].get())
        path = filedialog.asksaveasfilename(
            defaultextension=suffix,
            filetypes=[("Makera Studio Project", "*.mks"), ("NC/G-code", "*.nc"), ("All files", "*.*")]
        )
        if path:
            self.vars["output"].set(path)

    def _sync_output_extension_with_format(self):
        current = self.vars["output"].get()
        synced = sync_output_suffix_for_format(current, self.vars["output_format"].get())
        if synced != current:
            self.vars["output"].set(synced)

    def _on_output_format_changed(self, _event=None):
        self._sync_output_extension_with_format()
        self._log(f"Output format set to {self.vars['output_format'].get()}. Output path suffix updated where safe.")

    def _log(self, text: str):
        tag = None
        if text.startswith("ERROR"):
            tag = "error"
        elif text.startswith("WARNING") or text.startswith("Preview warning"):
            tag = "warning"
        elif text.startswith("Created") or text.startswith("Generation complete"):
            tag = "success"
        if tag:
            self.status.insert("end", text + "\n", tag)
        else:
            self.status.insert("end", text + "\n")
        self.status.see("end")

    def _preset_dir(self) -> Path:
        return preset_dir()

    def _preset_path(self, name: str) -> Path:
        return preset_path(name)

    def _browse_reference_image(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("WEBP", "*.webp"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.vars["reference_image"].set(path)

    def _clear_reference_image(self):
        self.vars["reference_image"].set("")

    def _refresh_presets(self):
        names = [name for name, _path in list_presets(self._preset_dir())]
        self.preset_combo["values"] = names
        if names and not self.vars.get("preset_name", tk.StringVar()).get():
            self.vars["preset_name"].set(names[0])

    def _collect_preset_data(self) -> Dict[str, object]:
        data: Dict[str, object] = {}
        for key, var in self.vars.items():
            if key in ("preset_name", "ui_theme"):
                continue
            try:
                data[key] = var.get()
            except Exception:
                pass
        return data

    def _apply_preset_data(self, data: Dict[str, object]) -> None:
        for key in PRESET_METADATA_FIELDS:
            if key in self.vars:
                self.vars[key].set(data.get(key, ""))

        for key, value in data.items():
            if key.startswith("_"):
                continue
            if key == "ui_theme":
                continue
            if key in self.vars:
                try:
                    self.vars[key].set(value)
                except Exception:
                    pass
        if "nc_power_profile" not in data and "nc_s_max" in data and "nc_power_profile" in self.vars:
            self.vars["nc_power_profile"].set(profile_for_nc_s_max(data["nc_s_max"]))
        self._sync_nc_s_max_from_profile()
        self._sync_output_extension_with_format()
        self._schedule_preview_refresh()

    def _sync_nc_s_max_from_profile(self) -> None:
        if "nc_power_profile" not in self.vars or "nc_s_max" not in self.vars:
            return
        profile = self.vars["nc_power_profile"].get()
        profile_s_max = NC_POWER_PROFILES.get(profile)
        if profile_s_max is not None:
            self.vars["nc_s_max"].set(fmt_num(profile_s_max, 3))

    def _save_named_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            messagebox.showwarning("Preset name missing", "Enter a preset name first.")
            return
        data = self._collect_preset_data()
        existing = find_preset_path(name, self._preset_dir())
        if existing.exists() and not messagebox.askyesno(
            "Overwrite preset?",
            f"Preset '{name}' already exists.\n\nOverwrite it?",
        ):
            self._log("Preset save canceled.")
            return
        path = write_preset_file(existing, data, name) if existing.exists() else save_preset_data(name, data, self._preset_dir())
        self._log("Preset saved: " + str(path))
        self._refresh_presets()

    def _load_selected_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            return
        path = find_preset_path(name, self._preset_dir())
        if not path.exists():
            messagebox.showerror("Error", "Preset not found.")
            return
        data = read_preset_file(path)
        self._apply_preset_data(data)
        self._refresh_preview(log_warning=True)
        self._log("Preset loaded: " + str(path))

    def _delete_selected_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            return
        path = find_preset_path(name, self._preset_dir())
        if path.exists():
            path.unlink()
            self._log("Preset deleted: " + str(path))
        self.vars["preset_name"].set("")
        self._refresh_presets()

    def _save_preset_file(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            messagebox.showwarning("Preset missing", "Select a preset to export first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{name}.json",
            filetypes=[("Preset JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        exported = export_preset_file(name, Path(path), self._preset_dir())
        self._log("Preset exported: " + str(exported))

    def _load_preset_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Preset JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            imported = import_preset_file(Path(path), self._preset_dir(), overwrite=False)
        except FileExistsError:
            data = read_preset_file(Path(path))
            name = str(data.get("name") or data.get("_preset_name") or Path(path).stem)
            if not messagebox.askyesno(
                "Overwrite preset?",
                f"Preset '{name}' already exists.\n\nOverwrite it?",
            ):
                self._log("Preset import canceled.")
                return
            imported = import_preset_file(Path(path), self._preset_dir(), overwrite=True)
        data = read_preset_file(imported)
        self.vars["preset_name"].set(str(data.get("name") or data.get("_preset_name") or imported.stem))
        self._apply_preset_data(data)
        self._refresh_presets()
        self._refresh_preview(log_warning=True)
        self._log("Preset imported: " + str(imported))

    def _bind_auto_preview_updates(self):
        keys = (
            "rows",
            "cols",
            "tile_size",
            "gap",
            "stock_x",
            "stock_y",
            "auto_position",
            "grid_x",
            "grid_y",
            "speed_min",
            "speed_max",
            "power_min",
            "power_max",
            "round_speed_values",
            "round_power_values",
            "labels_enabled",
        )
        for key in keys:
            if key in self.vars:
                self.vars[key].trace_add("write", lambda *_args: self._schedule_preview_refresh())

    def _preview_snapshot(self):
        settings = self._settings()
        layout_settings = copy.deepcopy(settings)
        layout = computed_layout(layout_settings)
        warnings = validate_layout(settings)
        rows = int(settings.rows)
        cols = int(settings.cols)
        speeds_raw = linspace(settings.speed_min, settings.speed_max, rows)
        powers_raw = linspace(settings.power_min, settings.power_max, cols)
        speeds = [int(round(v)) for v in speeds_raw] if settings.round_speed_values else [round(v, 6) for v in speeds_raw]
        powers = [int(round(v)) for v in powers_raw] if settings.round_power_values else [round(v, 6) for v in powers_raw]
        return settings, layout, warnings, speeds, powers

    def _draw_layout_preview(self, canvas, settings: GeneratorSettings, layout: Dict[str, float], warnings, compact: bool = False):
        canvas.delete("all")
        p = self.palette
        canvas.configure(bg=p["preview_bg"], highlightbackground=p["border"])
        cw = max(int(canvas.winfo_width() or (300 if compact else 560)), 120)
        ch = max(int(canvas.winfo_height() or (360 if compact else 460)), 120)
        pad = 22 if compact else 34
        sx = max(float(layout["stock_x"]), 1.0)
        sy = max(float(layout["stock_y"]), 1.0)
        scale = min((cw - 2 * pad) / sx, (ch - 2 * pad) / sy)
        scale = max(scale, 0.1)

        def px(x):
            return pad + x * scale

        def py(y):
            return ch - pad - y * scale

        gx = layout["grid_x"]
        gy = layout["grid_y"]
        grid_w = layout["grid_w"]
        grid_h = layout["grid_h"]
        tile = settings.tile_size
        gap = settings.gap
        rows = int(settings.rows)
        cols = int(settings.cols)

        canvas.create_rectangle(px(0), py(sy), px(sx), py(0), outline=p["preview_stock"], width=2)
        canvas.create_text(px(sx / 2), py(sy) - 12, text=f"Stock {sx:g} x {sy:g} mm", fill=p["preview_text"])
        canvas.create_rectangle(
            px(layout["layout_min_x"]),
            py(layout["layout_max_y"]),
            px(layout["layout_max_x"]),
            py(layout["layout_min_y"]),
            outline=p["preview_bounds"],
            dash=(4, 2),
        )
        if settings.labels_enabled:
            canvas.create_rectangle(px(gx), py(gy + grid_h + 12), px(gx + grid_w), py(gy + grid_h), outline=p["preview_label_zone"], dash=(3, 2))
            canvas.create_rectangle(px(gx - 16), py(gy + grid_h), px(gx), py(gy), outline=p["preview_label_zone"], dash=(3, 2))
            if not compact:
                canvas.create_text(px(gx + grid_w / 2), py(gy + grid_h + 8), text="POWER (%)", fill=p["preview_text"])
                canvas.create_text(px(max(2.5, gx - 13)), py(gy + grid_h / 2), text="SPEED", fill=p["preview_text"], angle=90)

        for r in range(rows):
            for col in range(cols):
                x = gx + col * (tile + gap)
                y = gy + r * (tile + gap)
                canvas.create_rectangle(px(x), py(y + tile), px(x + tile), py(y), outline=p["preview_grid"], fill=p["preview_tile_fill"], width=1)

        canvas.create_rectangle(px(gx), py(gy + grid_h), px(gx + grid_w), py(gy), outline=p["preview_grid"], width=2)
        if warnings:
            canvas.create_text(cw - pad, ch - 10, text=f"{len(warnings)} warning(s)", fill=p["warning"], anchor="e")
        elif compact:
            canvas.create_text(cw - pad, ch - 10, text=f"{rows} x {cols}", fill=p["success"], anchor="e")

    def _write_preview_summary(self, settings: GeneratorSettings, layout: Dict[str, float], warnings, speeds, powers):
        if not hasattr(self, "preview_text"):
            return
        rows = int(settings.rows)
        cols = int(settings.cols)
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("end", "Layout summary\n", "heading")
        self.preview_text.insert("end", "--------------\n")
        self.preview_text.insert("end", f"Grid: {rows} x {cols}\n")
        self.preview_text.insert("end", f"Tiles: {rows * cols}\n")
        self.preview_text.insert("end", f"Grid size: {layout['grid_w']:.1f} x {layout['grid_h']:.1f} mm\n")
        self.preview_text.insert("end", f"Grid origin: X{layout['grid_x']:.1f} Y{layout['grid_y']:.1f}\n")
        self.preview_text.insert(
            "end",
            f"Approx bounds: X{layout['layout_min_x']:.1f}..{layout['layout_max_x']:.1f}, "
            f"Y{layout['layout_min_y']:.1f}..{layout['layout_max_y']:.1f}\n\n",
        )
        self.preview_text.insert("end", "Speed top -> bottom:\n", "heading")
        self.preview_text.insert("end", ", ".join(str(v) for v in reversed(speeds)) + "\n\n")
        self.preview_text.insert("end", "Power left -> right:\n", "heading")
        self.preview_text.insert("end", ", ".join(str(v) for v in powers) + "\n\n")
        if warnings:
            self.preview_text.insert("end", "Warnings:\n", "warning")
            for w in warnings:
                self.preview_text.insert("end", "- " + w + "\n", "warning")
        else:
            self.preview_text.insert("end", "No layout warnings.\n", "ok")

    def _refresh_preview(self, log_success: bool = False, show_error: bool = False, log_warning: bool = False) -> bool:
        try:
            settings, layout, warnings, speeds, powers = self._preview_snapshot()
            if hasattr(self, "preview_canvas"):
                self._draw_layout_preview(self.preview_canvas, settings, layout, warnings, compact=False)
            if hasattr(self, "side_preview_canvas") and self._side_preview_visible:
                self._draw_layout_preview(self.side_preview_canvas, settings, layout, warnings, compact=True)
            self._write_preview_summary(settings, layout, warnings, speeds, powers)
            if hasattr(self, "side_preview_note"):
                note = f"{int(settings.rows)} x {int(settings.cols)} grid"
                if warnings:
                    note += f" - {len(warnings)} layout warning(s)"
                else:
                    note += " - layout looks inside stock"
                self.side_preview_note.set(note)
            if log_success:
                self._log("Preview updated.")
            return True
        except Exception as e:
            if hasattr(self, "side_preview_note"):
                self.side_preview_note.set("Preview waiting for valid numeric values.")
            if log_warning:
                self._log("Preview warning: " + str(e))
            if show_error:
                self._log("ERROR: " + str(e))
                messagebox.showerror("Error", str(e))
            return False

    def _schedule_preview_refresh(self):
        if self._preview_after_id:
            self.root.after_cancel(self._preview_after_id)
        self._preview_after_id = self.root.after(250, self._run_scheduled_preview_refresh)

    def _run_scheduled_preview_refresh(self):
        self._preview_after_id = None
        self._refresh_preview()

    def _settings(self) -> GeneratorSettings:
        def f(name): return float(self.vars[name].get())
        def i(name): return int(float(self.vars[name].get()))
        return GeneratorSettings(
            output_path=Path(self.vars["output"].get()),
            output_format=self.vars["output_format"].get(),
            overwrite_existing=bool(self.vars["overwrite_existing"].get()),
            auto_filename=bool(self.vars["auto_filename"].get()),
            material_name=self.vars["material_name"].get(),
            rows=i("rows"),
            cols=i("cols"),
            speed_min=f("speed_min"),
            speed_max=f("speed_max"),
            power_min=f("power_min"),
            power_max=f("power_max"),
            tile_size=f("tile_size"),
            gap=f("gap"),
            grid_x=f("grid_x"),
            grid_y=f("grid_y"),
            auto_position=bool(self.vars["auto_position"].get()),
            tile_mode_name=self.vars["mode"].get(),
            line_interval=f("line_interval"),
            passes=i("passes"),
            bidirectional=bool(self.vars["bidirectional"].get()),
            scan_angle=f("scan_angle"),
            labels_enabled=bool(self.vars["labels_enabled"].get()),
            language=self.vars["language"].get(),
            label_speed=f("label_speed"),
            label_power=f("label_power"),
            label_mode_name=self.vars["label_mode"].get(),
            label_thickness=f("label_thickness"),
            stock_x=f("stock_x"),
            stock_y=f("stock_y"),
            stock_z=f("stock_z"),
            round_speed_values=bool(self.vars["round_speed_values"].get()),
            round_power_values=bool(self.vars["round_power_values"].get()),
            nc_power_profile=self.vars["nc_power_profile"].get(),
            nc_s_max=f("nc_s_max"),
        )

    def _display_value(self, value) -> str:
        try:
            f = float(value)
            return str(int(f)) if f.is_integer() else f"{f:g}"
        except Exception:
            return str(value)

    def _next_steps_message(self, output_format: str) -> str:
        if output_format == "MKS":
            return "Next: open the .mks in Makera Studio, click Recalculate, then inspect Preview."
        if output_format == "NC":
            return "Next: verify the controller S-value scale and preview the .nc in your sender/viewer."
        return (
            "Next: open the .mks in Makera Studio, click Recalculate, then inspect Preview.\n"
            "Also verify the controller S-value scale and preview the .nc in your sender/viewer."
        )

    def _generate(self):
        try:
            settings = self._settings()
            pre_warnings = validate_layout(settings)
            for warning in pre_warnings:
                self._log("WARNING: " + warning)
            infos = []
            if settings.output_format in ("MKS", "Both"):
                infos.append(generate_mks(copy.deepcopy(settings)))
            if settings.output_format in ("NC", "Both"):
                infos.append(generate_generic_nc(copy.deepcopy(settings)))

            for info in infos:
                self._log("Created: " + info["output"])
                if info.get("format") == "NC":
                    self._log(f"NC lines: {info['lines']} | Tiles: {info['tiles']} | Profile: {info['power_profile']} | S max: {info['s_max']}")
                else:
                    self._log(f"Paths: {info['paths']} | Shapes: {info['shapes']} | Labels: {info['label_shapes']} | Tiles: {info['tile_shapes']}")
                self._log("Speed top -> bottom: " + ", ".join(self._display_value(x) for x in info["speeds_visual_top_to_bottom"]))
                self._log("Power left -> right: " + ", ".join(self._display_value(x) for x in info["powers_left_to_right"]))
                for warning in info.get("warnings", []):
                    self._log("WARNING: " + warning)

            self._refresh_preview(log_warning=True)
            next_steps = self._next_steps_message(settings.output_format)
            for line in next_steps.splitlines():
                self._log(line)
            self._log("Generation complete. Preview and verify before running the laser.")
            messagebox.showinfo("Done", "File(s) created.\n\n" + next_steps)
        except Exception as e:
            self._log("ERROR: " + str(e))
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()
