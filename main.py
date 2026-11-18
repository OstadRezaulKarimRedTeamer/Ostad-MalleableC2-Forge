"""
Ostad Malleable C2 Forge - Main Entry Point (Master Unified GUI & CLI)
Official Red Team & Adversary Simulation Suite by Ostad Red Team Forge.
Founder: Ostad Rezaul Karim (Top 1% Red Teamer)
"""

import sys
import os
import argparse
import ctypes
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.generator import ProfileGenerator
from backend.serializer import serialize_profile
from backend.parser import parse_profile
from backend.linter import C2Linter
from backend.traffic_sim import TrafficSimulator
from backend.detection_engine import DetectionEngine
from backend.c2_server import EmbeddedC2Server
from backend.c2_client import EmbeddedC2Client


def enable_high_dpi():
    """Enables crisp High-DPI scaling on Windows."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def run_cli(args):
    """Headless Command Line Interface."""
    print("=" * 75)
    print("🦅 OSTAD MALLEABLE C2 FORGE - MASTER ADVERSARY SIMULATION SUITE")
    print("Unified C2 Engine: Server, Client, Generator, c2lint & RoE Audit")
    print("Ostad Red Team Forge • Elite Offensive Security Edition")
    print("Founder: Ostad Rezaul Karim (Top 1% Red Teamer)")
    print("=" * 75)

    # 1. Lint Mode
    if args.lint:
        if not os.path.exists(args.lint):
            print(f"[!] Error: File '{args.lint}' not found.")
            sys.exit(1)
        with open(args.lint, "r", encoding="utf-8") as f:
            content = f.read()
        profile = parse_profile(content)
        linter = C2Linter()
        rep = linter.audit(profile)

        print(f"\n[+] Audit Report for: {args.lint}")
        print(f"[*] OPSEC Stealth Score: {rep.score}/100 [Grade: {rep.grade}]")
        print(f"[*] Critical Issues: {rep.critical_count} | Warnings: {rep.warning_count} | Passed: {len(rep.passed_rules)}")

        if rep.issues:
            print("\n[-] Findings:")
            for i in rep.issues:
                print(f"  [{i.severity}] {i.rule_id} ({i.category}): {i.message}")
                print(f"       Fix: {i.suggestion}")
        else:
            print("\n[✓] Zero OPSEC issues found! Profile operates with maximum stealth.")

        sys.exit(0)

    # 2. Generation Mode / Baseline Profile
    gen = ProfileGenerator()
    profile = gen.generate(
        template_key=args.template,
        sleeptime=args.sleep,
        jitter=args.jitter,
        evasion_level=args.evasion,
        custom_host=args.host,
        allocator=args.allocator
    )
    profile_code = serialize_profile(profile)

    # 3. Server Mode
    if args.server:
        port = args.port or 8080
        print(f"\n[*] Starting Ostad C2 Server Listener on port {port}...")
        server = EmbeddedC2Server(port=port, profile=profile, on_log_callback=print)
        if server.start():
            print(f"[✓] Ostad C2 Server listening on 0.0.0.0:{port}. Press Ctrl+C to terminate.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
                print("\n[*] Server listener stopped.")
        sys.exit(0)

    # 4. Client Mode
    if args.client:
        port = args.port or 8080
        target = args.client
        rounds = args.rounds or 5
        print(f"\n[*] Launching Ostad C2 Beacon Client targeting {target}:{port} ({rounds} rounds)...")
        client = EmbeddedC2Client(c2_endpoints=[target], port=port, profile=profile, on_log_callback=print)
        client.start(rounds=rounds)
        while client.running:
            time.sleep(0.5)
        print("[✓] Client beacon simulation completed.")
        sys.exit(0)

    # Traffic simulation output if requested
    if args.simulate:
        sim = TrafficSimulator(profile)
        req_get, resp_get = sim.simulate_get_transaction()
        req_post, resp_post = sim.simulate_post_transaction()
        print("\n--- [SIMULATED HTTP-GET CHECK-IN] ---")
        print(req_get)
        print("\n--- [SIMULATED HTTP-POST EXFILTRATION] ---")
        print(req_post)

    # Suricata output if requested
    if args.suricata:
        det = DetectionEngine(profile)
        print("\n--- [SURICATA NIDS RULES] ---")
        print(det.generate_suricata_rules())

    # YARA output if requested
    if args.yara:
        det = DetectionEngine(profile)
        print("\n--- [YARA MEMORY SIGNATURE] ---")
        print(det.generate_yara_rule())

    # Output file or stdout
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(profile_code)
        print(f"\n[✓] Polymorphic profile successfully written to: {args.output}")
    elif not (args.simulate or args.suricata or args.yara):
        print("\n" + profile_code)


def run_gui():
    """Launches the master unified desktop GUI suite."""
    enable_high_dpi()
    from ui.app import MalleableC2App
    app = MalleableC2App()
    app.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description="Ostad Malleable C2 Forge - Master Unified Red Team C2 Suite"
    )
    parser.add_argument("--cli", action="store_true", help="Run in headless CLI mode instead of GUI")
    parser.add_argument("--server", action="store_true", help="Run standalone C2 Server listener")
    parser.add_argument("--client", type=str, default=None, help="Run standalone C2 Client agent targeting HOST")
    parser.add_argument("--port", type=int, default=8080, help="Server/Client port (default: 8080)")
    parser.add_argument("--rounds", type=int, default=5, help="Number of beacon rounds for client (default: 5)")
    parser.add_argument("--template", type=str, default="amazon_cloudfront", help="Template ID (amazon_cloudfront, microsoft_onedrive, google_analytics, slack_api, cloudflare_cdn, github_api)")
    parser.add_argument("--evasion", type=str, default="stealth", choices=["standard", "stealth", "paranoid"], help="Evasion level")
    parser.add_argument("--sleep", type=int, default=5000, help="Beacon sleeptime in ms")
    parser.add_argument("--jitter", type=int, default=25, help="Beacon jitter percentage")
    parser.add_argument("--host", type=str, default=None, help="Custom Host/Domain header")
    parser.add_argument("--allocator", type=str, default="VirtualAllocEx", help="Process memory allocator")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output .profile file path")
    parser.add_argument("--lint", type=str, default=None, help="Run c2lint audit on specified .profile file")
    parser.add_argument("--simulate", action="store_true", help="Print simulated wire HTTP transactions")
    parser.add_argument("--suricata", action="store_true", help="Generate and print Suricata NIDS rules")
    parser.add_argument("--yara", action="store_true", help="Generate and print YARA rules")

    args = parser.parse_args()

    if args.cli or args.server or args.client or args.lint or args.output or args.simulate or args.suricata or args.yara:
        run_cli(args)
    else:
        run_gui()


if __name__ == "__main__":
    main()
