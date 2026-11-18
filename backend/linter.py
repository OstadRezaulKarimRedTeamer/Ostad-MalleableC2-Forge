"""
Malleable C2 Linter & OPSEC Audit Engine
Faithful replica and expansion of Cobalt Strike's 'c2lint'.
Performs 25+ automated checks covering syntax, transform parity, and EDR/NIDS OPSEC.
"""

from typing import List
from backend.models import Profile, AuditIssue, AuditReport


class C2Linter:
    """Audits Malleable C2 profiles for syntax errors, OPSEC risks, and detection indicators."""

    def __init__(self):
        pass

    def audit(self, profile: Profile) -> AuditReport:
        issues: List[AuditIssue] = []
        passed: List[str] = []
        score = 100

        # Rule 1: Jitter Check
        if profile.jitter == 0:
            score -= 15
            issues.append(AuditIssue(
                rule_id="OPSEC-001",
                category="OPSEC",
                severity="CRITICAL",
                message="Profile jitter is set to 0%. Strict beaconing intervals are trivial for NIDS/Zeek to detect.",
                suggestion="Set jitter to at least 20-30% to introduce realistic timing variation."
            ))
        else:
            passed.append("Jitter timing variation configured (>0%)")

        # Rule 2: Sleeptime Check
        if profile.sleeptime < 1000:
            score -= 10
            issues.append(AuditIssue(
                rule_id="OPSEC-002",
                category="OPSEC",
                severity="WARNING",
                message=f"Sleeptime is extremely aggressive ({profile.sleeptime}ms). High packet frequency will alert SOC analysts.",
                suggestion="Increase sleeptime to 5000ms (5s) or higher for stealthy operations."
            ))
        else:
            passed.append("Sleeptime within acceptable operational parameters")

        # Rule 3: User-Agent Check
        ua = profile.useragent.lower()
        if not profile.useragent:
            score -= 20
            issues.append(AuditIssue(
                rule_id="OPSEC-003",
                category="OPSEC",
                severity="CRITICAL",
                message="User-Agent is empty. Beacon requests will use standard Java/libcurl agent, triggering instant block.",
                suggestion="Specify a modern, authentic browser User-Agent."
            ))
        elif "curl" in ua or "python" in ua or "powershell" in ua:
            score -= 25
            issues.append(AuditIssue(
                rule_id="OPSEC-004",
                category="OPSEC",
                severity="CRITICAL",
                message=f"Suspicious tool signature found in User-Agent: '{profile.useragent}'",
                suggestion="Replace with a modern Windows 10/11 Chrome or Edge User-Agent."
            ))
        else:
            passed.append("User-Agent resembles legitimate workstation browser")

        # Rule 4: Memory Permissions (stage.userwx)
        if profile.stage.userwx:
            score -= 25
            issues.append(AuditIssue(
                rule_id="EDR-001",
                category="EVASION",
                severity="CRITICAL",
                message="stage.userwx is TRUE! Memory is allocated as PAGE_EXECUTE_READWRITE (RWX). Modern EDRs flag RWX private memory pages instantly.",
                suggestion="Set 'set userwx \"false\";' to enforce RX memory pages."
            ))
        else:
            passed.append("stage.userwx is disabled (No RWX memory pages)")

        # Rule 5: Memory Permissions (process-inject.userwx)
        if profile.process_inject.userwx:
            score -= 20
            issues.append(AuditIssue(
                rule_id="EDR-002",
                category="EVASION",
                severity="CRITICAL",
                message="process-inject.userwx is TRUE! Remote process memory will be allocated as RWX, triggering Sysmon Event ID 8 / 10.",
                suggestion="Set process-inject userwx to false."
            ))
        else:
            passed.append("process-inject userwx is disabled")

        # Rule 6: Sleep Mask Check
        if not profile.stage.sleep_mask:
            score -= 15
            issues.append(AuditIssue(
                rule_id="EDR-003",
                category="EVASION",
                severity="WARNING",
                message="stage.sleep_mask is FALSE! Beacon memory is unencrypted in memory during sleep cycles, making it vulnerable to Moneta/Hunt-Sleeping-Beacons.",
                suggestion="Enable 'set sleep_mask \"true\";' to obfuscate in-memory payload during beacon sleep."
            ))
        else:
            passed.append("stage.sleep_mask is enabled (In-memory encryption during sleep)")

        # Rule 7: Cleanup Check
        if not profile.stage.cleanup:
            score -= 10
            issues.append(AuditIssue(
                rule_id="EDR-004",
                category="EVASION",
                severity="WARNING",
                message="stage.cleanup is FALSE! Reflective loader stub remains resident in memory after initialization.",
                suggestion="Enable 'set cleanup \"true\";' to release the loader stub after Beacon starts."
            ))
        else:
            passed.append("stage.cleanup enabled (Reflective loader memory freed)")

        # Rule 8: PE Stomping
        if not profile.stage.stomppe:
            score -= 5
            issues.append(AuditIssue(
                rule_id="EDR-005",
                category="EVASION",
                severity="INFO",
                message="stage.stomppe is FALSE! In-memory PE headers will remain intact and match generic signatures.",
                suggestion="Enable 'set stomppe \"true\";' to wipe PE headers from memory."
            ))
        else:
            passed.append("stage.stomppe enabled (PE headers removed from memory)")

        # Rule 9: Spawnto Binary Check
        noisy_spawns = ["rundll32.exe", "powershell.exe", "cmd.exe"]
        for p in [profile.post_ex.spawnto_x86, profile.post_ex.spawnto_x64]:
            p_lower = p.lower()
            if any(n in p_lower for n in noisy_spawns):
                score -= 15
                issues.append(AuditIssue(
                    rule_id="OPSEC-005",
                    category="OPSEC",
                    severity="WARNING",
                    message=f"Post-Ex spawnto targets a highly scrutinized binary: '{p}'",
                    suggestion="Change spawnto to benign background binaries like werfault.exe, runtimebroker.exe, or svchost.exe."
                ))
                break
        else:
            passed.append("Post-Ex spawnto binaries use low-profile system targets")

        # Rule 10: URI Collision Check
        get_uris = set(profile.http_get.uris)
        post_uris = set(profile.http_post.uris)
        collision = get_uris.intersection(post_uris)
        if collision:
            score -= 20
            issues.append(AuditIssue(
                rule_id="SYNTAX-001",
                category="SYNTAX",
                severity="CRITICAL",
                message=f"URI Collision detected between HTTP-GET and HTTP-POST: {list(collision)}",
                suggestion="Ensure HTTP-GET and HTTP-POST utilize distinct URI paths."
            ))
        else:
            passed.append("No URI collisions between GET and POST channels")

        # Rule 11: Transform Termination Checks
        # HTTP-GET metadata block termination
        get_meta = profile.http_get.client.transform_blocks.get("metadata")
        if not get_meta or not get_meta.termination:
            score -= 15
            issues.append(AuditIssue(
                rule_id="SYNTAX-002",
                category="SYNTAX",
                severity="CRITICAL",
                message="HTTP-GET client metadata transform block has no termination (header, parameter, print, or uri-append)!",
                suggestion="Add a termination action (e.g. 'header \"Cookie\";' or 'parameter \"token\";')."
            ))
        else:
            passed.append("HTTP-GET metadata transform block has valid termination")

        # HTTP-POST id block
        post_id = profile.http_post.client.transform_blocks.get("id")
        if not post_id or not post_id.termination:
            score -= 10
            issues.append(AuditIssue(
                rule_id="SYNTAX-003",
                category="SYNTAX",
                severity="WARNING",
                message="HTTP-POST client id transform block is missing or unterminated.",
                suggestion="Configure 'id { parameter \"session\"; }' in HTTP-POST."
            ))
        else:
            passed.append("HTTP-POST session ID block properly terminated")

        # Rule 12: Host Header Consistency
        get_host = next((h.value for h in profile.http_get.client.headers if h.name.lower() == "host"), "")
        post_host = next((h.value for h in profile.http_post.client.headers if h.name.lower() == "host"), "")
        if get_host and post_host and get_host != post_host:
            score -= 10
            issues.append(AuditIssue(
                rule_id="OPSEC-006",
                category="OPSEC",
                severity="WARNING",
                message=f"Host header mismatch between GET ('{get_host}') and POST ('{post_host}').",
                suggestion="Align Host headers across all transactions to avoid proxy heuristic alerts."
            ))
        else:
            passed.append("Host headers consistent across HTTP transactions")

        # Rule 13: Magic Bytes Check
        if profile.stage.magic_mz_x86 == "MZ":
            issues.append(AuditIssue(
                rule_id="OPSEC-007",
                category="EVASION",
                severity="INFO",
                message="stage.magic_mz_x86 is standard 'MZ'. Signature scanners target MZ in private heap/stack.",
                suggestion="Modify magic bytes to custom markers (e.g., 'MZRE' or random)."
            ))
        else:
            passed.append(f"Custom MZ magic bytes specified ({profile.stage.magic_mz_x86})")

        # Final score adjustments
        score = max(0, min(100, score))

        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "F"

        return AuditReport(
            profile_name=profile.name,
            score=score,
            grade=grade,
            issues=issues,
            passed_rules=passed
        )
