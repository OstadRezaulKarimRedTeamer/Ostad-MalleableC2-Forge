#pragma once

#include "MalleableModels.hpp"
#include "MalleableTransforms.hpp"
#include <string>
#include <vector>
#include <sstream>

namespace OstadC2 {

class TrafficSimulator {
public:
    static std::pair<std::string, std::string> simulate_get(
        const Profile& p,
        const std::string& mock_metadata = "BEACON_ID=9821;ARCH=x64;HOST=VICTIM-PC;USER=admin"
    ) {
        std::ostringstream req;
        std::string uri = p.http_get.uris.empty() ? "/api/v1/sync" : p.http_get.uris[0];

        // Process metadata transform
        std::string cookie_header = "";
        auto it_meta = p.http_get.client.transform_blocks.find("metadata");
        if (it_meta != p.http_get.client.transform_blocks.end()) {
            TransformPipeline pipe;
            for (const auto& t : it_meta->second.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::vector<uint8_t> in(mock_metadata.begin(), mock_metadata.end());
            auto out = pipe.execute(in);
            std::string trans_str(out.begin(), out.end());

            if (it_meta->second.has_termination) {
                if (it_meta->second.termination.target == "header") {
                    cookie_header = it_meta->second.termination.name + ": " + trans_str;
                } else if (it_meta->second.termination.target == "parameter") {
                    uri += (uri.find('?') == std::string::npos ? "?" : "&");
                    uri += it_meta->second.termination.name + "=" + trans_str;
                } else if (it_meta->second.termination.target == "uri-append") {
                    uri += "/" + trans_str;
                }
            }
        }

        req << p.http_get.verb << " " << uri << " HTTP/1.1\r\n";
        req << "User-Agent: " << p.useragent << "\r\n";
        for (const auto& h : p.http_get.client.headers) {
            req << h.name << ": " << h.value << "\r\n";
        }
        if (!cookie_header.empty()) {
            req << cookie_header << "\r\n";
        }
        req << "Connection: keep-alive\r\n\r\n";

        // Server Response
        std::ostringstream resp;
        resp << "HTTP/1.1 200 OK\r\n";
        for (const auto& h : p.http_get.server.headers) {
            resp << h.name << ": " << h.value << "\r\n";
        }

        std::string srv_body = "";
        if (p.http_get.server.has_output) {
            TransformPipeline pipe;
            for (const auto& t : p.http_get.server.output.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::string task_raw = "TASK:102:shell whoami /all";
            std::vector<uint8_t> in(task_raw.begin(), task_raw.end());
            auto out = pipe.execute(in);
            srv_body.assign(out.begin(), out.end());
        }

        resp << "Content-Length: " << srv_body.size() << "\r\n";
        resp << "Connection: keep-alive\r\n\r\n";
        resp << srv_body;

        return {req.str(), resp.str()};
    }

    static std::pair<std::string, std::string> simulate_post(
        const Profile& p,
        const std::string& mock_output = "NT AUTHORITY\\SYSTEM\r\nPrivileges: SeDebugPrivilege Enabled"
    ) {
        std::ostringstream req;
        std::string uri = p.http_post.uris.empty() ? "/api/v1/report" : p.http_post.uris[0];

        // Process ID block
        auto it_id = p.http_post.client.transform_blocks.find("id");
        if (it_id != p.http_post.client.transform_blocks.end()) {
            TransformPipeline pipe;
            for (const auto& t : it_id->second.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::string id_raw = "982143";
            std::vector<uint8_t> in(id_raw.begin(), id_raw.end());
            auto out = pipe.execute(in);
            std::string id_trans(out.begin(), out.end());
            if (it_id->second.has_termination && it_id->second.termination.target == "parameter") {
                uri += (uri.find('?') == std::string::npos ? "?" : "&");
                uri += it_id->second.termination.name + "=" + id_trans;
            }
        }

        // Process Output block
        std::string body = "";
        auto it_out = p.http_post.client.transform_blocks.find("output");
        if (it_out != p.http_post.client.transform_blocks.end()) {
            TransformPipeline pipe;
            for (const auto& t : it_out->second.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::vector<uint8_t> in(mock_output.begin(), mock_output.end());
            auto out = pipe.execute(in);
            body.assign(out.begin(), out.end());
        }

        req << p.http_post.verb << " " << uri << " HTTP/1.1\r\n";
        req << "User-Agent: " << p.useragent << "\r\n";
        for (const auto& h : p.http_post.client.headers) {
            req << h.name << ": " << h.value << "\r\n";
        }
        req << "Content-Length: " << body.size() << "\r\n";
        req << "Connection: keep-alive\r\n\r\n";
        req << body;

        // Server Response
        std::ostringstream resp;
        resp << "HTTP/1.1 200 OK\r\n";
        for (const auto& h : p.http_post.server.headers) {
            resp << h.name << ": " << h.value << "\r\n";
        }
        std::string ack_body = "{\"status\":\"ok\"}";
        resp << "Content-Length: " << ack_body.size() << "\r\n";
        resp << "Connection: keep-alive\r\n\r\n";
        resp << ack_body;

        return {req.str(), resp.str()};
    }
};

} // namespace OstadC2
