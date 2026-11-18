"""
Malleable C2 Traffic Flow & HTTP Packet Stream Simulator
Simulates live HTTP/S transactions based on the active profile configuration,
providing Wireshark/Fiddler-level inspection of Beacon and C2 Server communications.
"""

from typing import Dict, Tuple
from backend.models import Profile, TransformBlock
from backend.transforms import TransformPipeline


def _build_pipeline(tb: TransformBlock) -> TransformPipeline:
    pipe = TransformPipeline()
    for t in tb.transforms:
        pipe.add_step(t.action, t.arg)
    return pipe


class TrafficSimulator:
    """Generates wire-accurate raw HTTP requests and responses for a given Profile."""

    def __init__(self, profile: Profile):
        self.profile = profile

    def simulate_get_transaction(self, mock_metadata: bytes = b"BEACON_HEARTBEAT:x64:CORP-PC\\Administrator") -> Tuple[str, str]:
        """
        Simulates HTTP-GET (Beacon checking in for tasking).
        Returns (raw_request, raw_response).
        """
        p = self.profile
        tx = p.http_get

        # 1. Process client metadata transform
        uri = tx.uris[0] if tx.uris else "/api/v1/sync"
        meta_block = tx.client.transform_blocks.get("metadata")

        headers_dict: Dict[str, str] = {}
        # User-Agent
        headers_dict["User-Agent"] = p.useragent

        for h in tx.client.headers:
            headers_dict[h.name] = h.value

        query_params = []
        for param in tx.client.parameters:
            query_params.append(f"{param.name}={param.value}")

        body = ""

        if meta_block:
            pipe = _build_pipeline(meta_block)
            transformed_bytes = pipe.execute(mock_metadata)
            transformed_str = transformed_bytes.decode('latin-1', errors='ignore')

            if meta_block.termination:
                target = meta_block.termination.target
                t_name = meta_block.termination.name

                if target == "header":
                    if t_name.lower() == "cookie" and "Cookie" in headers_dict:
                        headers_dict["Cookie"] += f"; {transformed_str}"
                    else:
                        headers_dict[t_name] = transformed_str
                elif target == "parameter":
                    query_params.append(f"{t_name}={transformed_str}")
                elif target == "uri-append":
                    uri = uri.rstrip('/') + '/' + transformed_str.lstrip('/')
                elif target == "print":
                    body = transformed_str

        # Build full URI
        full_uri = uri
        if query_params:
            delimiter = "&" if "?" in full_uri else "?"
            full_uri += delimiter + "&".join(query_params)

        # Build Raw Request String
        req_lines = [f"{tx.verb} {full_uri} HTTP/1.1"]
        for k, v in headers_dict.items():
            req_lines.append(f"{k}: {v}")
        req_lines.append("Connection: keep-alive")
        req_lines.append("")
        if body:
            req_lines.append(body)
        raw_request = "\r\n".join(req_lines)

        # 2. Process server response (C2 server tasking)
        mock_tasking = b"TASK:102:shell whoami /all"
        resp_headers: Dict[str, str] = {}
        for h in tx.server.headers:
            resp_headers[h.name] = h.value

        resp_body = ""
        if tx.server.output:
            pipe_srv = _build_pipeline(tx.server.output)
            trans_srv = pipe_srv.execute(mock_tasking)
            resp_body = trans_srv.decode('latin-1', errors='ignore')

        resp_headers["Content-Length"] = str(len(resp_body))

        resp_lines = [
            "HTTP/1.1 200 OK"
        ]
        for k, v in resp_headers.items():
            resp_lines.append(f"{k}: {v}")
        resp_lines.append("Connection: keep-alive")
        resp_lines.append("")
        resp_lines.append(resp_body)
        raw_response = "\r\n".join(resp_lines)

        return raw_request, raw_response

    def simulate_post_transaction(
        self,
        mock_id: bytes = b"982143",
        mock_output: bytes = b"NT AUTHORITY\\SYSTEM\r\nPrivileges: SeDebugPrivilege Enabled"
    ) -> Tuple[str, str]:
        """
        Simulates HTTP-POST (Beacon exfiltrating task execution results).
        Returns (raw_request, raw_response).
        """
        p = self.profile
        tx = p.http_post

        uri = tx.uris[0] if tx.uris else "/api/v1/report"
        headers_dict: Dict[str, str] = {}
        headers_dict["User-Agent"] = p.useragent
        for h in tx.client.headers:
            headers_dict[h.name] = h.value

        query_params = []
        for param in tx.client.parameters:
            query_params.append(f"{param.name}={param.value}")

        body = ""

        # Process ID block
        id_block = tx.client.transform_blocks.get("id")
        if id_block:
            pipe_id = _build_pipeline(id_block)
            id_trans = pipe_id.execute(mock_id).decode('latin-1', errors='ignore')
            if id_block.termination:
                if id_block.termination.target == "header":
                    headers_dict[id_block.termination.name] = id_trans
                elif id_block.termination.target == "parameter":
                    query_params.append(f"{id_block.termination.name}={id_trans}")

        # Process Output block (the payload being exfiltrated)
        out_block = tx.client.transform_blocks.get("output")
        if out_block:
            pipe_out = _build_pipeline(out_block)
            out_trans = pipe_out.execute(mock_output).decode('latin-1', errors='ignore')
            if out_block.termination and out_block.termination.target == "print":
                body = out_trans
            elif out_block.termination and out_block.termination.target == "header":
                headers_dict[out_block.termination.name] = out_trans

        # Build full URI
        full_uri = uri
        if query_params:
            delimiter = "&" if "?" in full_uri else "?"
            full_uri += delimiter + "&".join(query_params)

        headers_dict["Content-Length"] = str(len(body))

        # Raw Request
        req_lines = [f"{tx.verb} {full_uri} HTTP/1.1"]
        for k, v in headers_dict.items():
            req_lines.append(f"{k}: {v}")
        req_lines.append("Connection: keep-alive")
        req_lines.append("")
        if body:
            req_lines.append(body)
        raw_request = "\r\n".join(req_lines)

        # Server Response
        resp_headers: Dict[str, str] = {}
        for h in tx.server.headers:
            resp_headers[h.name] = h.value

        resp_body = '{"status": "received", "code": 200}'
        if tx.server.output:
            pipe_srv = _build_pipeline(tx.server.output)
            trans_srv = pipe_srv.execute(b"ACK:200")
            resp_body = trans_srv.decode('latin-1', errors='ignore')

        resp_headers["Content-Length"] = str(len(resp_body))

        resp_lines = [
            "HTTP/1.1 200 OK"
        ]
        for k, v in resp_headers.items():
            resp_lines.append(f"{k}: {v}")
        resp_lines.append("Connection: keep-alive")
        resp_lines.append("")
        resp_lines.append(resp_body)
        raw_response = "\r\n".join(resp_lines)

        return raw_request, raw_response
