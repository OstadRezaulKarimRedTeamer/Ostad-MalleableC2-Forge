"""
Live C2 Server & Multi-Session Operations Tab
Integrated Control Dashboard for Starting/Stopping Listener, Managing Sessions & Dispatching Tasks.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from backend.models import Profile
from backend.c2_server import EmbeddedC2Server
from ui.theme import (
    BG_DARK, BG_CARD, BG_EDITOR, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, FONT_SUBTITLE,
    FONT_BODY, FONT_BOLD, FONT_CODE, BORDER_COLOR
)


class ServerTab(tk.Frame):
    """Integrated Live C2 Server Management Dashboard."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.profile: Optional[Profile] = None
        self.server: Optional[EmbeddedC2Server] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Control Bar (Listener setup & metrics)
        ctrl_bar = tk.Frame(self, bg=BG_CARD, bd=1, relief="solid")
        ctrl_bar.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(ctrl_bar, text="Listen Port:", font=FONT_BOLD, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=(10, 4), pady=8)
        self.var_port = tk.StringVar(value="8080")
        self.entry_port = tk.Entry(ctrl_bar, textvariable=self.var_port, width=7, font=FONT_CODE, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.entry_port.pack(side="left", padx=4, pady=8)

        self.btn_toggle_server = tk.Button(
            ctrl_bar, text="▶ Start C2 Listener", font=FONT_BOLD, bg=ACCENT_GREEN, fg="#000",
            activebackground="#69f0ae", relief="flat", padx=14, pady=5, cursor="hand2",
            command=self._toggle_server
        )
        self.btn_toggle_server.pack(side="left", padx=10, pady=8)

        self.lbl_server_status = tk.Label(ctrl_bar, text="● STOPPED", font=FONT_BOLD, fg=ACCENT_RED, bg=BG_CARD)
        self.lbl_server_status.pack(side="left", padx=10, pady=8)

        # Metrics on right
        self.lbl_metrics = tk.Label(
            ctrl_bar,
            text="Connections: 0 | In: 0 B | Out: 0 B | Honeypot Deflects: 0 | NIDS Hits: 0",
            font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD
        )
        self.lbl_metrics.pack(side="right", padx=12, pady=8)

        # 2. Middle Paned Window (Sessions Table on top, Log Console on bottom)
        paned = tk.PanedWindow(self, orient="vertical", bg=BORDER_COLOR, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        # Top Pane: Active Sessions Table & Task Dispatcher
        top_pane = tk.Frame(paned, bg=BG_DARK)
        paned.add(top_pane, minsize=180)

        # Sessions Table Frame
        tbl_f = tk.LabelFrame(top_pane, text=" Active Beacon Sessions ", font=FONT_SUBTITLE, fg=ACCENT_CYAN, bg=BG_CARD, bd=1, relief="solid", padx=8, pady=4)
        tbl_f.pack(fill="both", expand=True, side="left", padx=(0, 5))

        cols = ("id", "remote", "entropy", "packets", "last_seen")
        self.tree_sessions = ttk.Treeview(tbl_f, columns=cols, show="headings", selectmode="browse", height=5)
        self.tree_sessions.heading("id", text="Beacon ID")
        self.tree_sessions.heading("remote", text="Remote Address")
        self.tree_sessions.heading("entropy", text="Shannon Entropy")
        self.tree_sessions.heading("packets", text="Packet Count")
        self.tree_sessions.heading("last_seen", text="Last Seen")

        self.tree_sessions.column("id", width=120, anchor="center")
        self.tree_sessions.column("remote", width=160, anchor="center")
        self.tree_sessions.column("entropy", width=120, anchor="center")
        self.tree_sessions.column("packets", width=100, anchor="center")
        self.tree_sessions.column("last_seen", width=120, anchor="center")

        scroll_s = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_sessions.yview)
        self.tree_sessions.configure(yscrollcommand=scroll_s.set)
        self.tree_sessions.pack(side="left", fill="both", expand=True)
        scroll_s.pack(side="right", fill="y")

        self.tree_sessions.bind("<<TreeviewSelect>>", self._on_session_selected)

        # Task Dispatcher Frame
        task_f = tk.LabelFrame(top_pane, text=" Operator Task Dispatcher ", font=FONT_SUBTITLE, fg=ACCENT_CYAN, bg=BG_CARD, bd=1, relief="solid", width=340, padx=10, pady=6)
        task_f.pack(fill="y", side="right", padx=(5, 0))
        task_f.pack_propagate(False)

        tk.Label(task_f, text="Target Beacon ID:", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", pady=(2, 1))
        self.var_target_beacon = tk.StringVar(value="")
        self.entry_target_beacon = tk.Entry(task_f, textvariable=self.var_target_beacon, font=FONT_CODE, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY)
        self.entry_target_beacon.pack(fill="x", pady=(0, 6))

        tk.Label(task_f, text="Command to Queue:", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", pady=(2, 1))
        self.var_task_cmd = tk.StringVar(value="SET_SLEEP 10000 30")
        self.combo_tasks = ttk.Combobox(
            task_f, textvariable=self.var_task_cmd,
            values=["SET_SLEEP 10000 30", "SET_SLEEP 3000 15", "PING", "STATUS_CHECK"],
            font=FONT_CODE
        )
        self.combo_tasks.pack(fill="x", pady=(0, 8))

        btn_dispatch = tk.Button(
            task_f, text="⚡ Queue Task to Beacon", font=FONT_BOLD, bg=ACCENT_RED, fg="white",
            activebackground="#f44336", relief="flat", padx=8, pady=4, cursor="hand2",
            command=self._dispatch_task
        )
        btn_dispatch.pack(fill="x", pady=4)

        # Bottom Pane: Live Server Console
        bot_pane = tk.Frame(paned, bg=BG_DARK)
        paned.add(bot_pane, minsize=240)

        log_hdr = tk.Frame(bot_pane, bg=BG_CARD)
        log_hdr.pack(fill="x")
        tk.Label(log_hdr, text="🖥️ Live Server Decoded Inbound Telemetry Stream", font=FONT_SUBTITLE, fg=ACCENT_GREEN, bg=BG_CARD).pack(side="left", padx=8, pady=4)

        tk.Button(log_hdr, text="Clear Console", font=FONT_BODY, bg=BG_INPUT, fg=TEXT_SECONDARY, relief="flat", padx=6, pady=2, command=self._clear_log).pack(side="right", padx=6, pady=2)

        self.txt_log = tk.Text(bot_pane, bg=BG_EDITOR, fg="#e0e0e0", font=FONT_CODE, bd=0, padx=8, pady=8)
        scroll_l = ttk.Scrollbar(bot_pane, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=scroll_l.set)

        self.txt_log.pack(side="left", fill="both", expand=True)
        scroll_l.pack(side="right", fill="y")

    def set_profile(self, profile: Profile):
        self.profile = profile
        if self.server and self.server.running:
            self.server.update_profile(profile)

    def _toggle_server(self):
        if self.server and self.server.running:
            self.server.stop()
            self.btn_toggle_server.config(text="▶ Start C2 Listener", bg=ACCENT_GREEN)
            self.lbl_server_status.config(text="● STOPPED", fg=ACCENT_RED)
            self.entry_port.config(state="normal")
        else:
            if not self.profile:
                messagebox.showerror("Error", "No profile loaded.")
                return
            try:
                port = int(self.var_port.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid port number.")
                return

            self.server = EmbeddedC2Server(
                port=port,
                profile=self.profile,
                on_log_callback=self._append_log_threadsafe,
                on_session_update_callback=self._update_sessions_threadsafe
            )
            if self.server.start():
                self.btn_toggle_server.config(text="⏹ Stop C2 Listener", bg=ACCENT_RED)
                self.lbl_server_status.config(text=f"● RUNNING (Port {port})", fg=ACCENT_GREEN)
                self.entry_port.config(state="disabled")

    def _append_log_threadsafe(self, msg: str):
        self.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg: str):
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self._refresh_metrics()

    def _update_sessions_threadsafe(self, sessions_dict: Dict[str, Any]):
        self.after(0, lambda: self._update_sessions_table(sessions_dict))

    def _update_sessions_table(self, sessions_dict: Dict[str, Any]):
        self.tree_sessions.delete(*self.tree_sessions.get_children())
        for bid, s in sessions_dict.items():
            self.tree_sessions.insert("", "end", values=(
                s.get("id", bid),
                f"{s.get('ip', '')}:{s.get('port', '')}",
                s.get("entropy", 0.0),
                s.get("packets", 0),
                s.get("last_seen", "")
            ))

    def _on_session_selected(self, event):
        sel = self.tree_sessions.selection()
        if sel:
            item = self.tree_sessions.item(sel[0])
            bid = item["values"][0]
            self.var_target_beacon.set(str(bid))

    def _dispatch_task(self):
        bid = self.var_target_beacon.get().strip()
        cmd = self.var_task_cmd.get().strip()
        if not bid:
            messagebox.showwarning("Warning", "Please select or enter a Target Beacon ID.")
            return
        if not cmd:
            messagebox.showwarning("Warning", "Please enter a command to queue.")
            return

        if self.server and self.server.running:
            self.server.queue_task(bid, cmd)
        else:
            messagebox.showwarning("Warning", "C2 Server Listener is not running.")

    def _refresh_metrics(self):
        if self.server:
            m = self.server.metrics
            self.lbl_metrics.config(
                text=f"Connections: {m['total_connections']} | In: {m['total_bytes_in']} B | Out: {m['total_bytes_out']} B | Honeypot Deflects: {m['honeypot_redirects']} | NIDS Hits: {m['nids_alerts']}"
            )

    def _clear_log(self):
        self.txt_log.delete("1.0", "end")
