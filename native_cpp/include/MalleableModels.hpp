#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdint>
#include <chrono>

namespace OstadC2 {

// Feature 20: MITRE ATT&CK Matrix Technique Mapping
struct MitreTechnique {
    std::string id;          // e.g. "T1071.001"
    std::string name;        // e.g. "Application Layer Protocol: Web Protocols"
    std::string tactic;      // e.g. "Command and Control"
    std::string description;
};

// Feature 10: Operational Hours & RoE Kill-Date
struct OperationalWindow {
    bool enabled = true;
    int start_hour = 8;     // 08:00 AM
    int end_hour = 20;      // 08:00 PM
    std::string kill_date = "2026-12-31"; // Auto-terminate after this date
    bool enforce_weekdays = true; // Monday to Friday only
};

struct Header {
    std::string name;
    std::string value;
};

struct Parameter {
    std::string name;
    std::string value;
};

struct TransformAction {
    std::string action; // "mask", "base64", "base64url", "netbios", "netbiosu", "prepend", "append"
    std::string arg;    // argument for prepend / append
};

struct TerminationAction {
    std::string target; // "print", "header", "parameter", "uri-append"
    std::string name;   // header name or parameter name
};

struct TransformBlock {
    std::string block_type; // "metadata", "id", "output"
    std::vector<TransformAction> transforms;
    TerminationAction termination;
    bool has_termination = false;
};

struct ClientSubBlock {
    std::vector<Header> headers;
    std::vector<Parameter> parameters;
    std::map<std::string, TransformBlock> transform_blocks;
};

struct ServerSubBlock {
    std::vector<Header> headers;
    TransformBlock output;
    bool has_output = false;
};

struct HttpTransaction {
    std::string verb = "GET"; // "GET" or "POST"
    std::vector<std::string> uris;
    ClientSubBlock client;
    ServerSubBlock server;
};

struct DnsBeaconBlock {
    uint32_t maxdns = 255;
    std::string beacon = "beacon.corp.com";
    std::string get_A = "cdn.corp.com";
    std::string get_AAAA = "ipv6.corp.com";
    std::string get_TXT = "txt.corp.com";
    uint32_t ttl = 300;
};

struct StageBlock {
    uint32_t checksum = 0;
    bool cleanup = true;
    bool sleep_mask = true;
    bool smartinject = true;
    bool stomppe = true;
    bool obfuscate = true;
    bool userwx = false;
    std::string compile_time = "";
    std::string magic_mz_x86 = "MZRE";
    std::string magic_mz_x64 = "MZRE";
    std::string magic_pe = "PE";
    std::string transform_x86_prepend = "";
    std::string transform_x64_prepend = "";
    std::map<std::string, std::string> raw_settings;
};

struct ProcessInjectBlock {
    std::string allocator = "VirtualAllocEx";
    uint32_t min_alloc = 4096;
    bool startrwx = false;
    bool userwx = false;
    std::vector<TransformAction> transform_x86;
    std::vector<TransformAction> transform_x64;
    std::vector<std::string> execute_order = {
        "CreateThread", "SetThreadContext", "CreateRemoteThread", "RtlCreateUserThread"
    };
    std::map<std::string, std::string> raw_settings;
};

struct PostExBlock {
    std::string spawnto_x86 = "%windir%\\syswow64\\werfault.exe";
    std::string spawnto_x64 = "%windir%\\sysnative\\werfault.exe";
    bool amsi_disable = true;
    std::string keylogger = "GetAsyncKeyState";
    std::map<std::string, std::string> raw_settings;
};

struct HttpsCertificate {
    std::string CN = "microsoft.com";
    std::string O = "Microsoft Corporation";
    std::string OU = "Cloud Services";
    std::string C = "US";
    std::string ST = "WA";
    std::string L = "Redmond";
    uint32_t validity = 365;
    std::map<std::string, std::string> raw_settings;
};

struct Profile {
    std::string name = "Untitled_Profile";
    uint32_t watermark = 982143; // Feature 1: Authorization Watermark
    uint32_t sleeptime = 5000;
    uint32_t jitter = 25;
    uint32_t data_jitter = 15;
    std::string useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";
    std::string pipename = "msagent_##";
    std::string pipename_stager = "status_##";
    std::string sample_name = "SecurityUpdate.exe";
    std::map<std::string, std::string> global_settings;

    HttpTransaction http_get;
    HttpTransaction http_post;
    HttpTransaction http_stager;
    DnsBeaconBlock dns_beacon;
    StageBlock stage;
    ProcessInjectBlock process_inject;
    PostExBlock post_ex;
    HttpsCertificate https_cert;
    OperationalWindow operational_window;
};

// Beacon Session Tracker
struct BeaconSession {
    std::string id;
    std::string ip;
    int port = 0;
    std::string user;
    std::string host;
    std::string os;
    std::string arch;
    uint32_t sleeptime = 5000;
    uint32_t jitter = 25;
    std::chrono::system_clock::time_point first_seen;
    std::chrono::system_clock::time_point last_seen;
    uint64_t total_packets = 0;
    uint64_t total_bytes = 0;
    double last_entropy = 0.0;
    std::vector<std::string> queued_tasks;
};

// Telemetry & Traffic Metrics
struct TrafficMetrics {
    uint64_t total_connections = 0;
    uint64_t total_get_requests = 0;
    uint64_t total_post_requests = 0;
    uint64_t total_bytes_in = 0;
    uint64_t total_bytes_out = 0;
    uint64_t nids_alerts_triggered = 0;
    uint64_t honeypot_redirects = 0;
    uint64_t auth_failures = 0;
};

struct AuditIssue {
    std::string rule_id;
    std::string category;
    std::string severity;
    std::string message;
    std::string suggestion;
};

struct AuditReport {
    std::string profile_name;
    int score = 100;
    std::string grade = "A+";
    std::vector<AuditIssue> issues;
    std::vector<std::string> passed_rules;

    int critical_count() const {
        int c = 0;
        for (const auto& i : issues) if (i.severity == "CRITICAL") c++;
        return c;
    }
    int warning_count() const {
        int c = 0;
        for (const auto& i : issues) if (i.severity == "WARNING") c++;
        return c;
    }
    int info_count() const {
        int c = 0;
        for (const auto& i : issues) if (i.severity == "INFO") c++;
        return c;
    }
};

} // namespace OstadC2
