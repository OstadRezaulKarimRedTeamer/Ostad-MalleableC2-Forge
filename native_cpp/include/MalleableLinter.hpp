#pragma once

#include "MalleableModels.hpp"
#include <algorithm>
#include <set>

namespace OstadC2 {

class C2Linter {
public:
    static AuditReport audit(const Profile& p) {
        AuditReport rep;
        rep.profile_name = p.name;
        int score = 100;

        // 1. Jitter
        if (p.jitter == 0) {
            score -= 15;
            rep.issues.push_back({
                "OPSEC-001", "OPSEC", "CRITICAL",
                "Profile jitter is 0%. Strict beaconing intervals are trivial for NIDS/Zeek to detect.",
                "Set jitter to at least 20-30%."
            });
        } else {
            rep.passed_rules.push_back("Jitter timing variation configured (>0%)");
        }

        // 2. Sleeptime
        if (p.sleeptime < 1000) {
            score -= 10;
            rep.issues.push_back({
                "OPSEC-002", "OPSEC", "WARNING",
                "Sleeptime is under 1000ms. High packet frequency alerts SOC analysts.",
                "Increase sleeptime to 5000ms or higher."
            });
        } else {
            rep.passed_rules.push_back("Sleeptime within acceptable bounds");
        }

        // 3. User-Agent
        std::string ua = p.useragent;
        std::transform(ua.begin(), ua.end(), ua.begin(), ::tolower);
        if (p.useragent.empty()) {
            score -= 20;
            rep.issues.push_back({
                "OPSEC-003", "OPSEC", "CRITICAL",
                "User-Agent is empty. Beacon will use default libcurl/Java headers.",
                "Specify a modern workstation browser User-Agent."
            });
        } else if (ua.find("curl") != std::string::npos || ua.find("python") != std::string::npos) {
            score -= 25;
            rep.issues.push_back({
                "OPSEC-004", "OPSEC", "CRITICAL",
                "Suspicious tool signature found in User-Agent.",
                "Replace with a standard browser User-Agent."
            });
        } else {
            rep.passed_rules.push_back("User-Agent matches legitimate workstation browser");
        }

        // 4. Memory Permissions (stage.userwx)
        if (p.stage.userwx) {
            score -= 25;
            rep.issues.push_back({
                "EDR-001", "EVASION", "CRITICAL",
                "stage.userwx is TRUE! Memory is allocated as PAGE_EXECUTE_READWRITE (RWX).",
                "Set 'userwx false' to enforce RX memory."
            });
        } else {
            rep.passed_rules.push_back("stage.userwx is disabled (No RWX memory)");
        }

        // 5. Memory Permissions (process-inject.userwx)
        if (p.process_inject.userwx) {
            score -= 20;
            rep.issues.push_back({
                "EDR-002", "EVASION", "CRITICAL",
                "process-inject.userwx is TRUE! Remote process memory will be allocated as RWX.",
                "Set process-inject userwx to false."
            });
        } else {
            rep.passed_rules.push_back("process-inject userwx is disabled");
        }

        // 6. Sleep Mask
        if (!p.stage.sleep_mask) {
            score -= 15;
            rep.issues.push_back({
                "EDR-003", "EVASION", "WARNING",
                "stage.sleep_mask is FALSE! Beacon memory is unencrypted during sleep.",
                "Enable 'sleep_mask true' to defeat memory scanners."
            });
        } else {
            rep.passed_rules.push_back("stage.sleep_mask enabled (In-memory encryption during sleep)");
        }

        // 7. Cleanup
        if (!p.stage.cleanup) {
            score -= 10;
            rep.issues.push_back({
                "EDR-004", "EVASION", "WARNING",
                "stage.cleanup is FALSE! Reflective loader stub remains resident in memory.",
                "Enable 'cleanup true'."
            });
        } else {
            rep.passed_rules.push_back("stage.cleanup enabled (Reflective loader memory freed)");
        }

        // 8. Stomp PE
        if (!p.stage.stomppe) {
            score -= 5;
            rep.issues.push_back({
                "EDR-005", "EVASION", "INFO",
                "stage.stomppe is FALSE! PE headers remain intact in memory.",
                "Enable 'stomppe true'."
            });
        } else {
            rep.passed_rules.push_back("stage.stomppe enabled (PE headers wiped from memory)");
        }

        // 9. Spawnto binary
        std::string sp86 = p.post_ex.spawnto_x86;
        std::transform(sp86.begin(), sp86.end(), sp86.begin(), ::tolower);
        if (sp86.find("rundll32") != std::string::npos || sp86.find("powershell") != std::string::npos) {
            score -= 15;
            rep.issues.push_back({
                "OPSEC-005", "OPSEC", "WARNING",
                "Post-Ex spawnto targets a highly monitored binary: " + p.post_ex.spawnto_x86,
                "Change spawnto to werfault.exe or svchost.exe."
            });
        } else {
            rep.passed_rules.push_back("Post-Ex spawnto binaries use low-profile system targets");
        }

        // 10. URI Collision
        std::set<std::string> get_uris(p.http_get.uris.begin(), p.http_get.uris.end());
        for (const auto& u : p.http_post.uris) {
            if (get_uris.find(u) != get_uris.end()) {
                score -= 20;
                rep.issues.push_back({
                    "SYNTAX-001", "SYNTAX", "CRITICAL",
                    "URI Collision detected between HTTP-GET and HTTP-POST: " + u,
                    "Ensure distinct URI paths for GET and POST channels."
                });
                break;
            }
        }
        if (score == 100 || rep.issues.empty()) {
            rep.passed_rules.push_back("No URI collisions between GET and POST channels");
        }

        // 11. Transform termination
        auto it_meta = p.http_get.client.transform_blocks.find("metadata");
        if (it_meta == p.http_get.client.transform_blocks.end() || !it_meta->second.has_termination) {
            score -= 15;
            rep.issues.push_back({
                "SYNTAX-002", "SYNTAX", "CRITICAL",
                "HTTP-GET metadata transform block is missing or unterminated.",
                "Add a termination action (e.g. 'header \"Cookie\";')."
            });
        } else {
            rep.passed_rules.push_back("HTTP-GET metadata transform block properly terminated");
        }

        score = std::max(0, std::min(100, score));
        rep.score = score;
        if (score >= 90) rep.grade = "A+";
        else if (score >= 80) rep.grade = "A";
        else if (score >= 70) rep.grade = "B";
        else if (score >= 50) rep.grade = "C";
        else rep.grade = "F";

        return rep;
    }
};

} // namespace OstadC2
