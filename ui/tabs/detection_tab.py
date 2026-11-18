"""
Threat Hunting & RoE Detection Rules Tab
Generates Suricata, Snort, and YARA signatures from the active Malleable C2 profile.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional
from backend.models import Profile
from backend.detection_engine import DetectionEngine
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_CODE, BORDER_COLOR
)


class DetectionTab(tk.Frame):
    """Blue Team Detection & RoE Verification Workbench."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.profile: Optional[Profile] = None

        self._build_ui()

    def _build_ui(self):
        # Controls / Format Selector
        ctrl_bar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        ctrl_bar.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(ctrl_bar, text="Rule Format:", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=10, pady=8)

        self.var_format = tk.StringVar(value="suricata")
        for val, label in [("suricata", "Suricata NIDS"), ("snort", "Snort NIDS"), ("yara", "YARA Memory / PE")]:
            tk.Radiobutton(
                ctrl_bar, text=label, variable=self.var_format, value=val,
                bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_DARK, activebackground=BG_CARD,
                font=FONT_BODY, command=self.update_rules
            ).pack(side="left", padx=8)

        btn_copy = tk.Button(
            ctrl_bar, text="📋 Copy Rules", font=FONT_BODY, bg=BG_DARK, fg=TEXT_PRIMARY,
            activebackground=BG_CARD, relief="flat", padx=10, pady=4, command=self._copy_rules
        )
        btn_copy.pack(side="right", padx=5, pady=8)

        btn_export = tk.Button(
            ctrl_bar, text="💾 Export to File...", font=("Segoe UI", 9, "bold"), bg=ACCENT_CYAN, fg="#000",
            activebackground="#48cae4", relief="flat", padx=12, pady=4, command=self._export_rules
        )
        btn_export.pack(side="right", padx=10, pady=8)

        # Text Display Area
        disp_frame = tk.Frame(self, bg=BORDER_COLOR, bd=1)
        disp_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scroll_y = ttk.Scrollbar(disp_frame, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.txt_rules = tk.Text(
            disp_frame, bg=BG_EDITOR, fg="#e0e0e0", font=FONT_CODE,
            bd=0, padx=10, pady=10, wrap="none", yscrollcommand=scroll_y.set
        )
        self.txt_rules.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self.txt_rules.yview)

    def set_profile(self, profile: Profile):
        self.profile = profile
        self.update_rules()

    def update_rules(self):
        if not self.profile:
            return

        engine = DetectionEngine(self.profile)
        fmt = self.var_format.get()

        if fmt == "suricata":
            rules_text = engine.generate_suricata_rules()
        elif fmt == "snort":
            rules_text = engine.generate_snort_rules()
        elif fmt == "yara":
            rules_text = engine.generate_yara_rule()
        else:
            rules_text = ""

        self.txt_rules.delete("1.0", "end")
        self.txt_rules.insert("1.0", rules_text)

    def _copy_rules(self):
        content = self.txt_rules.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Rules copied to clipboard!")

    def _export_rules(self):
        fmt = self.var_format.get()
        ext = ".rules" if fmt in ("suricata", "snort") else ".yar"
        fpath = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} Rule", f"*{ext}"), ("All Files", "*.*")]
        )
        if fpath:
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(self.txt_rules.get("1.0", "end-1c"))
                messagebox.showinfo("Exported", f"Successfully exported rules to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
