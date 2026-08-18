#!/usr/bin/env python3
"""Server Launcher — premium Python port of ServerLauncherTR."""

from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from PIL import Image, ImageSequence, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_PROJECTS_ROOT = os.environ.get("SERVER_LAUNCHER_ROOT", r"Z:\Projects")
WINDOW_TITLE = "Server Launcher"
MAX_RECENTS = 8
LOGO_FPS = 12

BG = "#070707"
PANEL = "#121212"
PANEL_ALT = "#181818"
COPPER = "#D4783A"
COPPER_HI = "#E8A05A"
STEEL = "#C5C5C5"
TEXT = "#F4F1EC"
MUTED = "#8E8A84"
LINE = "#2A2622"
DANGER = "#C45C4A"


def app_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def asset_path(name: str) -> Path:
    return app_dir() / "assets" / name


def recents_file() -> Path:
    return _config_dir() / "recents.json"


def settings_file() -> Path:
    return _config_dir() / "settings.json"


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home())) / "ServerLauncherPR"
    else:
        base = Path.home() / ".server_launcher_pr"
    base.mkdir(parents=True, exist_ok=True)
    return base


def load_settings() -> dict:
    path = settings_file()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(data: dict) -> None:
    current = load_settings()
    current.update(data)
    settings_file().write_text(json.dumps(current, indent=2), encoding="utf-8")


def _dir_accessible(path: str) -> bool:
    if not path:
        return False
    try:
        os.listdir(path)
        return True
    except OSError:
        pass
    if sys.platform == "win32":
        import ctypes

        invalid = 0xFFFFFFFF
        directory = 0x10
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs != invalid and attrs & directory:
            return True
    return False


def _wake_drive(path: str) -> None:
    drive = os.path.splitdrive(path)[0]
    if not drive:
        return
    try:
        os.listdir(drive + os.sep)
    except OSError:
        pass


def win32_logical_drives() -> list[str]:
    if sys.platform != "win32":
        return []
    import ctypes

    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    drives = []
    for index in range(26):
        if bitmask & (1 << index):
            drives.append(f"{chr(ord('A') + index)}:\\")
    return drives


def win32_unc_for(drive: str) -> str | None:
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    local = drive[:2]
    buffer = ctypes.create_unicode_buffer(1024)
    length = wintypes.DWORD(1024)
    error = ctypes.windll.mpr.WNetGetConnectionW(local, buffer, ctypes.byref(length))
    if error == 0 and buffer.value:
        return buffer.value
    return None


def win32_net_use_remote(drive: str) -> str | None:
    if sys.platform != "win32":
        return None
    try:
        completed = subprocess.run(
            ["net", "use", drive[:2]],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    for line in (completed.stdout or "").splitlines():
        for part in line.split():
            if part.startswith("\\\\"):
                return part.rstrip("\\")
    return None


def _candidate_project_roots() -> list[str]:
    candidates: list[str] = []
    saved = load_settings().get("projects_root")
    if saved:
        candidates.append(saved)
    env = os.environ.get("SERVER_LAUNCHER_ROOT")
    if env:
        candidates.append(env)
    candidates.extend(
        [
            r"Z:\Projects",
            r"Z:\Projects\\",
            "Z:/Projects",
        ]
    )
    if sys.platform == "win32":
        _wake_drive("Z:\\")
        unc = win32_unc_for("Z:")
        if unc:
            candidates.append(os.path.join(unc, "Projects"))
            candidates.append(unc)
        mapped = win32_net_use_remote("Z:")
        if mapped:
            candidates.append(os.path.join(mapped, "Projects"))
            candidates.append(mapped)
        for drive in win32_logical_drives():
            candidates.append(os.path.join(drive, "Projects"))
    unique: list[str] = []
    seen: set[str] = set()
    for path in candidates:
        key = os.path.normcase(os.path.normpath(path))
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


_projects_root_cache: str | None = None


def get_projects_root(refresh: bool = False) -> tuple[str | None, str | None]:
    global _projects_root_cache
    if not refresh and _projects_root_cache and _dir_accessible(_projects_root_cache):
        return _projects_root_cache, None
    for path in _candidate_project_roots():
        _wake_drive(path)
        if _dir_accessible(path):
            _projects_root_cache = path
            return path, None
    _projects_root_cache = None
    return None, r"Z:\Projects not found — click ... and select the Projects folder"


def set_projects_root(path: str) -> bool:
    global _projects_root_cache
    if not _dir_accessible(path):
        return False
    _projects_root_cache = path
    save_settings({"projects_root": path})
    return True


def normalize_query(text: str) -> str:
    query = text.strip()
    if query.upper().startswith("PR#"):
        query = query[3:]
    return query.strip()


def list_project_names(query: str) -> tuple[list[str], str | None]:
    query = normalize_query(query)
    if len(query) < 1:
        return [], None
    root, error = get_projects_root()
    if not root:
        return [], error
    prefix = f"PR#{query}".upper()
    names: list[str] = []
    try:
        for name in os.listdir(root):
            if name.upper().startswith(prefix):
                names.append(name[3:] if name.upper().startswith("PR#") else name)
    except OSError as exc:
        return [], str(exc)
    names.sort(key=str.upper)
    return names, None


def ui_font(size: int, weight: str = "normal") -> tuple:
    family = "Segoe UI" if sys.platform == "win32" else "Helvetica Neue"
    return (family, size, weight) if weight != "normal" else (family, size)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(rgb[0]))),
        max(0, min(255, int(rgb[1]))),
        max(0, min(255, int(rgb[2]))),
    )


def mix_hex(c1: str, c2: str, t: float) -> str:
    a = hex_to_rgb(c1)
    b = hex_to_rgb(c2)
    return rgb_to_hex((lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)))


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def open_path(path: str) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    command = ["open", path] if sys.platform == "darwin" else ["xdg-open", path]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise OSError(completed.stderr.strip() or f"Could not open {path}")


def show_error(action: str, exc: BaseException) -> None:
    messagebox.showerror(WINDOW_TITLE, f"Could not open {action}:\n{exc}")


def win32_hwnd(widget: tk.Misc) -> int:
    if sys.platform != "win32":
        return 0
    import ctypes

    hwnd = ctypes.windll.user32.GetParent(widget.winfo_id())
    return int(hwnd or 0)


def win32_force_foreground(widget: tk.Misc) -> None:
    widget.deiconify()
    widget.lift()
    widget.focus_force()
    if sys.platform != "win32":
        return
    import ctypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    hwnd = win32_hwnd(widget)
    if not hwnd:
        return
    user32.ShowWindow(hwnd, 9)
    foreground = user32.GetForegroundWindow()
    current_thread = kernel32.GetCurrentThreadId()
    fg_thread = user32.GetWindowThreadProcessId(foreground, None)
    user32.AttachThreadInput(fg_thread, current_thread, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(fg_thread, current_thread, False)


def load_logo_frames(max_width: int = 118) -> tuple[list, int]:
    gif_path = asset_path("logo_compact.gif")
    if not gif_path.exists():
        gif_path = asset_path("logo_animated.gif")
    preview = asset_path("logo_preview.png")
    delay_ms = int(1000 / LOGO_FPS)
    frames: list = []

    if gif_path.exists() and HAS_PIL:
        image = Image.open(gif_path)
        ratio = min(1.0, max_width / float(image.size[0]))
        size = (max(1, int(image.size[0] * ratio)), max(1, int(image.size[1] * ratio)))
        for frame in ImageSequence.Iterator(image):
            converted = frame.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            frames.append(ImageTk.PhotoImage(converted))
        duration = image.info.get("duration") or delay_ms
        return frames, int(duration)

    if gif_path.exists():
        index = 0
        while True:
            try:
                frame = tk.PhotoImage(file=str(gif_path), format=f"gif -index {index}")
                if frame.width() > max_width:
                    factor = max(1, int(round(frame.width() / max_width)))
                    frame = frame.subsample(factor, factor)
                frames.append(frame)
                index += 1
            except tk.TclError:
                break
        if frames:
            return frames, delay_ms

    if preview.exists():
        if HAS_PIL:
            image = Image.open(preview)
            ratio = min(1.0, max_width / float(image.size[0]))
            size = (max(1, int(image.size[0] * ratio)), max(1, int(image.size[1] * ratio)))
            frames.append(ImageTk.PhotoImage(image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)))
        else:
            frames.append(tk.PhotoImage(file=str(preview)))
    return frames, delay_ms


class HoverButton(tk.Frame):
    def __init__(self, master: tk.Misc, text: str, command, accent: bool = False) -> None:
        super().__init__(master, bg=LINE, highlightthickness=0)
        self.command = command
        self.accent = accent
        self._hover = 0.0
        self._target = 0.0
        self._anim = None
        self.inner = tk.Label(
            self,
            text=text,
            bg=COPPER if accent else PANEL_ALT,
            fg="#1A1008" if accent else TEXT,
            font=ui_font(10, "bold") if accent else ui_font(10),
            padx=8,
            pady=7,
            cursor="hand2",
        )
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)
        for widget in (self, self.inner):
            widget.bind("<Enter>", lambda _e: self._set_hover(True))
            widget.bind("<Leave>", lambda _e: self._set_hover(False))
            widget.bind("<Button-1>", self._click)

    def _set_hover(self, hovered: bool) -> None:
        self._target = 1.0 if hovered else 0.0
        self._tick()

    def _tick(self) -> None:
        delta = self._target - self._hover
        if abs(delta) < 0.02:
            self._hover = self._target
        else:
            self._hover += delta * 0.28
            self._anim = self.after(16, self._tick)
        if self.accent:
            bg = mix_hex(COPPER, COPPER_HI, self._hover)
            fg = "#1A1008"
            border = mix_hex(COPPER, "#F0C48A", self._hover)
        else:
            bg = mix_hex(PANEL_ALT, "#2A2118", self._hover)
            fg = mix_hex(TEXT, COPPER_HI, self._hover)
            border = mix_hex(LINE, COPPER, self._hover)
        self.configure(bg=border)
        self.inner.configure(bg=bg, fg=fg)

    def _click(self, _event=None) -> None:
        self.command()


class RecentChip(tk.Frame):
    def __init__(self, master: tk.Misc, key: str, stamp: str, on_open, on_remove) -> None:
        super().__init__(master, bg=LINE, highlightthickness=0)
        self.inner = tk.Frame(self, bg=PANEL_ALT)
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)
        label = tk.Label(
            self.inner,
            text=f"PR#{key if len(key) < 24 else key[:22] + '…'}",
            bg=PANEL_ALT,
            fg=TEXT,
            font=ui_font(10, "bold"),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        meta = tk.Label(
            self.inner,
            text=stamp,
            bg=PANEL_ALT,
            fg=MUTED,
            font=ui_font(8),
            padx=(0, 4),
            cursor="hand2",
        )
        close = tk.Label(
            self.inner,
            text="×",
            bg=PANEL_ALT,
            fg=MUTED,
            font=ui_font(11),
            padx=8,
            cursor="hand2",
        )
        label.pack(side="left")
        meta.pack(side="left")
        close.pack(side="right")
        for widget in (self.inner, label, meta):
            widget.bind("<Button-1>", lambda _e, k=key: on_open(k))
            widget.bind("<Enter>", lambda _e: self._paint(True))
            widget.bind("<Leave>", lambda _e: self._paint(False))
        close.bind("<Button-1>", lambda _e, k=key: on_remove(k))

    def _paint(self, hovered: bool) -> None:
        bg = "#241C16" if hovered else PANEL_ALT
        border = COPPER if hovered else LINE
        self.configure(bg=border)
        for child in self.inner.winfo_children():
            child.configure(bg=bg)
        self.inner.configure(bg=bg)


class ServerLauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(WINDOW_TITLE)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("400x640")
        self._photos: list = []
        self._ignore_search = False
        self._logo_index = 0
        self._logo_frames: list = []
        self._particles: list[dict] = []
        self._tick = 0.0
        self._pinned = False
        self._suggest_visible = False
        self._set_icons()
        self._build_ui()
        self._load_logo()
        self._refresh_recents()
        self._position_window()
        self._animate_entrance()
        self._animate()
        self._bind_window_focus()
        self.after(200, self._connect_projects)

    def _set_icons(self) -> None:
        ico = asset_path("icon.ico")
        png = asset_path("icon.png")
        if sys.platform == "win32" and ico.exists():
            try:
                self.iconbitmap(default=str(ico))
            except tk.TclError:
                pass
        if png.exists():
            try:
                photo = tk.PhotoImage(file=str(png))
                self._photos.append(photo)
                self.iconphoto(True, photo)
            except tk.TclError:
                pass

    def _build_ui(self) -> None:
        self.stage = tk.Frame(self, bg=BG)
        self.stage.pack(fill="both", expand=True)

        self.header_canvas = tk.Canvas(self.stage, height=64, bg=BG, highlightthickness=0, bd=0)
        self.header_canvas.pack(fill="x")
        self.logo_item = self.header_canvas.create_image(10, 32, anchor="w")
        self.title_item = self.header_canvas.create_text(
            136, 24, anchor="w", fill=TEXT, font=ui_font(13, "bold"), text="SERVER LAUNCHER"
        )
        self.header_canvas.create_text(
            136, 42, anchor="w", fill=MUTED, font=ui_font(9), text="Prime Rebar project center"
        )
        self.scan_line = self.header_canvas.create_line(0, 63, 400, 63, fill=COPPER, width=1)
        self._init_particles()

        body = tk.Frame(self.stage, bg=BG, padx=12, pady=10)
        body.pack(fill="both", expand=True)

        card = tk.Frame(body, bg=LINE)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=PANEL, padx=10, pady=10)
        inner.pack(fill="x", padx=1, pady=1)

        tk.Label(inner, text="PROJECT", bg=PANEL, fg=COPPER, font=ui_font(8, "bold")).pack(anchor="w")
        row = tk.Frame(inner, bg=PANEL)
        row.pack(fill="x", pady=(4, 10))
        tk.Label(row, text="PR#", bg=PANEL, fg=STEEL, font=ui_font(11, "bold")).pack(side="left", padx=(0, 6))

        self.search_border = tk.Frame(row, bg=LINE)
        self.search_border.pack(side="left", fill="x", expand=True)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        self.search_entry = tk.Entry(
            self.search_border,
            textvariable=self.search_var,
            font=ui_font(12),
            bg="#1C1814",
            fg=TEXT,
            insertbackground=COPPER_HI,
            relief="flat",
            highlightthickness=0,
            bd=6,
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<FocusIn>", self._on_search_focus)
        self.search_entry.bind("<Down>", self._focus_suggestions)
        self.search_entry.bind("<Escape>", lambda _e: self._hide_suggestions())
        self.search_entry.bind("<Return>", self._on_search_return)
        self.search_entry.focus_set()
        browse = tk.Label(
            row,
            text="...",
            bg=PANEL_ALT,
            fg=TEXT,
            font=ui_font(11, "bold"),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        browse.pack(side="right", padx=(8, 0))
        browse.bind("<Button-1>", lambda _e: self._choose_projects_folder())

        self.suggest_win = tk.Toplevel(self)
        self.suggest_win.withdraw()
        self.suggest_win.overrideredirect(True)
        self.suggest_win.configure(bg=COPPER)
        self.suggest_list = tk.Listbox(
            self.suggest_win,
            height=7,
            font=ui_font(10),
            bg="#1C1814",
            fg=TEXT,
            selectbackground=COPPER,
            selectforeground="#1A1008",
            activestyle="none",
            highlightthickness=0,
            relief="flat",
            bd=0,
            exportselection=False,
        )
        self.suggest_list.pack(fill="both", expand=True, padx=1, pady=1)
        self.suggest_list.bind("<ButtonRelease-1>", self._apply_suggestion)
        self.suggest_list.bind("<Return>", self._apply_suggestion)
        self.suggest_list.bind("<Escape>", lambda _e: self._hide_suggestions())
        self.bind("<Button-1>", self._on_root_click, add="+")

        tk.Label(inner, text="QUICK ACTIONS", bg=PANEL, fg=STEEL, font=ui_font(8, "bold")).pack(anchor="w")
        grid = tk.Frame(inner, bg=PANEL)
        grid.pack(fill="x", pady=(6, 8))
        grid.columnconfigure(0, weight=1, uniform="a")
        grid.columnconfigure(1, weight=1, uniform="a")
        actions = [
            ("Contract Drawings", 0, 0, self._open_contract_drawings),
            ("Incoming", 0, 1, self._open_incoming),
            ("Working", 1, 0, self._open_working),
            ("Outgoing", 1, 1, self._open_outgoing),
            ("Project Docs", 2, 0, self._open_project_doc),
            ("Listing", 2, 1, self._open_listing),
            ("Tracker", 3, 0, self._open_tracker),
            ("List Log", 3, 1, self._open_listlog),
            ("Scheduler", 4, 0, self._open_scheduler),
            ("Change Order", 4, 1, self._open_change_order),
        ]
        self._action_buttons: list[HoverButton] = []
        for text, row_i, col, command in actions:
            button = HoverButton(grid, text, command)
            button.grid(row=row_i, column=col, sticky="nsew", padx=3, pady=3)
            self._action_buttons.append(button)

        HoverButton(inner, "Open Working", self._open_working, accent=True).pack(fill="x", pady=(2, 0))

        recents_head = tk.Frame(body, bg=BG)
        recents_head.pack(fill="x", pady=(12, 6))
        tk.Label(recents_head, text="RECENT", bg=BG, fg=STEEL, font=ui_font(8, "bold")).pack(side="left")
        clear = tk.Label(recents_head, text="Clear", bg=BG, fg=MUTED, font=ui_font(8), cursor="hand2")
        clear.pack(side="right")
        clear.bind("<Button-1>", lambda _e: self._clear_recents())
        clear.bind("<Enter>", lambda _e: clear.configure(fg=COPPER_HI))
        clear.bind("<Leave>", lambda _e: clear.configure(fg=MUTED))

        recents_card = tk.Frame(body, bg=LINE)
        recents_card.pack(fill="both", expand=True)
        self.recents_wrap = tk.Frame(recents_card, bg=PANEL, padx=8, pady=8)
        self.recents_wrap.pack(fill="both", expand=True, padx=1, pady=1)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(self.stage, bg="#0C0C0C")
        status_bar.pack(fill="x", side="bottom")
        self.status = tk.Label(
            status_bar,
            textvariable=self.status_var,
            bg="#0C0C0C",
            fg=MUTED,
            font=ui_font(8),
            anchor="w",
            padx=12,
            pady=6,
        )
        self.status.pack(side="left", fill="x", expand=True)
        self.pin_button = tk.Label(
            status_bar,
            text="PIN",
            bg="#0C0C0C",
            fg=MUTED,
            font=ui_font(8, "bold"),
            padx=12,
            pady=6,
            cursor="hand2",
        )
        self.pin_button.pack(side="right")
        self.pin_button.bind("<Button-1>", lambda _e: self._toggle_pin())

    def _init_particles(self) -> None:
        self._particles = []
        for _ in range(12):
            self._particles.append(
                {
                    "x": random.uniform(0, 400),
                    "y": random.uniform(6, 56),
                    "vx": random.uniform(-0.18, 0.35),
                    "vy": random.uniform(-0.08, 0.08),
                    "r": 1,
                    "color": random.choice((COPPER, COPPER_HI, "#5A4A3A")),
                    "id": None,
                }
            )
        for particle in self._particles:
            particle["id"] = self.header_canvas.create_oval(
                particle["x"],
                particle["y"],
                particle["x"] + particle["r"],
                particle["y"] + particle["r"],
                fill=particle["color"],
                outline="",
            )

    def _load_logo(self) -> None:
        frames, delay = load_logo_frames(118)
        self._logo_frames = frames
        self._logo_delay = delay
        self._photos.extend(frames)
        if frames:
            self.header_canvas.itemconfigure(self.logo_item, image=frames[0])
            self.after(delay, self._advance_logo)

    def _advance_logo(self) -> None:
        if not self._logo_frames:
            return
        self._logo_index = (self._logo_index + 1) % len(self._logo_frames)
        self.header_canvas.itemconfigure(self.logo_item, image=self._logo_frames[self._logo_index])
        self.after(self._logo_delay, self._advance_logo)

    def _animate(self) -> None:
        self._tick += 0.045
        width = max(self.header_canvas.winfo_width(), 400)
        self.header_canvas.coords(self.scan_line, 0, 63, width, 63)
        glow = mix_hex(COPPER, "#3A2416", (math.sin(self._tick * 1.4) + 1) / 2)
        self.header_canvas.itemconfigure(self.scan_line, fill=glow)
        for particle in self._particles:
            particle["x"] = (particle["x"] + particle["vx"]) % width
            particle["y"] += particle["vy"] + math.sin(self._tick + particle["x"] * 0.02) * 0.05
            if particle["y"] < 4:
                particle["y"] = 56
            if particle["y"] > 56:
                particle["y"] = 4
            self.header_canvas.coords(
                particle["id"],
                particle["x"],
                particle["y"],
                particle["x"] + particle["r"] + 1,
                particle["y"] + particle["r"] + 1,
            )
        self.after(33, self._animate)

    def _animate_entrance(self) -> None:
        for index, button in enumerate(self._action_buttons):
            button.grid_remove()
            self.after(180 + index * 45, lambda b=button: b.grid())

    def _bind_window_focus(self) -> None:
        self.bind("<Map>", self._on_map)
        self.bind("<Unmap>", self._on_unmap)
        self.bind("<Configure>", self._on_configure)
        self.bind_all("<Button-1>", self._on_root_click, add="+")
        if sys.platform == "win32":
            self.after(200, self._raise_window)

    def _on_unmap(self, event: tk.Event) -> None:
        if event.widget is self:
            self._hide_suggestions()

    def _on_map(self, event: tk.Event) -> None:
        if event.widget is not self:
            return
        self.after(10, self._raise_window)

    def _raise_window(self) -> None:
        win32_force_foreground(self)
        if self._pinned:
            self.attributes("-topmost", True)
        else:
            self.attributes("-topmost", True)
            self.after(80, lambda: self.attributes("-topmost", False) if not self._pinned else None)

    def _toggle_pin(self) -> None:
        self._pinned = not self._pinned
        self.attributes("-topmost", self._pinned)
        self.pin_button.configure(fg=COPPER_HI if self._pinned else MUTED, text="PINNED" if self._pinned else "PIN")
        self._set_status("Always on top" if self._pinned else "Pin off")

    def _on_configure(self, event: tk.Event) -> None:
        if event.widget is self and self._suggest_visible:
            self.after_idle(self._reposition_suggestions)

    def _on_search_focus(self, _event=None) -> None:
        self.search_border.configure(bg=COPPER)

    def _on_search_return(self, _event=None):
        if self._suggest_visible and self.suggest_list.size():
            if not self.suggest_list.curselection():
                self.suggest_list.selection_set(0)
            self._apply_suggestion()
            return "break"
        self._open_working()
        return "break"

    def _focus_suggestions(self, _event=None):
        self._refresh_suggestions()
        if self._suggest_visible and self.suggest_list.size():
            self.suggest_list.focus_set()
            self.suggest_list.selection_clear(0, tk.END)
            self.suggest_list.selection_set(0)
            self.suggest_list.activate(0)
        return "break"

    def _position_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = max(40, (self.winfo_screenheight() - height) // 3)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _project_key(self) -> str:
        return normalize_query(self.search_var.get())

    def _project_folder(self) -> str:
        root = get_projects_root()[0] or DEFAULT_PROJECTS_ROOT
        return os.path.join(root, f"PR#{self._project_key()}")

    def _project_id(self) -> str:
        return f"PR#{self._project_key()}".split("_", 1)[0]

    def _set_status(self, text: str, ok: bool = True) -> None:
        self.status_var.set(text)
        self.status.configure(fg=COPPER_HI if ok else DANGER)

    def _connect_projects(self) -> None:
        root, error = get_projects_root(refresh=True)
        if root:
            self._set_status(f"Connected  ·  {root}")
        else:
            self._set_status(error or "Projects folder not found — click ... to select it", ok=False)

    def _choose_projects_folder(self) -> None:
        self._hide_suggestions()
        initial = get_projects_root()[0] or "Z:\\"
        selected = filedialog.askdirectory(title="Select Z:\\Projects folder", initialdir=initial)
        if not selected:
            return
        if set_projects_root(selected):
            self._set_status(f"Connected  ·  {selected}")
            self._refresh_suggestions()
        else:
            self._set_status("Could not open that folder", ok=False)

    def _load_recents(self) -> list[dict]:
        path = recents_file()
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            return []
        return []

    def _save_recents(self, items: list[dict]) -> None:
        recents_file().write_text(json.dumps(items, indent=2), encoding="utf-8")

    def _relative_time(self, iso_stamp: str) -> str:
        try:
            opened = datetime.fromisoformat(iso_stamp)
        except ValueError:
            return ""
        seconds = int((datetime.now() - opened).total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    def _refresh_recents(self) -> None:
        for child in self.recents_wrap.winfo_children():
            child.destroy()
        items = self._load_recents()
        if not items:
            tk.Label(
                self.recents_wrap,
                text="No recent projects yet.",
                bg=PANEL,
                fg=MUTED,
                font=ui_font(9),
            ).pack(anchor="w")
            return
        for item in items[:6]:
            chip = RecentChip(
                self.recents_wrap,
                item.get("key", ""),
                self._relative_time(item.get("opened_at", "")),
                self._open_recent,
                self._remove_recent,
            )
            chip.pack(fill="x", pady=3)

    def _remember_recent(self) -> None:
        key = self._project_key()
        if not key:
            return
        items = [item for item in self._load_recents() if item.get("key") != key]
        items.insert(0, {"key": key, "opened_at": datetime.now().isoformat(timespec="seconds")})
        self._save_recents(items[:MAX_RECENTS])
        self._refresh_recents()

    def _open_recent(self, key: str) -> None:
        self._ignore_search = True
        self.search_var.set(key)
        self._ignore_search = False
        self.search_entry.icursor(tk.END)
        self._hide_suggestions()
        self._set_status(f"Loaded PR#{key}  ·  choose a folder or document")
        self.search_entry.focus_set()

    def _remove_recent(self, key: str) -> None:
        items = [item for item in self._load_recents() if item.get("key") != key]
        self._save_recents(items)
        self._refresh_recents()

    def _clear_recents(self) -> None:
        self._save_recents([])
        self._refresh_recents()
        self._set_status("Recent projects cleared")

    def _on_search_changed(self, *_args: object) -> None:
        if self._ignore_search:
            return
        self._refresh_suggestions()

    def _refresh_suggestions(self) -> None:
        text = self.search_var.get()
        if len(normalize_query(text)) < 2:
            self._hide_suggestions()
            return
        names, error = list_project_names(text)
        if error:
            self._hide_suggestions()
            self._set_status(error, ok=False)
            return
        self._show_suggestions(names)

    def _show_suggestions(self, names: list[str]) -> None:
        if not names:
            self._hide_suggestions()
            return
        self.suggest_list.delete(0, tk.END)
        for name in names[:20]:
            self.suggest_list.insert(tk.END, name)
        self._suggest_visible = True
        self._reposition_suggestions()
        self.suggest_win.deiconify()
        self.suggest_win.lift()

    def _reposition_suggestions(self) -> None:
        if not self._suggest_visible:
            return
        self.update_idletasks()
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()
        width = max(self.search_entry.winfo_width(), 240)
        count = max(self.suggest_list.size(), 1)
        height = min(196, 26 * min(count, 7) + 4)
        self.suggest_win.geometry(f"{width}x{height}+{x}+{y}")

    def _hide_suggestions(self) -> None:
        self._suggest_visible = False
        self.suggest_win.withdraw()

    def _apply_suggestion(self, _event: object | None = None) -> None:
        selection = self.suggest_list.curselection()
        if not selection:
            return
        value = self.suggest_list.get(selection[0])
        self._ignore_search = True
        self.search_var.set(value)
        self._ignore_search = False
        self.search_entry.icursor(tk.END)
        self._hide_suggestions()
        self.search_entry.focus_set()
        self._set_status(f"Selected PR#{value}")

    def _on_root_click(self, event: tk.Event) -> None:
        widget = event.widget
        if widget in (self.search_entry, self.suggest_list, self.search_border):
            return
        try:
            if str(widget).startswith(str(self.suggest_win)):
                return
        except (tk.TclError, AttributeError):
            pass
        self._hide_suggestions()

    def _opened(self, action: str) -> None:
        self._remember_recent()
        key = self._project_key() or "—"
        self._set_status(f"Opened {action}  ·  PR#{key}")

    def _open_single(self, path: str, action: str) -> None:
        try:
            open_path(path)
            self._opened(action)
        except BaseException as exc:
            self._set_status(f"Failed to open {action}", ok=False)
            show_error(action, exc)

    def _open_fallback(self, paths: list[str], action: str) -> None:
        last_error: BaseException | None = None
        for path in paths:
            try:
                open_path(path)
                self._opened(action)
                return
            except BaseException as exc:
                last_error = exc
        if last_error is not None:
            self._set_status(f"Failed to open {action}", ok=False)
            show_error(action, last_error)

    def _open_contract_drawings(self) -> None:
        dated = os.path.join(
            self._project_folder(), "1.0 Contract Drawings", datetime.now().strftime("%m.%d.%Y")
        )
        parent = os.path.join(self._project_folder(), "1.0 Contract Drawings")
        self._open_fallback([dated, parent], "Contract Drawings")

    def _open_incoming(self) -> None:
        self._open_single(os.path.join(self._project_folder(), "2.0 Incoming"), "Incoming")

    def _open_working(self) -> None:
        self._open_single(os.path.join(self._project_folder(), "3.0 Working"), "Working")

    def _open_outgoing(self) -> None:
        now = datetime.now()
        outgoing = os.path.join(self._project_folder(), "4.0 Outgoing")
        year = os.path.join(outgoing, now.strftime("%Y"))
        month = os.path.join(year, now.strftime("%B %Y"))
        day = os.path.join(month, now.strftime("%m.%d.%Y"))
        self._open_fallback([day, month, year, outgoing], "Outgoing")

    def _open_project_doc(self) -> None:
        self._open_single(
            os.path.join(self._project_folder(), "5.0 Project Documentation"),
            "Project Documentation",
        )

    def _open_listing(self) -> None:
        self._open_single(os.path.join(self._project_folder(), "7.0 Listing"), "Listing")

    def _open_tracker(self) -> None:
        self._open_single(
            os.path.join(get_projects_root()[0] or DEFAULT_PROJECTS_ROOT, "1.0 Project Tracker", f"{self._project_id()}_Tracker.xls"),
            "Tracker",
        )

    def _open_listlog(self) -> None:
        self._open_single(
            os.path.join(get_projects_root()[0] or DEFAULT_PROJECTS_ROOT, "2.0 Project Listlog", f"{self._project_id()}_Listlog.xls"),
            "List Log",
        )

    def _open_scheduler(self) -> None:
        self._open_single(
            os.path.join(
                get_projects_root()[0] or DEFAULT_PROJECTS_ROOT, "3.0 Drawing Schedular", f"{self._project_id()}_Schedular.xls"
            ),
            "Scheduler",
        )

    def _open_change_order(self) -> None:
        self._open_single(
            os.path.join(
                get_projects_root()[0] or DEFAULT_PROJECTS_ROOT, "4.0 Project Change_Order", f"{self._project_id()}_Schedular.xls"
            ),
            "Change Order",
        )


def main() -> None:
    app = ServerLauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()
