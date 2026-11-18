"""
Ostad Malleable C2 Forge - Master Unified Application Window
Official Red Team & Adversary Emulation Suite by Ostad Red Team Forge.
Founder: Ostad Rezaul Karim (Top 1% Red Teamer)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from typing import Optional

from backend.models import Profile
from backend.generator import ProfileGenerator
from backend.serializer import serialize_profile
from backend.parser import parse_profile
from backend.templates import TEMPLATES_META, load_template_profile

from ui.theme import (
    BG_DARK, BG_SIDEBAR, BG_CARD, BG_CARD_HOVER, BG_INPUT, TEXT_PRIMARY,
    TEXT_SECONDARY, ACCENT_RED, ACCENT_RED_HOVER, ACCENT_CYAN, ACCENT_GREEN,
    ACCENT_AMBER, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BOLD, BORDER_COLOR
)
from ui.tabs.generator_tab import GeneratorTab
from ui.tabs.editor_tab import EditorTab
from ui.tabs.traffic_tab import TrafficTab
from ui.tabs.linter_tab import LinterTab
from ui.tabs.detection_tab import DetectionTab
from ui.tabs.transform_tab import TransformTab
from ui.tabs.server_tab import ServerTab
from ui.tabs.client_tab import ClientTab
from ui.tabs.mitre_tab import MitreTab


class MalleableC2App(tk.Tk):
    """Master Unified Application Window for Ostad Malleable C2 Forge."""

    def __init__(self):
        super().__init__()
        self.title("Ostad Malleable C2 Forge - Master Unified Red Team Dashboard | Ostad Red Team Forge")
        self.geometry("1360x860")
        self.minsize(1100, 700)
        self.configure(bg=BG_DARK)

        self.current_profile: Optional[Profile] = None
        self.current_profile_str: str = ""
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.profiles_dir = os.path.join(self.base_dir, "profiles")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._init_styles()
        self._build_ui()
        self._load_initial_profile()

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure notebook tabs
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=BG_CARD,
            foreground=TEXT_PRIMARY,
            padding=[14, 8],
            font=FONT_BOLD,
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT_RED), ("active", BG_CARD_HOVER)],
            foreground=[("selected", "white"), ("active", ACCENT_CYAN)]
        )

        # Scrollbar style
        style.configure(
            "Vertical.TScrollbar",
            background=BG_CARD,
            troughcolor=BG_DARK,
            arrowcolor=TEXT_PRIMARY,
            borderwidth=0
        )

    def _build_ui(self):
        # 1. Header Bar
        self._build_header()

        # 2. Main Middle Area (Sidebar + Notebook)
        main_body = tk.Frame(self, bg=BG_DARK)
        main_body.pack(fill="both", expand=True)

        # Left Sidebar (Templates & Quick Info)
        self._build_sidebar(main_body)

        # Notebook (Main Master Workspace)
        self.notebook = ttk.Notebook(main_body)
        self.notebook.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Tab 1: Live C2 Server Listener & Sessions
        self.tab_server = ServerTab(self.notebook)
        self.notebook.add(self.tab_server, text=" 🖥️ Live C2 Server ")

        # Tab 2: Live C2 Client Beacon Agent
        self.tab_client = ClientTab(self.notebook)
        self.notebook.add(self.tab_client, text=" 🚀 Live C2 Agent ")

        # Tab 3: Polymorphic Generator Wizard
        self.tab_generator = GeneratorTab(self.notebook, on_generate_callback=self._on_wizard_generate)
        self.notebook.add(self.tab_generator, text=" 🧙 Polymorphic Generator ")

        # Tab 4: Profile Source Editor
        self.tab_editor = EditorTab(self.notebook, on_profile_changed_callback=self._on_editor_code_changed)
        self.notebook.add(self.tab_editor, text=" 📝 Source Editor ")

        # Tab 5: Traffic Flow Simulator
        self.tab_traffic = TrafficTab(self.notebook)
        self.notebook.add(self.tab_traffic, text=" 🌐 Traffic Flow Simulator ")

        # Tab 6: OPSEC Audit & c2lint
        self.tab_linter = LinterTab(self.notebook)
        self.notebook.add(self.tab_linter, text=" 🛡️ OPSEC Audit (c2lint) ")

        # Tab 7: Blue Team Detection Rules (RoE)
        self.tab_detection = DetectionTab(self.notebook)
        self.notebook.add(self.tab_detection, text=" 🎯 Detection Rules (RoE) ")

        # Tab 8: Transform Sandbox
        self.tab_transform = TransformTab(self.notebook)
        self.notebook.add(self.tab_transform, text=" 🧪 Transform Sandbox ")

        # Tab 9: MITRE ATT&CK & Audit Trail
        self.tab_mitre = MitreTab(self.notebook)
        self.notebook.add(self.tab_mitre, text=" ⚔️ MITRE & Audit Trail ")

        # 3. Status Bar
        self._build_statusbar()

    def _build_header(self):
        header = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        header.pack(fill="x", padx=0, pady=0)

        # Branding Info
        brand_f = tk.Frame(header, bg=BG_CARD)
        brand_f.pack(side="left", padx=16, pady=8)

        lbl_title = tk.Label(
            brand_f,
            text="🦅 OSTAD MALLEABLE C2 FORGE - MASTER UNIFIED DASHBOARD",
            font=("Segoe UI", 13, "bold"),
            fg=ACCENT_RED,
            bg=BG_CARD
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            brand_f,
            text="Unified C2 Suite: Server, Client, Generator, OPSEC Linter & RoE Audit • Ostad Red Team Forge",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=BG_CARD
        )
        lbl_sub.pack(anchor="w")

        # Action Buttons
        btn_box = tk.Frame(header, bg=BG_CARD)
        btn_box.pack(side="right", padx=16, pady=8)

        btn_srv = tk.Button(
            btn_box, text="🖥️ C2 Server", font=FONT_BOLD, bg=BG_INPUT, fg=ACCENT_GREEN,
            activebackground=BG_CARD_HOVER, relief="flat", padx=10, pady=5, cursor="hand2",
            command=lambda: self.notebook.select(self.tab_server)
        )
        btn_srv.pack(side="left", padx=3)

        btn_cli = tk.Button(
            btn_box, text="🚀 C2 Agent", font=FONT_BOLD, bg=BG_INPUT, fg=ACCENT_CYAN,
            activebackground=BG_CARD_HOVER, relief="flat", padx=10, pady=5, cursor="hand2",
            command=lambda: self.notebook.select(self.tab_client)
        )
        btn_cli.pack(side="left", padx=3)

        btn_gen = tk.Button(
            btn_box, text="⚡ Morph Profile", font=FONT_BOLD, bg=ACCENT_RED, fg="white",
            activebackground=ACCENT_RED_HOVER, relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._quick_morph
        )
        btn_gen.pack(side="left", padx=3)

        btn_lint = tk.Button(
            btn_box, text="🔍 Run c2lint", font=FONT_BOLD, bg=BG_INPUT, fg=ACCENT_CYAN,
            activebackground=BG_CARD_HOVER, relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._switch_to_linter
        )
        btn_lint.pack(side="left", padx=3)

        btn_export = tk.Button(
            btn_box, text="💾 Export .profile", font=FONT_BOLD, bg=BG_INPUT, fg=TEXT_PRIMARY,
            activebackground=BG_CARD_HOVER, relief="flat", padx=10, pady=5, cursor="hand2",
            command=self._export_profile
        )
        btn_export.pack(side="left", padx=3)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=BG_SIDEBAR, width=240, bd=1, relief="solid")
        sidebar.pack(side="left", fill="y", padx=(0, 0), pady=0)
        sidebar.pack_propagate(False)

        # Title
        tk.Label(
            sidebar, text="PRESET TEMPLATES", font=FONT_SUBTITLE,
            fg=ACCENT_CYAN, bg=BG_SIDEBAR
        ).pack(anchor="w", padx=14, pady=(14, 6))

        # Templates Listbox / Buttons
        for tpl in TEMPLATES_META:
            tid = tpl["id"]
            btn = tk.Button(
                sidebar,
                text=f"{tpl['icon']}  {tpl['name']}",
                font=FONT_BODY,
                bg=BG_SIDEBAR,
                fg=TEXT_PRIMARY,
                activebackground=BG_CARD,
                activeforeground=ACCENT_CYAN,
                relief="flat",
                anchor="w",
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda k=tid: self._load_template_by_key(k)
            )
            btn.pack(fill="x", padx=6, pady=2)

        # Divider
        tk.Frame(sidebar, height=1, bg=BORDER_COLOR).pack(fill="x", padx=10, pady=16)

        # Active Profile Info Box
        tk.Label(sidebar, text="PROFILE TELEMETRY", font=FONT_SUBTITLE, fg=TEXT_SECONDARY, bg=BG_SIDEBAR).pack(anchor="w", padx=14, pady=(0, 6))

        self.info_box = tk.Frame(sidebar, bg=BG_CARD, bd=1, relief="solid", padx=10, pady=10)
        self.info_box.pack(fill="x", padx=10, pady=4)

        self.lbl_info_name = tk.Label(self.info_box, text="Name: Amazon CDN", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD, anchor="w", wraplength=200)
        self.lbl_info_name.pack(fill="x", pady=2)

        self.lbl_info_sleep = tk.Label(self.info_box, text="Sleep: 5000ms ± 25%", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD, anchor="w")
        self.lbl_info_sleep.pack(fill="x", pady=2)

        self.lbl_info_status = tk.Label(self.info_box, text="Status: ✓ Validated", font=FONT_BOLD, fg=ACCENT_GREEN, bg=BG_CARD, anchor="w")
        self.lbl_info_status.pack(fill="x", pady=2)

        # RoE Badge
        tk.Frame(sidebar, height=1, bg=BORDER_COLOR).pack(fill="x", padx=10, pady=16)
        badge_box = tk.Frame(sidebar, bg=BG_INPUT, bd=1, relief="solid", padx=10, pady=10)
        badge_box.pack(fill="x", padx=10, pady=4)
        tk.Label(badge_box, text="🛡️ ROE COMPLIANT", font=FONT_BOLD, fg=ACCENT_GREEN, bg=BG_INPUT).pack()
        tk.Label(badge_box, text="Red Team Adversary Simulation\nOstad Rezaul Karim", font=("Segoe UI", 8), fg=TEXT_SECONDARY, bg=BG_INPUT).pack(pady=4)

    def _build_statusbar(self):
        statusbar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid", height=24)
        statusbar.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(statusbar, text="Ready", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD)
        self.lbl_status.pack(side="left", padx=10, pady=2)

        lbl_forge = tk.Label(
            statusbar,
            text="Ostad Red Team Forge • Elite Offensive Security Edition",
            font=FONT_BODY,
            fg=ACCENT_CYAN,
            bg=BG_CARD
        )
        lbl_forge.pack(side="right", padx=10, pady=2)

    def _load_initial_profile(self):
        """Loads default initial profile on startup."""
        self._load_template_by_key("amazon_cloudfront")

    def _load_template_by_key(self, template_key: str):
        content = load_template_profile(template_key, self.profiles_dir)
        self._apply_profile_content(content)
        self.lbl_status.config(text=f"Loaded template: {template_key}")

    def _apply_profile_content(self, content: str):
        self.current_profile_str = content
        try:
            self.current_profile = parse_profile(content)
        except Exception as e:
            self.lbl_status.config(text=f"Parse Warning: {e}")

        # Update tabs
        self.tab_editor.set_content(content)
        if self.current_profile:
            self.tab_traffic.set_profile(self.current_profile)
            self.tab_linter.set_profile(self.current_profile)
            self.tab_detection.set_profile(self.current_profile)
            self.tab_server.set_profile(self.current_profile)
            self.tab_client.set_profile(self.current_profile)

            # Update sidebar info
            self.lbl_info_name.config(text=f"Profile: {self.current_profile.name[:25]}")
            self.lbl_info_sleep.config(text=f"Sleep: {self.current_profile.sleeptime}ms ± {self.current_profile.jitter}%")

    def _on_wizard_generate(self, params: dict):
        gen = ProfileGenerator()
        profile = gen.generate(**params)
        content = serialize_profile(profile)
        self._apply_profile_content(content)
        self.notebook.select(self.tab_editor)
        self.lbl_status.config(text="Polymorphic profile successfully generated and synchronized!")

    def _on_editor_code_changed(self, new_code: str):
        self.current_profile_str = new_code
        try:
            self.current_profile = parse_profile(new_code)
            self.tab_traffic.set_profile(self.current_profile)
            self.tab_linter.set_profile(self.current_profile)
            self.tab_detection.set_profile(self.current_profile)
            self.tab_server.set_profile(self.current_profile)
            self.tab_client.set_profile(self.current_profile)
            self.lbl_info_status.config(text="Status: ✓ Validated", fg=ACCENT_GREEN)
        except Exception:
            self.lbl_info_status.config(text="Status: ⚠️ Syntax Error", fg=ACCENT_RED)

    def _quick_morph(self):
        self.notebook.select(self.tab_generator)
        self.tab_generator._on_generate_clicked()

    def _switch_to_linter(self):
        self.notebook.select(self.tab_linter)
        self.tab_linter.run_audit()

    def _export_profile(self):
        self.tab_editor._save_file()

    def _on_close(self):
        """Clean shutdown of servers and clients."""
        try:
            if hasattr(self, 'tab_server') and self.tab_server.server and self.tab_server.server.running:
                self.tab_server.server.stop()
            if hasattr(self, 'tab_client') and self.tab_client.client and self.tab_client.client.running:
                self.tab_client.client.stop()
        except Exception:
            pass
        self.destroy()
