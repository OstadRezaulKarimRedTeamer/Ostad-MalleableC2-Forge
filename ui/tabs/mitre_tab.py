"""
MITRE ATT&CK Technique Mapping & RoE Audit Trail Tab
Displays MITRE ATT&CK matrix alignment and live cryptographic RoE audit events.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from backend.mitre_mapper import get_mitre_mapping
from backend.audit_trail import AuditTrail
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_AMBER, FONT_SUBTITLE, FONT_BODY,
    FONT_BOLD, FONT_CODE, BORDER_COLOR
)


class MitreTab(tk.Frame):
    """MITRE ATT&CK & Audit Trail Dashboard."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.audit = AuditTrail()

        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient="vertical", bg=BORDER_COLOR, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Top Pane: MITRE ATT&CK Table
        top_pane = tk.Frame(paned, bg=BG_DARK)
        paned.add(top_pane, minsize=220)

        hdr_m = tk.Frame(top_pane, bg=BG_CARD)
        hdr_m.pack(fill="x")
        tk.Label(hdr_m, text="⚔️ MITRE ATT&CK Matrix Technique Alignment", font=FONT_SUBTITLE, fg=ACCENT_CYAN, bg=BG_CARD).pack(side="left", padx=8, pady=4)

        tbl_f = tk.Frame(top_pane, bg=BORDER_COLOR, bd=1)
        tbl_f.pack(fill="both", expand=True, pady=(4, 0))

        cols = ("id", "name", "tactic", "component", "desc")
        self.tree_mitre = ttk.Treeview(tbl_f, columns=cols, show="headings", selectmode="browse")
        self.tree_mitre.heading("id", text="Technique ID")
        self.tree_mitre.heading("name", text="Technique Name")
        self.tree_mitre.heading("tactic", text="Tactic")
        self.tree_mitre.heading("component", text="Profile Component")
        self.tree_mitre.heading("desc", text="Description")

        self.tree_mitre.column("id", width=110, anchor="center")
        self.tree_mitre.column("name", width=220, anchor="w")
        self.tree_mitre.column("tactic", width=150, anchor="center")
        self.tree_mitre.column("component", width=180, anchor="w")
        self.tree_mitre.column("desc", width=340, anchor="w")

        scroll_m = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_mitre.yview)
        self.tree_mitre.configure(yscrollcommand=scroll_m.set)
        self.tree_mitre.pack(side="left", fill="both", expand=True)
        scroll_m.pack(side="right", fill="y")

        # Load MITRE rows
        for t in get_mitre_mapping():
            self.tree_mitre.insert("", "end", values=(
                t["id"], t["name"], t["tactic"], t["component"], t["description"]
            ))

        # 2. Bottom Pane: RoE Audit Trail Log Viewer
        bot_pane = tk.Frame(paned, bg=BG_DARK)
        paned.add(bot_pane, minsize=240)

        hdr_a = tk.Frame(bot_pane, bg=BG_CARD)
        hdr_a.pack(fill="x")
        tk.Label(hdr_a, text="📜 RoE Audit Trail Log (c2_audit_trail.log)", font=FONT_SUBTITLE, fg=ACCENT_GREEN, bg=BG_CARD).pack(side="left", padx=8, pady=4)

        tk.Button(hdr_a, text="🔄 Refresh Audit Log", font=FONT_BODY, bg=BG_INPUT, fg=TEXT_PRIMARY, relief="flat", padx=8, pady=2, command=self.refresh_audit_log).pack(side="right", padx=6, pady=2)

        log_f = tk.Frame(bot_pane, bg=BORDER_COLOR, bd=1)
        log_f.pack(fill="both", expand=True, pady=(4, 0))

        self.txt_audit = tk.Text(log_f, bg=BG_EDITOR, fg="#b0bec5", font=FONT_CODE, bd=0, padx=8, pady=8)
        scroll_a = ttk.Scrollbar(log_f, orient="vertical", command=self.txt_audit.yview)
        self.txt_audit.configure(yscrollcommand=scroll_a.set)
        self.txt_audit.pack(side="left", fill="both", expand=True)
        scroll_a.pack(side="right", fill="y")

        self.refresh_audit_log()

    def refresh_audit_log(self):
        self.txt_audit.delete("1.0", "end")
        logs = self.audit.get_recent_logs(limit=100)
        if not logs:
            self.txt_audit.insert("end", "[No audit events recorded yet. Start server or execute tasks to record events.]\n")
            return

        for record in logs:
            ts = record.get("timestamp", "")
            evt = record.get("event", "")
            det = json.dumps(record.get("details", {}))
            self.txt_audit.insert("end", f"[{ts}] {evt:<18} | {det}\n")
        self.txt_audit.see("end")
