"""
Interactive Byte Transform Sandbox Tab
Allows operators and reverse engineers to experiment with Malleable C2 transforms in real-time.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple
from backend.transforms import TransformPipeline, apply_transform, reverse_transform
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED, FONT_SUBTITLE, FONT_BODY,
    FONT_BOLD, FONT_CODE, BORDER_COLOR
)


class TransformTab(tk.Frame):
    """Real-time Transform Sandbox (mask, base64, netbios, prepend, append)."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.pipeline_steps: List[Tuple[str, str]] = [
            ("mask", ""),
            ("base64url", ""),
            ("prepend", "token=")
        ]

        self._build_ui()

    def _build_ui(self):
        # Left Panel: Steps & Controls
        left_p = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid", width=360)
        left_p.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left_p, text="Transform Pipeline Builder", font=FONT_SUBTITLE, fg=ACCENT_CYAN, bg=BG_CARD).pack(anchor="w", padx=12, pady=10)

        # Add Step Frame
        add_f = tk.LabelFrame(left_p, text=" Add New Step ", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD, bd=1, relief="solid", padx=8, pady=8)
        add_f.pack(fill="x", padx=10, pady=5)

        tk.Label(add_f, text="Transform:", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=0, sticky="w", pady=4)
        self.var_action = tk.StringVar(value="mask")
        self.combo_action = ttk.Combobox(add_f, textvariable=self.var_action, values=["mask", "base64", "base64url", "netbios", "netbiosu", "prepend", "append"], state="readonly", width=14)
        self.combo_action.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        tk.Label(add_f, text="Arg (optional):", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=1, column=0, sticky="w", pady=4)
        self.var_arg = tk.StringVar(value="")
        self.entry_arg = tk.Entry(add_f, textvariable=self.var_arg, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, width=16)
        self.entry_arg.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        btn_add = tk.Button(add_f, text="+ Add Step", font=FONT_BOLD, bg=ACCENT_CYAN, fg="#000", relief="flat", padx=8, pady=2, command=self._add_step)
        btn_add.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 2))

        # Active Steps List
        tk.Label(left_p, text="Current Pipeline Order:", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", padx=12, pady=(12, 4))
        self.listbox_steps = tk.Listbox(left_p, bg=BG_INPUT, fg=TEXT_PRIMARY, font=FONT_CODE, height=8, bd=1, relief="solid")
        self.listbox_steps.pack(fill="x", padx=10, pady=4)

        btn_box = tk.Frame(left_p, bg=BG_CARD)
        btn_box.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_box, text="Remove Selected", font=FONT_BODY, bg=BG_DARK, fg=ACCENT_RED, relief="flat", padx=6, pady=2, command=self._remove_step).pack(side="left")
        tk.Button(btn_box, text="Clear All", font=FONT_BODY, bg=BG_DARK, fg=TEXT_MUTED, relief="flat", padx=6, pady=2, command=self._clear_steps).pack(side="right")

        # Right Panel: Live Execution Sandbox
        right_p = tk.Frame(self, bg=BG_DARK)
        right_p.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # 1. Input Box
        tk.Label(right_p, text="1. Raw Input (Plaintext / Payload Bytes):", font=FONT_SUBTITLE, fg=TEXT_PRIMARY, bg=BG_DARK).pack(anchor="w")
        self.txt_in = tk.Text(right_p, bg=BG_EDITOR, fg=TEXT_PRIMARY, font=FONT_CODE, height=4, bd=1, relief="solid", padx=8, pady=6)
        self.txt_in.pack(fill="x", pady=(2, 10))
        self.txt_in.insert("1.0", "Hello Ostad Red Team Forge! This is Beacon payload check-in data.")
        self.txt_in.bind("<KeyRelease>", lambda e: self.run_transforms())

        # 2. Transformed Result
        tk.Label(right_p, text="2. Forward Transformed Output (Wire Format):", font=FONT_SUBTITLE, fg=ACCENT_GREEN, bg=BG_DARK).pack(anchor="w")
        self.txt_out = tk.Text(right_p, bg=BG_EDITOR, fg="#81c784", font=FONT_CODE, height=5, bd=1, relief="solid", padx=8, pady=6)
        self.txt_out.pack(fill="x", pady=(2, 10))

        # 3. Reverse Decoded Result
        tk.Label(right_p, text="3. Reverse Decoded Verification (C2 Engine Recovery):", font=FONT_SUBTITLE, fg=ACCENT_CYAN, bg=BG_DARK).pack(anchor="w")
        self.txt_rev = tk.Text(right_p, bg=BG_EDITOR, fg="#80d8ff", font=FONT_CODE, height=4, bd=1, relief="solid", padx=8, pady=6)
        self.txt_rev.pack(fill="x", pady=(2, 10))

        self._refresh_listbox()
        self.run_transforms()

    def _refresh_listbox(self):
        self.listbox_steps.delete(0, "end")
        for i, (act, arg) in enumerate(self.pipeline_steps):
            display = f"{i+1}. {act} \"{arg}\"" if arg else f"{i+1}. {act}"
            self.listbox_steps.insert("end", display)

    def _add_step(self):
        act = self.var_action.get()
        arg = self.var_arg.get()
        self.pipeline_steps.append((act, arg))
        self.var_arg.set("")
        self._refresh_listbox()
        self.run_transforms()

    def _remove_step(self):
        sel = self.listbox_steps.curselection()
        if sel:
            idx = sel[0]
            del self.pipeline_steps[idx]
            self._refresh_listbox()
            self.run_transforms()

    def _clear_steps(self):
        self.pipeline_steps.clear()
        self._refresh_listbox()
        self.run_transforms()

    def run_transforms(self):
        raw_text = self.txt_in.get("1.0", "end-1c")
        raw_bytes = raw_text.encode('utf-8', errors='ignore')

        # Forward
        pipe = TransformPipeline(self.pipeline_steps)
        try:
            forward_bytes = pipe.execute(raw_bytes)
            forward_str = forward_bytes.decode('latin-1', errors='replace')
        except Exception as e:
            forward_str = f"[Transform Error]: {e}"

        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("1.0", forward_str)

        # Reverse
        try:
            recovered_bytes = pipe.reverse(forward_bytes)
            recovered_str = recovered_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            recovered_str = f"[Reverse Error]: {e}"

        self.txt_rev.delete("1.0", "end")
        self.txt_rev.insert("1.0", recovered_str)
