from __future__ import annotations

import copy
from pathlib import Path
from typing import Dict

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, simpledialog
except Exception:
    tk = None
    ttk = None
    filedialog = None
    messagebox = None
    simpledialog = None

from .font import text_segments
from .generator_mks import generate_mks
from .generator_nc import fmt_num, generate_generic_nc, profile_for_nc_s_max
from .geometry import computed_layout, linspace, validate_layout
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


class GeneratorGui:
    def __init__(self) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available")

        self.root = tk.Tk()
        self.root.title(f"Makera Material Test Generator {APP_VERSION}")
        self.root.geometry("900x720")
        self.vars: Dict[str, tk.Variable] = {}
        self.preset_names_var = tk.StringVar(value="")
        self._build()
        self._refresh_presets()

    def _var(self, name: str, default, cls=tk.StringVar):
        v = cls(value=default)
        self.vars[name] = v
        return v

    def _entry(self, parent, label: str, varname: str, default, row: int, col: int = 0, width: int = 12):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=6, pady=4)
        ent = ttk.Entry(parent, textvariable=self._var(varname, default), width=width)
        ent.grid(row=row, column=col+1, sticky="w", padx=6, pady=4)
        return ent

    def _build(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        output = ttk.LabelFrame(main, text="Output")
        output.pack(fill="x", pady=(0, 8))

        self._var("output", str(Path.cwd() / "makera_material_test_generated.mks"))
        ttk.Entry(output, textvariable=self.vars["output"], width=78).grid(row=0, column=0, columnspan=5, padx=6, pady=6, sticky="we")
        ttk.Button(output, text="Browse", command=self._browse_output).grid(row=0, column=5, padx=6, pady=6)

        self.vars["output_format"] = tk.StringVar(value="MKS")
        ttk.Label(output, text="Format").grid(row=1, column=0, sticky="w", padx=6, pady=3)
        ttk.Combobox(output, textvariable=self.vars["output_format"], values=["MKS", "NC", "Both"], state="readonly", width=10).grid(row=1, column=1, sticky="w", padx=6, pady=3)

        self.vars["overwrite_existing"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(output, text="Overwrite existing file", variable=self.vars["overwrite_existing"]).grid(row=1, column=2, sticky="w", padx=6, pady=3)

        self.vars["auto_filename"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(output, text="Auto filename", variable=self.vars["auto_filename"]).grid(row=1, column=3, sticky="w", padx=6, pady=3)
        ttk.Label(output, text="Material").grid(row=1, column=4, sticky="e", padx=6, pady=3)
        ttk.Entry(output, textvariable=self._var("material_name", "material"), width=16).grid(row=1, column=5, sticky="w", padx=6, pady=3)
        output.columnconfigure(0, weight=1)

        tabs = ttk.Notebook(main)
        tabs.pack(fill="both", expand=True)

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

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Generate", command=self._generate).pack(side="left", padx=6)
        ttk.Button(buttons, text="Close", command=self.root.destroy).pack(side="left", padx=6)

        self.status = tk.Text(main, height=9)
        self.status.pack(fill="both", expand=False)
        self._log("Ready. Generate files, then verify them in Makera Studio or your NC viewer/sender.")

    def _build_grid_tab(self):
        f = self.tab_grid
        self._entry(f, "Rows", "rows", "6", 0, 0)
        self._entry(f, "Columns", "cols", "6", 0, 2)
        self._entry(f, "Tile size (mm)", "tile_size", "8.0", 1, 0)
        self._entry(f, "Gap (mm)", "gap", "2.0", 1, 2)

        self.vars["auto_position"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Auto position inside stock", variable=self.vars["auto_position"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self._entry(f, "Grid X manual", "grid_x", "18.0", 3, 0)
        self._entry(f, "Grid Y manual", "grid_y", "8.0", 3, 2)

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=4, column=0, columnspan=4, sticky="we", pady=12)

        self._entry(f, "Stock X (mm)", "stock_x", "100", 5, 0)
        self._entry(f, "Stock Y (mm)", "stock_y", "100", 5, 2)
        self._entry(f, "Stock Z (mm)", "stock_z", "20", 6, 0)

        note = ttk.Label(f, text="Auto position keeps room for labels and centers the whole test layout inside the stock.", foreground="#555")
        note.grid(row=7, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_params_tab(self):
        f = self.tab_params
        self._entry(f, "Speed min (mm/min)", "speed_min", "2200", 0, 0)
        self._entry(f, "Speed max (mm/min)", "speed_max", "2800", 0, 2)
        self._entry(f, "Power min (%)", "power_min", "20", 1, 0)
        self._entry(f, "Power max (%)", "power_max", "40", 1, 2)

        self.vars["round_speed_values"] = tk.BooleanVar(value=True)
        self.vars["round_power_values"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Round speed labels/values to integers", variable=self.vars["round_speed_values"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(f, text="Round power labels/values to integers", variable=self.vars["round_power_values"]).grid(row=2, column=2, columnspan=2, sticky="w", padx=6, pady=4)

        note = ttk.Label(f, text="Tip: integer rounding avoids long labels like 1942.857.", foreground="#555")
        note.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_laser_tab(self):
        f = self.tab_laser
        ttk.Label(f, text="Tile mode").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["mode"] = tk.StringVar(value="Offset Fill")
        ttk.Combobox(f, textvariable=self.vars["mode"], values=list(LASER_MODES), state="readonly", width=18).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        self._entry(f, "Line interval (mm)", "line_interval", "0.10", 0, 2)
        self._entry(f, "Passes", "passes", "1", 1, 0)
        self._entry(f, "Scan angle", "scan_angle", "0", 1, 2)

        self.vars["bidirectional"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Bi-directional Fill", variable=self.vars["bidirectional"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=4, sticky="we", pady=12)

        ttk.Label(f, text="NC power profile").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.vars["nc_power_profile"] = tk.StringVar(value=DEFAULT_NC_POWER_PROFILE)
        profile_combo = ttk.Combobox(f, textvariable=self.vars["nc_power_profile"], values=list(NC_POWER_PROFILES), state="readonly", width=18)
        profile_combo.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        profile_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_nc_s_max_from_profile())

        self._entry(f, "NC S max", "nc_s_max", "1", 5, 0)
        note = ttk.Label(f, text="Generic NC only: Makera uses S0.0-S1.0; GRBL often uses S0-S1000; 8-bit uses S0-S255.", foreground="#555")
        note.grid(row=6, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_labels_tab(self):
        f = self.tab_labels
        self.vars["labels_enabled"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Enable labels", variable=self.vars["labels_enabled"]).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Language").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.vars["language"] = tk.StringVar(value="English")
        ttk.Combobox(f, textvariable=self.vars["language"], values=["English", "Deutsch"], state="readonly", width=12).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        self._entry(f, "Label speed", "label_speed", "2500", 1, 0)
        self._entry(f, "Label power (%)", "label_power", "25", 1, 2)

        ttk.Label(f, text="Label mode").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.vars["label_mode"] = tk.StringVar(value="Line")
        ttk.Combobox(f, textvariable=self.vars["label_mode"], values=list(LASER_MODES), state="readonly", width=18).grid(row=2, column=1, sticky="w", padx=6, pady=4)
        self._entry(f, "Label thickness", "label_thickness", "0.06", 2, 2)


    def _build_preview_tab(self):
        f = self.tab_preview

        top = ttk.Frame(f)
        top.pack(fill="x", pady=(0, 8))
        ttk.Button(top, text="Update Preview", command=self._update_preview).pack(side="left", padx=6)
        ttk.Label(top, text="Approximate 2D layout preview. The real laser paths are calculated by Makera Studio / your controller.", foreground="#555").pack(side="left", padx=12)

        body = ttk.Frame(f)
        body.pack(fill="both", expand=True)

        self.preview_canvas = tk.Canvas(body, width=560, height=460, bg="white", highlightthickness=1, highlightbackground="#aaa")
        self.preview_canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.preview_text = tk.Text(body, width=36, height=22)
        self.preview_text.pack(side="right", fill="y")

    def _update_preview(self):
        try:
            import copy as _copy
            settings = self._settings()
            layout_settings = _copy.deepcopy(settings)
            layout = computed_layout(layout_settings)
            warnings = validate_layout(settings)

            c = self.preview_canvas
            c.delete("all")
            cw = int(c.winfo_width() or 560)
            ch = int(c.winfo_height() or 460)
            pad = 30

            sx = layout["stock_x"]
            sy = layout["stock_y"]
            scale = min((cw - 2 * pad) / max(sx, 1), (ch - 2 * pad) / max(sy, 1))

            def px(x):
                return pad + x * scale

            def py(y):
                # Display Y upwards
                return ch - pad - y * scale

            # Stock outline
            c.create_rectangle(px(0), py(sy), px(sx), py(0), outline="#222", width=2)
            c.create_text(px(sx/2), py(sy) - 12, text=f"Stock {sx:g} × {sy:g} mm", fill="#222")

            gx = layout["grid_x"]
            gy = layout["grid_y"]
            tile = settings.tile_size
            gap = settings.gap
            rows = int(settings.rows)
            cols = int(settings.cols)

            # Approx label zones
            if settings.labels_enabled:
                c.create_text(px(gx + layout["grid_w"]/2), py(gy + layout["grid_h"] + 9.5), text="POWER (%)", fill="#555")
                c.create_text(px(max(2.5, gx - 16.5)), py(gy + layout["grid_h"]/2), text="SPEED", fill="#555", angle=90)

            # Tiles
            for r in range(rows):
                for col in range(cols):
                    x = gx + col * (tile + gap)
                    y = gy + r * (tile + gap)
                    c.create_rectangle(px(x), py(y + tile), px(x + tile), py(y), outline="#1f77b4", width=1)

            # Overall approx layout bounds
            c.create_rectangle(px(layout["layout_min_x"]), py(layout["layout_max_y"]), px(layout["layout_max_x"]), py(layout["layout_min_y"]), outline="#cc7a00", dash=(4, 2))

            # Value summary
            speeds_raw = linspace(settings.speed_min, settings.speed_max, rows)
            powers_raw = linspace(settings.power_min, settings.power_max, cols)
            speeds = [int(round(v)) for v in speeds_raw] if settings.round_speed_values else [round(v, 6) for v in speeds_raw]
            powers = [int(round(v)) for v in powers_raw] if settings.round_power_values else [round(v, 6) for v in powers_raw]

            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("end", "Layout summary\n")
            self.preview_text.insert("end", "--------------\n")
            self.preview_text.insert("end", f"Grid: {rows} × {cols}\n")
            self.preview_text.insert("end", f"Tiles: {rows * cols}\n")
            self.preview_text.insert("end", f"Grid size: {layout['grid_w']:.1f} × {layout['grid_h']:.1f} mm\n")
            self.preview_text.insert("end", f"Grid origin: X{layout['grid_x']:.1f} Y{layout['grid_y']:.1f}\n")
            self.preview_text.insert("end", f"Approx bounds: X{layout['layout_min_x']:.1f}..{layout['layout_max_x']:.1f}, Y{layout['layout_min_y']:.1f}..{layout['layout_max_y']:.1f}\n\n")
            self.preview_text.insert("end", "Speed top → bottom:\n")
            self.preview_text.insert("end", ", ".join(str(v) for v in reversed(speeds)) + "\n\n")
            self.preview_text.insert("end", "Power left → right:\n")
            self.preview_text.insert("end", ", ".join(str(v) for v in powers) + "\n\n")

            if warnings:
                self.preview_text.insert("end", "Warnings:\n")
                for w in warnings:
                    self.preview_text.insert("end", "- " + w + "\n")
            else:
                self.preview_text.insert("end", "No layout warnings.\n")

            self._log("Preview updated.")
        except Exception as e:
            self._log("ERROR: " + str(e))
            messagebox.showerror("Error", str(e))



    def _build_presets_tab(self):
        f = self.tab_presets

        ttk.Label(f, text="Preset").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["preset_name"] = tk.StringVar(value="")
        self.preset_combo = ttk.Combobox(f, textvariable=self.vars["preset_name"], values=[], width=42)
        self.preset_combo.grid(row=0, column=1, columnspan=4, sticky="we", padx=6, pady=4)

        ttk.Button(f, text="Load selected", command=self._load_selected_preset).grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Save selected", command=self._save_named_preset).grid(row=1, column=1, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Save preset as...", command=self._save_preset_as).grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Delete selected", command=self._delete_selected_preset).grid(row=1, column=3, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Refresh", command=self._refresh_presets).grid(row=1, column=4, padx=6, pady=6, sticky="w")

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=5, sticky="we", pady=12)

        ttk.Button(f, text="Import preset...", command=self._load_preset_file).grid(row=3, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Export preset...", command=self._save_preset_file).grid(row=3, column=1, padx=6, pady=6, sticky="w")

        meta = ttk.LabelFrame(f, text="Preset metadata")
        meta.grid(row=4, column=0, columnspan=5, sticky="we", padx=6, pady=(10, 6))
        metadata_labels = [
            ("Name", "name"),
            ("Material", "material"),
            ("Machine", "machine"),
            ("Laser module", "laser_module"),
            ("Notes", "notes"),
            ("Safety note", "safety_note"),
        ]
        for row, (label, key) in enumerate(metadata_labels):
            ttk.Label(meta, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=3)
            ttk.Entry(meta, textvariable=self._var(key, ""), width=58).grid(row=row, column=1, columnspan=4, sticky="we", padx=6, pady=3)
        meta.columnconfigure(1, weight=1)

        note = ttk.Label(f, text="Presets are starting points. Verify values and material safety on your own machine.", foreground="#555")
        note.grid(row=5, column=0, columnspan=5, sticky="w", padx=6, pady=10)
        f.columnconfigure(1, weight=1)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mks",
            filetypes=[("Makera Studio Project", "*.mks"), ("NC/G-code", "*.nc"), ("All files", "*.*")]
        )
        if path:
            self.vars["output"].set(path)

    def _log(self, text: str):
        self.status.insert("end", text + "\n")
        self.status.see("end")

    def _preset_dir(self) -> Path:
        return preset_dir()

    def _preset_path(self, name: str) -> Path:
        return preset_path(name)

    def _refresh_presets(self):
        names = [name for name, _path in list_presets(self._preset_dir())]
        self.preset_combo["values"] = names
        if names and not self.vars.get("preset_name", tk.StringVar()).get():
            self.vars["preset_name"].set(names[0])

    def _collect_preset_data(self) -> Dict[str, object]:
        data: Dict[str, object] = {}
        for key, var in self.vars.items():
            if key == "preset_name":
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
        if "name" in self.vars and not self.vars["name"].get():
            self.vars["name"].set(str(data.get("_preset_name") or self.vars["preset_name"].get() or ""))

        for key, value in data.items():
            if key.startswith("_"):
                continue
            if key in self.vars:
                try:
                    self.vars[key].set(value)
                except Exception:
                    pass
        if "nc_power_profile" not in data and "nc_s_max" in data and "nc_power_profile" in self.vars:
            self.vars["nc_power_profile"].set(profile_for_nc_s_max(data["nc_s_max"]))
        self._sync_nc_s_max_from_profile()

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
        path = write_preset_file(existing, data, name) if existing.exists() else save_preset_data(name, data, self._preset_dir())
        self._log("Preset saved: " + str(path))
        self._refresh_presets()

    def _save_preset_as(self):
        current = self.vars["preset_name"].get().strip()
        name = simpledialog.askstring("Save preset as", "New preset name:", initialvalue=current)
        if not name:
            return
        name = name.strip()
        self.vars["preset_name"].set(name)
        if "name" in self.vars:
            self.vars["name"].set(name)
        self._save_named_preset()

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
        imported = import_preset_file(Path(path), self._preset_dir())
        data = read_preset_file(imported)
        self.vars["preset_name"].set(str(data.get("name") or data.get("_preset_name") or imported.stem))
        self._apply_preset_data(data)
        self._refresh_presets()
        self._log("Preset imported: " + str(imported))

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
                self._log("Speed top→bottom: " + ", ".join(str(int(x) if isinstance(x, int) or float(x).is_integer() else x) for x in info["speeds_visual_top_to_bottom"]))
                self._log("Power left→right: " + ", ".join(str(int(x) if isinstance(x, int) or float(x).is_integer() else x) for x in info["powers_left_to_right"]))
                for warning in info.get("warnings", []):
                    self._log("WARNING: " + warning)

            messagebox.showinfo("Done", "File(s) created.\n\nFor MKS: open in Makera Studio → Recalculate → inspect Preview.\nFor NC: verify S-value scale and preview before use.")
        except Exception as e:
            self._log("ERROR: " + str(e))
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()

