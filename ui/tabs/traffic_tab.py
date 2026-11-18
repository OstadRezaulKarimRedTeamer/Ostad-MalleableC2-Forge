"""
Live Traffic Flow & HTTP Packet Stream Simulator Tab
Displays side-by-side wire captures of Beacon Check-in (GET) and Exfiltration (POST).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from backend.models import Profile
from backend.traffic_sim import TrafficSimulator
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_CODE, BORDER_COLOR
)


class TrafficTab(tk.Frame):
    """Network Packet Stream Visualizer."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.profile: Optional[Profile] = None

        self._build_ui()

    def _build_ui(self):
        # Top Controls Bar
        ctrl_bar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        ctrl_bar.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(ctrl_bar, text="Mock Beacon Metadata:", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=10, pady=8)
        self.var_meta = tk.StringVar(value="BEACON_ID=9821;ARCH=x64;HOST=DC-ENTERPRISE;USER=SYSTEM")
        self.entry_meta = tk.Entry(ctrl_bar, textvariable=self.var_meta, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, width=45, font=FONT_CODE)
        self.entry_meta.pack(side="left", padx=5, pady=8)

        btn_sim = tk.Button(
            ctrl_bar, text="🔄 Simulate Live Wire Packets", font=("Segoe UI", 9, "bold"),
            bg=ACCENT_CYAN, fg="#000", activebackground="#48cae4", relief="flat",
            padx=12, pady=4, cursor="hand2", command=self.update_simulation
        )
        btn_sim.pack(side="left", padx=10, pady=8)

        # Paned Window (Split Left & Right)
        paned = tk.PanedWindow(self, orient="horizontal", bg=BORDER_COLOR, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: HTTP-GET Check-in
        frame_get = tk.Frame(paned, bg=BG_DARK)
        paned.add(frame_get, minsize=400)
        self._build_stream_box(frame_get, "🌐 HTTP-GET Transaction (Beacon Check-in / Heartbeat)", is_get=True)

        # Right: HTTP-POST Exfiltration
        frame_post = tk.Frame(paned, bg=BG_DARK)
        paned.add(frame_post, minsize=400)
        self._build_stream_box(frame_post, "📤 HTTP-POST Transaction (Beacon Data Exfiltration)", is_get=False)

    def _build_stream_box(self, parent, title: str, is_get: bool):
        hdr = tk.Label(parent, text=title, font=FONT_SUBTITLE, fg=ACCENT_GREEN if is_get else ACCENT_RED, bg=BG_CARD, padx=8, pady=4)
        hdr.pack(fill="x")

        # Request area
        lbl_req = tk.Label(parent, text="► Client Request (Wire bytes):", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_DARK)
        lbl_req.pack(anchor="w", padx=5, pady=(5, 2))

        txt_req = tk.Text(parent, bg=BG_EDITOR, fg="#e0e0e0", font=FONT_CODE, height=12, bd=1, relief="solid", padx=6, pady=6)
        txt_req.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Response area
        lbl_resp = tk.Label(parent, text="◄ C2 Server Response (Wire bytes):", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_DARK)
        lbl_resp.pack(anchor="w", padx=5, pady=(5, 2))

        txt_resp = tk.Text(parent, bg=BG_EDITOR, fg="#81c784", font=FONT_CODE, height=8, bd=1, relief="solid", padx=6, pady=6)
        txt_resp.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        if is_get:
            self.txt_get_req = txt_req
            self.txt_get_resp = txt_resp
        else:
            self.txt_post_req = txt_req
            self.txt_post_resp = txt_resp

    def set_profile(self, profile: Profile):
        self.profile = profile
        self.update_simulation()

    def update_simulation(self):
        if not self.profile:
            return

        sim = TrafficSimulator(self.profile)
        meta_bytes = self.var_meta.get().encode('utf-8', errors='ignore')

        # Run GET
        req_get, resp_get = sim.simulate_get_transaction(meta_bytes)
        self.txt_get_req.delete("1.0", "end")
        self.txt_get_req.insert("1.0", req_get)
        self.txt_get_resp.delete("1.0", "end")
        self.txt_get_resp.insert("1.0", resp_get)

        # Run POST
        req_post, resp_post = sim.simulate_post_transaction()
        self.txt_post_req.delete("1.0", "end")
        self.txt_post_req.insert("1.0", req_post)
        self.txt_post_resp.delete("1.0", "end")
        self.txt_post_resp.insert("1.0", resp_post)
