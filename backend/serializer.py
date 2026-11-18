"""
Malleable C2 AST Serializer
Converts a Profile object into formatted, valid Malleable C2 DSL text.
"""

from typing import List
from backend.models import (
    Profile, HttpTransaction, ClientSubBlock, ServerSubBlock,
    TransformBlock, TransformAction, TerminationAction
)


def _serialize_transform_block(name: str, tb: TransformBlock, indent: str = "        ") -> str:
    lines = [f"{indent}{name} {{"]
    for t in tb.transforms:
        if t.action in ("prepend", "append"):
            escaped_arg = t.arg.replace('"', '\\"')
            lines.append(f"{indent}    {t.action} \"{escaped_arg}\";")
        else:
            lines.append(f"{indent}    {t.action};")

    if tb.termination:
        target = tb.termination.target
        val = tb.termination.name
        if target == "print":
            lines.append(f"{indent}    print;")
        elif target == "header":
            lines.append(f"{indent}    header \"{val}\";")
        elif target == "parameter":
            lines.append(f"{indent}    parameter \"{val}\";")
        elif target == "uri-append":
            lines.append(f"{indent}    uri-append;")
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _serialize_client(client: ClientSubBlock, indent: str = "    ") -> str:
    lines = [f"{indent}client {{"]
    for h in client.headers:
        lines.append(f"{indent}    header \"{h.name}\" \"{h.value}\";")
    for p in client.parameters:
        lines.append(f"{indent}    parameter \"{p.name}\" \"{p.value}\";")

    for tb_name, tb in client.transform_blocks.items():
        lines.append(_serialize_transform_block(tb_name, tb, indent + "    "))

    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _serialize_server(server: ServerSubBlock, indent: str = "    ") -> str:
    lines = [f"{indent}server {{"]
    for h in server.headers:
        lines.append(f"{indent}    header \"{h.name}\" \"{h.value}\";")

    if server.output:
        lines.append(_serialize_transform_block("output", server.output, indent + "    "))

    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _serialize_http_transaction(verb_block: str, tx: HttpTransaction) -> str:
    lines = [f"{verb_block} {{"]
    if tx.uris:
        uri_str = " ".join(f'"{u}"' for u in tx.uris) if len(tx.uris) > 1 else f'"{tx.uris[0]}"'
        lines.append(f"    set uri {uri_str};")
    if tx.verb != "GET":
        lines.append(f"    set verb \"{tx.verb}\";")

    lines.append("")
    lines.append(_serialize_client(tx.client, "    "))
    lines.append("")
    lines.append(_serialize_server(tx.server, "    "))
    lines.append("}")
    return "\n".join(lines)


def serialize_profile(profile: Profile) -> str:
    """Serializes a complete Profile AST to a standard .profile string."""
    out = [
        f"# =====================================================================",
        f"# Profile: {profile.name}",
        f"# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine",
        f"# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)",
        f"# =====================================================================\n",
        f"set sample_name \"{profile.sample_name}\";",
        f"set sleeptime \"{profile.sleeptime}\";",
        f"set jitter \"{profile.jitter}\";",
        f"set maxget \"1048576\";",
        f"set data_jitter \"{profile.data_jitter}\";",
        f"set useragent \"{profile.useragent}\";",
        f"set pipename \"{profile.pipename}\";",
        f"set pipename_stager \"{profile.pipename_stager}\";\n"
    ]

    # Additional global settings
    for k, v in profile.global_settings.items():
        if isinstance(v, bool):
            val_str = "true" if v else "false"
        else:
            val_str = str(v)
        out.append(f"set {k} \"{val_str}\";")

    out.append("")
    # HTTP-GET
    out.append(_serialize_http_transaction("http-get", profile.http_get))
    out.append("")

    # HTTP-POST
    out.append(_serialize_http_transaction("http-post", profile.http_post))
    out.append("")

    # HTTP-STAGER if present
    if profile.http_stager:
        out.append(_serialize_http_transaction("http-stager", profile.http_stager))
        out.append("")

    # STAGE Block
    s = profile.stage
    stage_lines = [
        "stage {",
        f"    set checksum \"{s.checksum}\";",
        f"    set cleanup \"{'true' if s.cleanup else 'false'}\";",
        f"    set sleep_mask \"{'true' if s.sleep_mask else 'false'}\";",
        f"    set smartinject \"{'true' if s.smartinject else 'false'}\";",
        f"    set stomppe \"{'true' if s.stomppe else 'false'}\";",
        f"    set obfuscate \"{'true' if s.obfuscate else 'false'}\";",
        f"    set userwx \"{'true' if s.userwx else 'false'}\";",
        f"    set magic_mz_x86 \"{s.magic_mz_x86}\";",
        f"    set magic_mz_x64 \"{s.magic_mz_x64}\";",
        f"    set magic_pe \"{s.magic_pe}\";"
    ]
    if s.compile_time:
        stage_lines.append(f"    set compile_time \"{s.compile_time}\";")
    if s.transform_x86_prepend:
        stage_lines.append(f"    transform-x86 {{\n        prepend \"{s.transform_x86_prepend}\";\n    }}")
    if s.transform_x64_prepend:
        stage_lines.append(f"    transform-x64 {{\n        prepend \"{s.transform_x64_prepend}\";\n    }}")
    stage_lines.append("}")
    out.append("\n".join(stage_lines))
    out.append("")

    # PROCESS-INJECT Block
    pi = profile.process_inject
    pi_lines = [
        "process-inject {",
        f"    set allocator \"{pi.allocator}\";",
        f"    set min_alloc \"{pi.min_alloc}\";",
        f"    set startrwx \"{'true' if pi.startrwx else 'false'}\";",
        f"    set userwx \"{'true' if pi.userwx else 'false'}\";",
        "    execute {"
    ]
    for exe in pi.execute_order:
        pi_lines.append(f"        {exe};")
    pi_lines.append("    }")
    pi_lines.append("}")
    out.append("\n".join(pi_lines))
    out.append("")

    # POST-EX Block
    pe = profile.post_ex
    pe_lines = [
        "post-ex {",
        f"    set spawnto_x86 \"{pe.spawnto_x86}\";",
        f"    set spawnto_x64 \"{pe.spawnto_x64}\";",
        f"    set amsi_disable \"{'true' if pe.amsi_disable else 'false'}\";",
        f"    set keylogger \"{pe.keylogger}\";",
        "}"
    ]
    out.append("\n".join(pe_lines))
    out.append("")

    # HTTPS-CERTIFICATE Block
    c = profile.https_cert
    cert_lines = [
        "https-certificate {",
        f"    set CN \"{c.CN}\";",
        f"    set O \"{c.O}\";",
        f"    set OU \"{c.OU}\";",
        f"    set C \"{c.C}\";",
        f"    set ST \"{c.ST}\";",
        f"    set L \"{c.L}\";",
        f"    set validity \"{c.validity}\";",
        "}"
    ]
    out.append("\n".join(cert_lines))
    out.append("")

    return "\n".join(out)
