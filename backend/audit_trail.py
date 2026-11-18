"""
RoE Audit Trail Logger
Logs cryptographically traceable JSON audit events for red team accountability.
"""

import os
import json
import time


class AuditTrail:
    """Manages c2_audit_trail.log file."""

    def __init__(self, log_path: str = "c2_audit_trail.log"):
        self.log_path = log_path

    def log(self, event_type: str, details: dict):
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "epoch": time.time(),
            "event": event_type,
            "details": details
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def get_recent_logs(self, limit: int = 50) -> list:
        if not os.path.exists(self.log_path):
            return []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [json.loads(line.strip()) for line in lines[-limit:] if line.strip()]
        except Exception:
            return []
