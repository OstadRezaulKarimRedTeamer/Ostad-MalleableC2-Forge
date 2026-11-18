"""
Generator & Morphing Wizard Tab
Allows operators to configure and generate polymorphic, evasion-tuned Malleable C2 profiles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any
from ui.theme import (
    BG_DARK, BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_RED, ACCENT_RED_HOVER, ACCENT_CYAN, ACCENT_GREEN, FONT_TITLE,
    FONT_SUBTITLE, FONT_BODY, FONT_BOLD, BORDER_COLOR
)
from backend.wordlists import USER_AGENTS, SAFE_SPAWNTO_X64
from backend.templates import TEMPLATES_META


class GeneratorTab(tk.Frame):
    """Wizard to customize and polymorphically generate C2 profiles."""

    def __init__(self, parent, on_generate_callback: Callable[[Dict[str, Any]], None]):
        super().__init__(parent, bg=BG_DARK)
        self.on_generate_callback = on_generate_callback

        self._build_ui()

    def _build_ui(self):
        # Scrollable container
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=950)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Section 1: Template & Target Identity
        sec1 = self._create_section(scroll_frame, "1. Target Service & Deception Profile")

        row = 0
        tk.Label(sec1, text="Service Template:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_template = tk.StringVar(value="amazon_cloudfront")
        tpl_choices = [t["id"] for t in TEMPLATES_META]
        self.combo_template = ttk.Combobox(sec1, textvariable=self.var_template, values=tpl_choices, state="readonly", width=35)
        self.combo_template.grid(row=row, column=1, sticky="w", padx=10, pady=6)

        row += 1
        tk.Label(sec1, text="Evasion Level:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_evasion = tk.StringVar(value="stealth")
        evasion_frame = tk.Frame(sec1, bg=BG_CARD)
        evasion_frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        for val, label in [("standard", "Standard"), ("stealth", "Stealth (Recommended)"), ("paranoid", "Paranoid (Max Evasion)")]:
            tk.Radiobutton(
                evasion_frame, text=label, variable=self.var_evasion, value=val,
                bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT, activebackground=BG_CARD,
                activeforeground=ACCENT_CYAN, font=FONT_BODY
            ).pack(side="left", padx=6)

        row += 1
        tk.Label(sec1, text="Custom Host/Domain (Optional):", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_host = tk.StringVar(value="")
        self.entry_host = tk.Entry(sec1, textvariable=self.var_host, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, width=38, font=FONT_BODY)
        self.entry_host.grid(row=row, column=1, sticky="w", padx=10, pady=6)

        row += 1
        tk.Label(sec1, text="Workstation User-Agent:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_ua = tk.StringVar(value="Random High-Reputation Browser")
        ua_options = ["Random High-Reputation Browser"] + USER_AGENTS
        self.combo_ua = ttk.Combobox(sec1, textvariable=self.var_ua, values=ua_options, state="readonly", width=55)
        self.combo_ua.grid(row=row, column=1, sticky="w", padx=10, pady=6)

        # Section 2: Timing & Heartbeat Jitter
        sec2 = self._create_section(scroll_frame, "2. Network Heartbeat & Traffic Timing")

        row = 0
        tk.Label(sec2, text="Sleep Time (ms):", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_sleep = tk.IntVar(value=5000)
        sleep_box = tk.Frame(sec2, bg=BG_CARD)
        sleep_box.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        self.scale_sleep = tk.Scale(sleep_box, from_=1000, to=60000, resolution=1000, orient="horizontal", variable=self.var_sleep, length=240, bg=BG_CARD, fg=TEXT_PRIMARY, highlightthickness=0)
        self.scale_sleep.pack(side="left")
        self.lbl_sleep_val = tk.Label(sleep_box, text="5000 ms (5s)", font=FONT_BODY, fg=ACCENT_CYAN, bg=BG_CARD)
        self.lbl_sleep_val.pack(side="left", padx=10)
        self.scale_sleep.configure(command=lambda v: self.lbl_sleep_val.configure(text=f"{v} ms ({int(v)//1000}s)"))

        row += 1
        tk.Label(sec2, text="Jitter Percentage (%):", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_jitter = tk.IntVar(value=25)
        jitter_box = tk.Frame(sec2, bg=BG_CARD)
        jitter_box.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        self.scale_jitter = tk.Scale(jitter_box, from_=0, to=80, orient="horizontal", variable=self.var_jitter, length=240, bg=BG_CARD, fg=TEXT_PRIMARY, highlightthickness=0)
        self.scale_jitter.pack(side="left")
        self.lbl_jitter_val = tk.Label(jitter_box, text="25 %", font=FONT_BODY, fg=ACCENT_CYAN, bg=BG_CARD)
        self.lbl_jitter_val.pack(side="left", padx=10)
        self.scale_jitter.configure(command=lambda v: self.lbl_jitter_val.configure(text=f"{v} %"))

        # Section 3: In-Memory Evasion & EDR Defense
        sec3 = self._create_section(scroll_frame, "3. In-Memory Defense & EDR Protection")

        row = 0
        self.var_sleep_mask = tk.BooleanVar(value=True)
        tk.Checkbutton(
            sec3, text="Enable Sleep Mask (Encrypt memory payload during sleep)",
            variable=self.var_sleep_mask, bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
            activebackground=BG_CARD, font=FONT_BODY
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        row += 1
        self.var_cleanup = tk.BooleanVar(value=True)
        tk.Checkbutton(
            sec3, text="Enable Cleanup (Free reflective DLL loader stub after startup)",
            variable=self.var_cleanup, bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
            activebackground=BG_CARD, font=FONT_BODY
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        row += 1
        self.var_stomppe = tk.BooleanVar(value=True)
        tk.Checkbutton(
            sec3, text="Stomp PE Headers (Wipe in-memory MZ/PE headers)",
            variable=self.var_stomppe, bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT,
            activebackground=BG_CARD, font=FONT_BODY
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        row += 1
        self.var_userwx = tk.BooleanVar(value=False)
        tk.Checkbutton(
            sec3, text="Avoid RWX Memory (Enforce RX memory allocation to bypass EDR heuristics)",
            variable=self.var_userwx, bg=BG_CARD, fg=ACCENT_GREEN, selectcolor=BG_INPUT,
            activebackground=BG_CARD, font=FONT_BOLD
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        # Section 4: Injection & Post-Exploitation
        sec4 = self._create_section(scroll_frame, "4. Process Injection & Post-Exploitation")

        row = 0
        tk.Label(sec4, text="Memory Allocator:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_allocator = tk.StringVar(value="VirtualAllocEx")
        alloc_frame = tk.Frame(sec4, bg=BG_CARD)
        alloc_frame.grid(row=row, column=1, sticky="w", padx=10, pady=6)
        for val, label in [("VirtualAllocEx", "VirtualAllocEx"), ("NtMapViewOfSection", "NtMapViewOfSection (Advanced)")]:
            tk.Radiobutton(
                alloc_frame, text=label, variable=self.var_allocator, value=val,
                bg=BG_CARD, fg=TEXT_PRIMARY, selectcolor=BG_INPUT, activebackground=BG_CARD,
                font=FONT_BODY
            ).pack(side="left", padx=6)

        row += 1
        tk.Label(sec4, text="Post-Ex Spawnto (x64):", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=row, column=0, sticky="w", padx=10, pady=6)
        self.var_spawnto = tk.StringVar(value=SAFE_SPAWNTO_X64[0])
        self.combo_spawnto = ttk.Combobox(sec4, textvariable=self.var_spawnto, values=SAFE_SPAWNTO_X64, state="readonly", width=42)
        self.combo_spawnto.grid(row=row, column=1, sticky="w", padx=10, pady=6)

        # Action Buttons Bar
        btn_frame = tk.Frame(scroll_frame, bg=BG_DARK)
        btn_frame.pack(fill="x", padx=10, pady=16)

        self.btn_generate = tk.Button(
            btn_frame,
            text="⚡ Generate Polymorphic Profile Now",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_RED,
            fg="white",
            activebackground=ACCENT_RED_HOVER,
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self._on_generate_clicked
        )
        self.btn_generate.pack(side="left")

    def _create_section(self, parent, title: str) -> tk.LabelFrame:
        frame = tk.LabelFrame(
            parent,
            text=f"  {title}  ",
            font=FONT_SUBTITLE,
            fg=ACCENT_CYAN,
            bg=BG_CARD,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        frame.pack(fill="x", padx=10, pady=8)
        return frame

    def _on_generate_clicked(self):
        ua_choice = self.var_ua.get()
        custom_ua = None if ua_choice == "Random High-Reputation Browser" else ua_choice
        custom_host = self.var_host.get().strip() or None

        params = {
            "template_key": self.var_template.get(),
            "sleeptime": self.var_sleep.get(),
            "jitter": self.var_jitter.get(),
            "evasion_level": self.var_evasion.get(),
            "custom_host": custom_host,
            "custom_useragent": custom_ua,
            "allocator": self.var_allocator.get(),
            "use_ntmap": (self.var_allocator.get() == "NtMapViewOfSection")
        }
        self.on_generate_callback(params)
