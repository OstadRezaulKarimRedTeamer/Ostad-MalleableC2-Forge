"""
OPSEC Audit & Linter Tab (c2lint Replica)
Displays comprehensive security audit results, OPSEC scores, and remediation advice.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from backend.models import Profile, AuditReport
from backend.linter import C2Linter
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_AMBER, ACCENT_RED, FONT_SCORE,
    FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BOLD, FONT_CODE, BORDER_COLOR
)


class LinterTab(tk.Frame):
    """c2lint OPSEC & Syntax Audit Dashboard."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.profile: Optional[Profile] = None
        self.report: Optional[AuditReport] = None

        self._build_ui()

    def _build_ui(self):
        # Header / Score Dashboard
        top_dash = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        top_dash.pack(fill="x", padx=10, pady=(10, 5))

        # Score box
        score_box = tk.Frame(top_dash, bg=BG_CARD)
        score_box.pack(side="left", padx=20, pady=10)

        tk.Label(score_box, text="OPSEC STEALTH SCORE", font=FONT_SUBTITLE, fg=TEXT_SECONDARY, bg=BG_CARD).pack()
        self.lbl_score = tk.Label(score_box, text="100 / 100", font=FONT_SCORE, fg=ACCENT_GREEN, bg=BG_CARD)
        self.lbl_score.pack()
        self.lbl_grade = tk.Label(score_box, text="Grade: A+ (Maximum Stealth)", font=FONT_BOLD, fg=ACCENT_GREEN, bg=BG_CARD)
        self.lbl_grade.pack()

        # Divider
        tk.Frame(top_dash, width=2, bg=BORDER_COLOR).pack(side="left", fill="y", pady=10)

        # Stats Cards
        stats_box = tk.Frame(top_dash, bg=BG_CARD)
        stats_box.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        row_f = tk.Frame(stats_box, bg=BG_CARD)
        row_f.pack(fill="x", expand=True)

        self.card_crit = self._create_stat_badge(row_f, "Critical Risks", "0", ACCENT_RED)
        self.card_warn = self._create_stat_badge(row_f, "Warnings", "0", ACCENT_AMBER)
        self.card_pass = self._create_stat_badge(row_f, "Passed Checks", "0", ACCENT_GREEN)

        btn_audit = tk.Button(
            top_dash, text="🔍 Re-Run c2lint Audit", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_CYAN, fg="#000", activebackground="#48cae4", relief="flat",
            padx=14, pady=8, cursor="hand2", command=self.run_audit
        )
        btn_audit.pack(side="right", padx=20, pady=15)

        # Issues Table Area
        tbl_frame = tk.Frame(self, bg=BORDER_COLOR, bd=1)
        tbl_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("id", "cat", "sev", "msg", "fix")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="Rule ID")
        self.tree.heading("cat", text="Category")
        self.tree.heading("sev", text="Severity")
        self.tree.heading("msg", text="Audit Finding / Issue Message")
        self.tree.heading("fix", text="Recommended Fix")

        self.tree.column("id", width=90, anchor="center")
        self.tree.column("cat", width=90, anchor="center")
        self.tree.column("sev", width=90, anchor="center")
        self.tree.column("msg", width=380, anchor="w")
        self.tree.column("fix", width=340, anchor="w")

        # Styling treeview colors
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=BG_DARK, foreground=TEXT_PRIMARY, fieldbackground=BG_DARK, font=FONT_BODY, rowheight=28)
        style.configure("Treeview.Heading", background=BG_CARD, foreground=TEXT_PRIMARY, font=FONT_BOLD)
        style.map("Treeview", background=[("selected", "#2a3a4a")])

        scroll_y = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _create_stat_badge(self, parent, title: str, count: str, color: str):
        frame = tk.Frame(parent, bg=BG_INPUT, bd=1, relief="solid", padx=15, pady=8)
        frame.pack(side="left", padx=10, expand=True, fill="both")
        lbl_c = tk.Label(frame, text=count, font=("Segoe UI", 16, "bold"), fg=color, bg=BG_INPUT)
        lbl_c.pack()
        tk.Label(frame, text=title, font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_INPUT).pack()
        return lbl_c

    def set_profile(self, profile: Profile):
        self.profile = profile
        self.run_audit()

    def run_audit(self):
        if not self.profile:
            return

        linter = C2Linter()
        self.report = linter.audit(self.profile)

        # Update Score Display
        score = self.report.score
        grade = self.report.grade
        self.lbl_score.config(text=f"{score} / 100")
        score_color = ACCENT_GREEN if score >= 85 else (ACCENT_AMBER if score >= 65 else ACCENT_RED)
        self.lbl_score.config(fg=score_color)
        self.lbl_grade.config(text=f"Grade: {grade} ({'Maximum Stealth' if score >= 90 else 'Moderate Risk' if score >= 70 else 'High Detection Risk'})", fg=score_color)

        # Update Stat Badges
        self.card_crit.config(text=str(self.report.critical_count))
        self.card_warn.config(text=str(self.report.warning_count))
        self.card_pass.config(text=str(len(self.report.passed_rules)))

        # Update Treeview
        self.tree.delete(*self.tree.get_children())

        # Insert Issues
        for issue in self.report.issues:
            self.tree.insert("", "end", values=(
                issue.rule_id,
                issue.category,
                issue.severity,
                issue.message,
                issue.suggestion
            ))

        # Insert Passed Rules as INFO
        for rule_msg in self.report.passed_rules:
            self.tree.insert("", "end", values=(
                "PASS",
                "VERIFIED",
                "PASSED",
                rule_msg,
                "✓ Operates within secure parameters"
            ))
