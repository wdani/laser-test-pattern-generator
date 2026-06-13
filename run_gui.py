#!/usr/bin/env python3
"""GUI-only launcher for Python and PyInstaller app builds."""

import os
import platform
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

from laser_test_pattern_generator.paths import prepare_app_launch_environment, startup_log_path
from laser_test_pattern_generator.gui import GeneratorGui


def write_startup_diagnostics(exc: BaseException, package_root: Path | None = None) -> Path:
    log_candidates = [
        startup_log_path(package_root=package_root),
        (package_root or Path.cwd()) / "logs" / "startup.log",
        Path(tempfile.gettempdir()) / "laser_test_pattern_generator_startup.log",
    ]
    details = [
        "=" * 72,
        f"timestamp_utc: {datetime.now(timezone.utc).isoformat()}",
        f"platform: {platform.platform()}",
        f"machine: {platform.machine()}",
        f"python: {sys.version.replace(os.linesep, ' ')}",
        f"sys.executable: {sys.executable}",
        f"sys.argv: {sys.argv!r}",
        f"sys.frozen: {getattr(sys, 'frozen', False)!r}",
        f"sys._MEIPASS: {getattr(sys, '_MEIPASS', '')!r}",
        f"cwd: {os.getcwd()}",
        f"package_root: {str(package_root) if package_root is not None else ''}",
        f"env_HOME: {os.environ.get('HOME', '')}",
        f"env_TMPDIR: {os.environ.get('TMPDIR', '')}",
        f"env_PATH: {os.environ.get('PATH', '')}",
        "traceback:",
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).rstrip(),
        "",
    ]
    last_error: Exception | None = None
    for log_path in log_candidates:
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write("\n".join(details))
            return log_path
        except Exception as log_error:
            last_error = log_error

    if last_error is not None:
        raise last_error
    raise RuntimeError("Could not write startup diagnostics")


def show_startup_error(log_path: Path) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Laser Test Pattern Generator",
            "The app could not start.\n\n"
            f"Startup diagnostics were written to:\n{log_path}",
        )
        root.destroy()
    except Exception:
        pass


def main() -> int:
    package_root: Path | None = None
    try:
        package_root = prepare_app_launch_environment()
        gui = GeneratorGui()
        gui.run()
        return 0
    except Exception as exc:
        if getattr(sys, "frozen", False):
            log_path = write_startup_diagnostics(exc, package_root)
            show_startup_error(log_path)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())
