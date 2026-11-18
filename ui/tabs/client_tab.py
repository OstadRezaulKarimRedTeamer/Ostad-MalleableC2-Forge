"""
C2 Client Agent Simulator & Route Cycling Tab
Allows operators to launch simulated Malleable C2 Beacon agents with live packet stream logs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from backend.models import Profile
from backend.c2_client import EmbeddedC2Client
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED, FONT_SUBTITLE, FONT_BODY,
    FONT_BOLD, FONT_CODE, BORDER_COLOR
)


class ClientTab(tk.Frame):
    """Integrated Live C2 Client Agent Simulator."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.profile: Optional[Profile] = None
        self.client: Optional[EmbeddedC2Client] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Controls Bar
        ctrl_bar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        ctrl_bar.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(ctrl_bar, text="C2 Egress Routes:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=(10, 4), pady=8)
        self.var_routes = tk.StringVar(value="127.0.0.1")
        self.entry_routes = tk.Entry(ctrl_bar, textvariable=self.var_routes, width=22, font=FONT_CODE, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.entry_routes.pack(side="left", padx=4, pady=8)

        tk.Label(ctrl_bar, text="Port:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=(10, 4), pady=8)
        self.var_port = tk.StringVar(value="8080")
        self.entry_port = tk.Entry(ctrl_bar, textvariable=self.var_port, width=6, font=FONT_CODE, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.entry_port.pack(side="left", padx=4, pady=8)

        tk.Label(ctrl_bar, text="Rounds:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=(10, 4), pady=8)
        self.var_rounds = tk.StringVar(value="5")
        self.entry_rounds = tk.Entry(ctrl_bar, textvariable=self.var_rounds, width=4, font=FONT_CODE, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.entry_rounds.pack(side="left", padx=4, pady=8)

        self.btn_toggle_client = tk.Button(
            ctrl_bar, text="🚀 Launch Client Agent", font=FONT_BOLD, bg=ACCENT_CYAN, fg="#000",
            activebackground="#48cae4", relief="flat", padx=14, pady=5, cursor="hand2",
            command=self._toggle_client
        )
        self.btn_toggle_client.pack(side="left", padx=10, pady=8)

        self.lbl_client_status = tk.Label(ctrl_bar, text="● IDLE", font=FONT_BOLD, fg=TEXT_SECONDARY, bg=BG_CARD)
        self.lbl_client_status.pack(side="left", padx=10, pady=8)

        tk.Button(ctrl_bar, text="Clear Logs", font=FONT_BODY, bg=BG_INPUT, fg=TEXT_SECONDARY, relief="flat", padx=8, pady=4, command=self._clear_log).pack(side="right", padx=10, pady=8)

        # 2. Main Live Client Log Console
        log_frame = tk.Frame(self, bg=BORDER_COLOR, bd=1)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_log = tk.Text(log_frame, bg=BG_EDITOR, fg="#e0e0e0", font=FONT_CODE, bd=0, padx=10, pady=10)
        scroll_y = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=scroll_y.set)

        self.txt_log.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def set_profile(self, profile: Profile):
        self.profile = profile

    def _toggle_client(self):
        if self.client and self.client.running:
            self.client.stop()
            self.btn_toggle_client.config(text="🚀 Launch Client Agent", bg=ACCENT_CYAN)
            self.lbl_client_status.config(text="● IDLE", fg=TEXT_SECONDARY)
        else:
            if not self.profile:
                messagebox.showerror("Error", "No profile loaded.")
                return

            try:
                port = int(self.var_port.get().strip())
                rounds = int(self.var_rounds.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid port or rounds number.")
                return

            routes_str = self.var_routes.get().strip()
            endpoints = [r.strip() for r in routes_str.split(",") if r.strip()]
            if not endpoints:
                endpoints = ["127.0.0.1"]

            self.client = EmbeddedC2Client(
                c2_endpoints=endpoints,
                port=port,
                profile=self.profile,
                on_log_callback=self._append_log_threadsafe
            )
            self.client.start(rounds=rounds)
            self.btn_toggle_client.config(text="⏹ Terminate Agent", bg=ACCENT_RED)
            self.lbl_client_status.config(text="● ACTIVE RUNNING", fg=ACCENT_GREEN)

            # Auto reset button when finished
            self._check_agent_alive()

    def _check_agent_alive(self):
        if self.client and self.client.running:
            self.after(500, self._check_agent_alive)
        else:
            self.btn_toggle_client.config(text="🚀 Launch Client Agent", bg=ACCENT_CYAN)
            self.lbl_client_status.config(text="● IDLE", fg=TEXT_SECONDARY)

    def _append_log_threadsafe(self, msg: str):
        self.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg: str):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")

    def _clear_log(self):
        self.txt_log.delete("1.0", "end")
