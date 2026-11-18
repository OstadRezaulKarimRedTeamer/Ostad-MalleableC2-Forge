"""
Malleable C2 Pre-built Industry Profile Templates
"""

import os
from typing import Dict, List
from backend.generator import ProfileGenerator
from backend.serializer import serialize_profile
from backend.models import Profile


TEMPLATES_META = [
    {
        "id": "amazon_cloudfront",
        "name": "Amazon CloudFront CDN",
        "description": "High-throughput static media & manifest delivery with CloudFront headers.",
        "icon": "☁️"
    },
    {
        "id": "microsoft_onedrive",
        "name": "Microsoft 365 / OneDrive",
        "description": "Enterprise Graph API and OneDrive delta synchronization emulation.",
        "icon": "📁"
    },
    {
        "id": "google_analytics",
        "name": "Google Analytics (GA4 / GTM)",
        "description": "Disguises heartbeats inside gtag telemetry pings and measurement protocol.",
        "icon": "📊"
    },
    {
        "id": "slack_api",
        "name": "Slack Enterprise Webhooks",
        "description": "Blends into Slack workspace polling and real-time messaging traffic.",
        "icon": "💬"
    },
    {
        "id": "cloudflare_cdn",
        "name": "Cloudflare Edge Workers",
        "description": "Edge worker cache emulation with CF-Ray IDs and security headers.",
        "icon": "🛡️"
    },
    {
        "id": "github_api",
        "name": "GitHub REST API v3",
        "description": "Simulates developer activity, git commit checks, and webhook telemetry.",
        "icon": "🐙"
    }
]


def generate_reference_profiles(output_dir: str):
    """Generates all default .profile files into the profiles directory."""
    os.makedirs(output_dir, exist_ok=True)
    gen = ProfileGenerator()
    for t in TEMPLATES_META:
        tid = t["id"]
        profile = gen.generate(template_key=tid, evasion_level="stealth")
        content = serialize_profile(profile)
        path = os.path.join(output_dir, f"{tid}.profile")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def load_template_profile(template_id: str, profiles_dir: str) -> str:
    """Loads a pre-generated template profile string or generates it on the fly."""
    path = os.path.join(profiles_dir, f"{template_id}.profile")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # Generate on the fly
    gen = ProfileGenerator()
    profile = gen.generate(template_key=template_id, evasion_level="stealth")
    return serialize_profile(profile)
