# Ostad Malleable C2 Forge - Master Unified Dashboard 🦅
### Polymorphic C2 Profile Engine, C2 Server/Agent, OPSEC Linter & RoE Audit Platform
#### Official Adversary Simulation & Purple Team Platform by Ostad Red Team Forge
#### Founder: Ostad Rezaul Karim (Top 1% Red Teamer • Cybersecurity Expert)

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20%7C%20Linux-0078D7?style=for-the-badge&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/Security-Red%20Team%20%26%20Purple%20Team-red?style=for-the-badge&logo=hackthebox&logoColor=white" alt="Security" />
  <img src="https://img.shields.io/badge/Version-5.0%20Master%20Edition-black?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/Ostad%20Red%20Team%20Forge-Official%20Release-990000?style=for-the-badge" alt="Forge" />
</p>

---

## 🦅 About Ostad Red Team Forge

**Ostad Red Team Forge** is an elite cybersecurity research, adversary simulation, and defensive purple-team collective founded by **Ostad Rezaul Karim**.

> **Founder & Director:** **Ostad Rezaul Karim**  
> **Global Ranking & Profile:** **Top 1% Red Teamer • Cybersecurity Expert**  
> **Core Disciplines:** Advanced Penetration Testing • Red Teaming & RoE Operations • Exploit & C2 Tool Engineering • Purple Team Detection Engineering  

**Ostad Malleable C2 Forge** synthesizes all core offensive and defensive C2 components into a single **Master Unified Dashboard**:
1. **Live C2 Server Listener** (Session tracking, Task dispatching, Honeypot redirection, NIDS alert simulation)
2. **Live C2 Client Agent** (Simulated Beacon agent with route cycling, Gaussian jitter, HTTP transactions)
3. **Polymorphic Generator** (CDN templates, SourcePoint & C2concealer inspired evasion)
4. **AST Source Editor** (Full Malleable C2 syntax highlighting and bidirectional sync)
5. **Traffic Simulator** (Wire inspection of simulated HTTP-GET and HTTP-POST packets)
6. **OPSEC Audit (c2lint)** (25+ automated OPSEC stealth checks with 0-100% scoring)
7. **Detection Engine (RoE)** (Suricata, Snort, and YARA rule generators)
8. **Transform Sandbox** (Real-time testing of netbios, base64url, mask, xor, prepend/append)
9. **MITRE ATT&CK & RoE Audit Trail** (Technique alignment & SHA-256 hashed audit events)

---

## ⚡ Master Unified Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        OSTAD MALLEABLE C2 FORGE - MASTER UNIFIED DASHBOARD                             │
├───────────────────────────────────┬───────────────────────────────────┬────────────────────────────────┤
│ 🖥️ 1. Live C2 Server Listener     │ 🚀 2. Live C2 Client Agent        │ 🧙 3. Polymorphic Generator    │
│ • Winsock/Socket HTTP Daemon      │ • Simulated Beacon Agent          │ • High-Reputation Templates    │
│ • Multi-Session Tracking Table    │ • Egress Multi-Route Cycling      │ • EDR Evasion Stacks           │
│ • Task Queue Dispatcher           │ • Gaussian Jitter Simulator       │ • Random User-Agents & URIs    │
│ • Active Honeypot Redirection     │ • Live Wire Packet Logger         │ • Header & Cookie Shapers      │
├───────────────────────────────────┼───────────────────────────────────┼────────────────────────────────┤
│ 📝 4. AST Profile Source Editor   │ 🌐 5. Traffic Flow Simulator      │ 🛡️ 6. OPSEC Audit (c2lint)     │
│ • Syntax Highlighting             │ • Wire-level HTTP Inspection      │ • 25+ OPSEC Evasion Rules      │
│ • Full Grammar Validation         │ • GET Check-in Frames             │ • Memory RWX Flags Detection   │
│ • Live Re-parsing Engine          │ • POST Exfiltration Frames        │ • OPSEC Score & Letter Grade   │
├───────────────────────────────────┼───────────────────────────────────┼────────────────────────────────┤
│ 🎯 7. Detection Rules (RoE)       │ 🧪 8. Transform Sandbox           │ ⚔️ 9. MITRE & Audit Trail      │
│ • Suricata NIDS Rule Export       │ • NetBIOS, Base64URL, XOR, Mask   │ • MITRE ATT&CK Matrix Alignment│
│ • Snort NIDS Signatures           │ • Step-by-step Pipeline Testing   │ • SHA-256 Cryptographic RoE Log│
│ • In-Memory YARA Signatures       │ • Shannon Entropy Calculator      │ • Live Operator Audit Viewer   │
└───────────────────────────────────┴───────────────────────────────────┴────────────────────────────────┘
```

---

## 🚀 Quick Start & Launching

### Option A: 1-Click Launch (Standalone EXE)
Double-click `Launch_OstadMalleableC2_Master.bat` located in `All Clone Tools\`:
```cmd
Launch_OstadMalleableC2_Master.bat
```
Direct executable location:
```
MalleableC2\dist\OstadMalleableC2\OstadMalleableC2.exe
```

### Option B: Run via Python
```cmd
cd MalleableC2
python main.py
```

### Option C: CLI Mode
```cmd
# Start C2 Server listener on port 8080:
python main.py --server --port 8080

# Run simulated C2 client beacon targeting localhost:
python main.py --client 127.0.0.1 --port 8080 --rounds 5

# Run OPSEC c2lint audit on profile:
python main.py --lint profiles/amazon_cloudfront.profile

# View simulated network wire transactions:
python main.py --simulate
```

---

## 📁 Repository Structure

```
All Clone Tools/
├── Launch_OstadMalleableC2_Master.bat       # Master 1-Click Launcher
├── MalleableC2/                            # Python Master Unified GUI & Backend Suite
│   ├── main.py                             # Unified Main Entry Point (GUI & CLI)
│   ├── run.bat                             # Python launcher script
│   ├── build_exe.bat                       # Standalone PyInstaller build script
│   ├── dist/OstadMalleableC2/              # Compiled Standalone Executable (.exe)
│   ├── backend/
│   │   ├── c2_server.py                    # Multi-threaded C2 Server Daemon
│   │   ├── c2_client.py                    # Beacon Agent with route cycling & jitter
│   │   ├── generator.py                    # Polymorphic Profile Generator
│   │   ├── linter.py                       # c2lint Replica (25+ OPSEC rules)
│   │   ├── parser.py                       # Malleable C2 Lexer & AST Parser
│   │   ├── serializer.py                   # Profile serialization engine
│   │   ├── traffic_sim.py                  # Wire HTTP traffic generator
│   │   ├── detection_engine.py             # Suricata, Snort & YARA rule generator
│   │   ├── transforms.py                   # NetBIOS, Base64, XOR, Mask algorithms
│   │   ├── mitre_mapper.py                 # MITRE ATT&CK alignment mapper
│   │   ├── audit_trail.py                  # Cryptographic RoE event logging
│   │   ├── templates.py                    # Pre-built enterprise profile templates
│   │   └── wordlists.py                    # Real-world URI & header catalogs
│   ├── ui/
│   │   ├── app.py                          # Master Unified Application Window
│   │   ├── theme.py                        # Modern Cyberpunk/Matrix Dark Theme
│   │   └── tabs/
│   │       ├── server_tab.py               # 🖥️ Live C2 Server & Sessions Tab
│   │       ├── client_tab.py               # 🚀 Live C2 Client Beacon Tab
│   │       ├── generator_tab.py            # 🧙 Polymorphic Generator Tab
│   │       ├── editor_tab.py               # 📝 Profile Source Editor Tab
│   │       ├── traffic_tab.py              # 🌐 Traffic Flow Simulator Tab
│   │       ├── linter_tab.py               # 🛡️ OPSEC Audit (c2lint) Tab
│   │       ├── detection_tab.py            # 🎯 Detection Rules (RoE) Tab
│   │       ├── transform_tab.py            # 🧪 Transform Sandbox Tab
│   │       └── mitre_tab.py                # ⚔️ MITRE & Audit Trail Tab
│   └── profiles/                           # Preset .profile files
└── MalleableC2_CPP/                        # Native C++17 Header Library & Standalone Binaries
    ├── include/                            # Complete C++17 Header Library
    ├── server/                             # Standalone Native C2 Server (Winsock2)
    ├── client/                             # Standalone Native C2 Client (Winsock2)
    ├── src/                                # Native C++ Workbench CLI
    ├── build_server.bat                    # Server build script
    └── build_client.bat                    # Client build script
```

---

## 🛡️ RoE & Legal Disclaimer

This tool is strictly intended for **authorized red teaming**, **purple teaming**, and **adversary emulation operations** within agreed Rules of Engagement (RoE). It is developed for cybersecurity researchers and defensive engineers to audit evasion resilience and build robust network detection signatures.
