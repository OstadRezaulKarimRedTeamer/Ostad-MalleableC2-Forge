"""
Live Malleable C2 Profile Editor & Syntax View Tab
Provides high-fidelity syntax highlighting, line numbering, and editing for .profile files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from typing import Callable, Optional
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_RED, ACCENT_CYAN, ACCENT_GREEN, ACCENT_AMBER, FONT_CODE, FONT_CODE_BOLD,
    FONT_BOLD, FONT_BODY, BORDER_COLOR
)


class EditorTab(tk.Frame):
    """Profile Source Code Editor with syntax highlighting."""

    def __init__(self, parent, on_profile_changed_callback: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=BG_DARK)
        self.on_profile_changed = on_profile_changed_callback

        self._build_ui()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        btn_load = tk.Button(
            toolbar, text="📂 Open Profile...", font=FONT_BOLD, bg=BG_DARK, fg=TEXT_PRIMARY,
            activebackground=BG_CARD, relief="flat", padx=10, pady=4, command=self._load_file
        )
        btn_load.pack(side="left", padx=5, pady=5)

        btn_save = tk.Button(
            toolbar, text="💾 Save .profile", font=FONT_BOLD, bg=ACCENT_RED, fg="white",
            activebackground="#c62828", relief="flat", padx=10, pady=4, command=self._save_file
        )
        btn_save.pack(side="left", padx=5, pady=5)

        btn_copy = tk.Button(
            toolbar, text="📋 Copy All", font=FONT_BODY, bg=BG_DARK, fg=TEXT_PRIMARY,
            activebackground=BG_CARD, relief="flat", padx=10, pady=4, command=self._copy_all
        )
        btn_copy.pack(side="left", padx=5, pady=5)

        btn_highlight = tk.Button(
            toolbar, text="🎨 Re-Highlight", font=FONT_BODY, bg=BG_DARK, fg=ACCENT_CYAN,
            activebackground=BG_CARD, relief="flat", padx=10, pady=4, command=self.highlight_syntax
        )
        btn_highlight.pack(side="left", padx=5, pady=5)

        self.lbl_stats = tk.Label(toolbar, text="Lines: 0 | Chars: 0", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD)
        self.lbl_stats.pack(side="right", padx=10)

        # Editor frame (with line numbers)
        edit_container = tk.Frame(self, bg=BORDER_COLOR, bd=1)
        edit_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Line numbers
        self.line_numbers = tk.Text(
            edit_container, width=5, bg="#08080a", fg="#4a4a5a",
            font=FONT_CODE, bd=0, padx=5, pady=5, state="disabled", takefocus=False
        )
        self.line_numbers.pack(side="left", fill="y")

        # Scrollbar
        scroll_y = ttk.Scrollbar(edit_container, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        # Text widget
        self.text_editor = tk.Text(
            edit_container, bg=BG_EDITOR, fg=TEXT_PRIMARY,
            insertbackground=ACCENT_CYAN, font=FONT_CODE, bd=0, padx=8, pady=5,
            wrap="none", undo=True, yscrollcommand=self._on_scroll_text
        )
        self.text_editor.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self._on_scroll_both)

        # Syntax tags
        self.text_editor.tag_configure("comment", foreground="#607d8b", font=FONT_CODE)
        self.text_editor.tag_configure("keyword", foreground="#ff5252", font=FONT_CODE_BOLD)
        self.text_editor.tag_configure("block_header", foreground="#00e5ff", font=FONT_CODE_BOLD)
        self.text_editor.tag_configure("string", foreground="#a5d6a7", font=FONT_CODE)
        self.text_editor.tag_configure("transform", foreground="#ffd54f", font=FONT_CODE_BOLD)
        self.text_editor.tag_configure("variable", foreground="#80d8ff", font=FONT_CODE)

        # Bind events
        self.text_editor.bind("<KeyRelease>", self._on_key_release)

    def _on_scroll_text(self, *args):
        self.line_numbers.yview_moveto(args[0])
        # Return for normal scrollbar
        return

    def _on_scroll_both(self, *args):
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_key_release(self, event=None):
        self._update_line_numbers()
        self.highlight_syntax()
        if self.on_profile_changed:
            self.on_profile_changed(self.get_content())

    def _update_line_numbers(self):
        lines = int(self.text_editor.index("end-1c").split(".")[0])
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        num_str = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert("1.0", num_str)
        self.line_numbers.config(state="disabled")

        chars = len(self.text_editor.get("1.0", "end-1c"))
        self.lbl_stats.config(text=f"Lines: {lines} | Chars: {chars}")

    def set_content(self, content: str):
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)
        self._update_line_numbers()
        self.highlight_syntax()

    def get_content(self) -> str:
        return self.text_editor.get("1.0", "end-1c")

    def highlight_syntax(self):
        content = self.get_content()

        # Clear existing tags
        for tag in ["comment", "keyword", "block_header", "string", "transform", "variable"]:
            self.text_editor.tag_remove(tag, "1.0", "end")

        # 1. Comments: #.*
        for m in re.finditer(r"#.*$", content, re.MULTILINE):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.text_editor.tag_add("comment", start, end)

        # 2. Strings: ".*?"
        for m in re.finditer(r'"(?:\\.|[^"\\])*"', content):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.text_editor.tag_add("string", start, end)

        # 3. Block headers
        blocks = r"\b(http-get|http-post|http-stager|client|server|stage|process-inject|post-ex|https-certificate|metadata|id|output|transform-x86|transform-x64|execute)\b"
        for m in re.finditer(blocks, content):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.text_editor.tag_add("block_header", start, end)

        # 4. Keywords
        keywords = r"\b(set|header|parameter|uri|verb|print|uri-append)\b"
        for m in re.finditer(keywords, content):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.text_editor.tag_add("keyword", start, end)

        # 5. Transforms
        transforms = r"\b(mask|base64|base64url|netbios|netbiosu|prepend|append)\b"
        for m in re.finditer(transforms, content):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.text_editor.tag_add("transform", start, end)

    def _save_file(self):
        fpath = filedialog.asksaveasfilename(
            defaultextension=".profile",
            filetypes=[("Malleable C2 Profile", "*.profile"), ("All Files", "*.*")]
        )
        if fpath:
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(self.get_content())
                messagebox.showinfo("Profile Saved", f"Successfully saved profile to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def _load_file(self):
        fpath = filedialog.askopenfilename(
            filetypes=[("Malleable C2 Profile", "*.profile"), ("All Files", "*.*")]
        )
        if fpath:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.set_content(content)
                if self.on_profile_changed:
                    self.on_profile_changed(content)
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

    def _copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.get_content())
        messagebox.showinfo("Copied", "Full profile source copied to clipboard!")
