"""
MITRE ATT&CK Matrix Technique Mapping Engine
Maps Malleable C2 parameters and network behaviors to standard MITRE techniques.
"""

from typing import List, Dict


MITRE_TECHNIQUES = [
    {
        "id": "T1071.001",
        "name": "Application Layer Protocol: Web Protocols",
        "tactic": "Command and Control",
        "description": "Adversaries communicate using application layer protocols (HTTP/HTTPS) to blend in with network traffic.",
        "component": "http-get, http-post, useragent"
    },
    {
        "id": "T1001.003",
        "name": "Data Obfuscation: Protocol Impersonation",
        "tactic": "Command and Control",
        "description": "Impersonates legitimate SaaS/CDN services (Amazon CloudFront, OneDrive, Slack, GA4, Cloudflare).",
        "component": "Service Templates, Headers, URIs"
    },
    {
        "id": "T1573.002",
        "name": "Encrypted Channel: Asymmetric Cryptography & Masking",
        "tactic": "Command and Control",
        "description": "Employs XOR masking with dynamic keys, Base64URL, and TLS certificates to conceal data.",
        "component": "metadata transform, mask, base64url"
    },
    {
        "id": "T1029",
        "name": "Scheduled Transfer",
        "tactic": "Command and Control",
        "description": "Leverages heartbeat sleeptime and Gaussian/Normal jitter to randomize check-in intervals.",
        "component": "sleeptime, jitter, data_jitter"
    },
    {
        "id": "T1027",
        "name": "Obfuscated Files or Information",
        "tactic": "Defense Evasion",
        "description": "Encrypts in-memory Beacon payload with Sleep Mask and stomps PE/DOS headers.",
        "component": "stage.sleep_mask, stage.stomppe, magic_mz"
    },
    {
        "id": "T1090.004",
        "name": "Proxy: Domain Fronting",
        "tactic": "Command and Control",
        "description": "Disguises backend destination using distinct Host header against CDN edge endpoints.",
        "component": "Host header, X-Forwarded-For"
    },
    {
        "id": "T1055",
        "name": "Process Injection",
        "tactic": "Privilege Escalation / Evasion",
        "description": "Injects beacon code into remote processes using VirtualAllocEx or NtMapViewOfSection without RWX permissions.",
        "component": "process-inject, allocator, userwx=false"
    }
]


def get_mitre_mapping() -> List[Dict[str, str]]:
    return MITRE_TECHNIQUES
