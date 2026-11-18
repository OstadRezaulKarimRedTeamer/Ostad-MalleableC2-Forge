#pragma once

#include "MalleableModels.hpp"
#include <sstream>

namespace OstadC2 {

class Serializer {
public:
    static std::string serialize_transform_block(const std::string& name, const TransformBlock& tb, const std::string& indent = "        ") {
        std::ostringstream ss;
        ss << indent << name << " {\n";
        for (const auto& t : tb.transforms) {
            if (t.action == "prepend" || t.action == "append") {
                ss << indent << "    " << t.action << " \"" << escape(t.arg) << "\";\n";
            } else {
                ss << indent << "    " << t.action << ";\n";
            }
        }
        if (tb.has_termination) {
            if (tb.termination.target == "print") {
                ss << indent << "    print;\n";
            } else if (tb.termination.target == "uri-append") {
                ss << indent << "    uri-append;\n";
            } else if (tb.termination.target == "header") {
                ss << indent << "    header \"" << escape(tb.termination.name) << "\";\n";
            } else if (tb.termination.target == "parameter") {
                ss << indent << "    parameter \"" << escape(tb.termination.name) << "\";\n";
            }
        }
        ss << indent << "}";
        return ss.str();
    }

    static std::string serialize_client(const ClientSubBlock& client, const std::string& indent = "    ") {
        std::ostringstream ss;
        ss << indent << "client {\n";
        for (const auto& h : client.headers) {
            ss << indent << "    header \"" << escape(h.name) << "\" \"" << escape(h.value) << "\";\n";
        }
        for (const auto& p : client.parameters) {
            ss << indent << "    parameter \"" << escape(p.name) << "\" \"" << escape(p.value) << "\";\n";
        }
        for (const auto& pair : client.transform_blocks) {
            ss << serialize_transform_block(pair.first, pair.second, indent + "    ") << "\n";
        }
        ss << indent << "}";
        return ss.str();
    }

    static std::string serialize_server(const ServerSubBlock& server, const std::string& indent = "    ") {
        std::ostringstream ss;
        ss << indent << "server {\n";
        for (const auto& h : server.headers) {
            ss << indent << "    header \"" << escape(h.name) << "\" \"" << escape(h.value) << "\";\n";
        }
        if (server.has_output) {
            ss << serialize_transform_block("output", server.output, indent + "    ") << "\n";
        }
        ss << indent << "}";
        return ss.str();
    }

    static std::string serialize_http(const std::string& verb_name, const HttpTransaction& tx) {
        std::ostringstream ss;
        ss << verb_name << " {\n";
        if (!tx.uris.empty()) {
            ss << "    set uri";
            for (const auto& u : tx.uris) {
                ss << " \"" << escape(u) << "\"";
            }
            ss << ";\n";
        }
        if (tx.verb != "GET") {
            ss << "    set verb \"" << tx.verb << "\";\n";
        }
        ss << "\n" << serialize_client(tx.client, "    ") << "\n\n";
        ss << serialize_server(tx.server, "    ") << "\n}";
        return ss.str();
    }

    static std::string serialize(const Profile& p) {
        std::ostringstream ss;
        ss << "# =====================================================================\n";
        ss << "# Profile: " << p.name << "\n";
        ss << "# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine (C++)\n";
        ss << "# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)\n";
        ss << "# =====================================================================\n\n";

        ss << "set sample_name \"" << escape(p.sample_name) << "\";\n";
        ss << "set sleeptime \"" << p.sleeptime << "\";\n";
        ss << "set jitter \"" << p.jitter << "\";\n";
        ss << "set maxget \"1048576\";\n";
        ss << "set data_jitter \"" << p.data_jitter << "\";\n";
        ss << "set useragent \"" << escape(p.useragent) << "\";\n";
        ss << "set pipename \"" << escape(p.pipename) << "\";\n";
        ss << "set pipename_stager \"" << escape(p.pipename_stager) << "\";\n\n";

        // Global settings
        for (const auto& pair : p.global_settings) {
            ss << "set " << pair.first << " \"" << escape(pair.second) << "\";\n";
        }

        ss << "\n" << serialize_http("http-get", p.http_get) << "\n\n";
        ss << serialize_http("http-post", p.http_post) << "\n\n";

        // stage block
        const auto& s = p.stage;
        ss << "stage {\n";
        ss << "    set checksum \"" << s.checksum << "\";\n";
        ss << "    set cleanup \"" << (s.cleanup ? "true" : "false") << "\";\n";
        ss << "    set sleep_mask \"" << (s.sleep_mask ? "true" : "false") << "\";\n";
        ss << "    set smartinject \"" << (s.smartinject ? "true" : "false") << "\";\n";
        ss << "    set stomppe \"" << (s.stomppe ? "true" : "false") << "\";\n";
        ss << "    set obfuscate \"" << (s.obfuscate ? "true" : "false") << "\";\n";
        ss << "    set userwx \"" << (s.userwx ? "true" : "false") << "\";\n";
        ss << "    set magic_mz_x86 \"" << escape(s.magic_mz_x86) << "\";\n";
        ss << "    set magic_mz_x64 \"" << escape(s.magic_mz_x64) << "\";\n";
        ss << "    set magic_pe \"" << escape(s.magic_pe) << "\";\n";
        if (!s.compile_time.empty()) ss << "    set compile_time \"" << s.compile_time << "\";\n";
        if (!s.transform_x86_prepend.empty()) {
            ss << "    transform-x86 {\n        prepend \"" << s.transform_x86_prepend << "\";\n    }\n";
        }
        if (!s.transform_x64_prepend.empty()) {
            ss << "    transform-x64 {\n        prepend \"" << s.transform_x64_prepend << "\";\n    }\n";
        }
        ss << "}\n\n";

        // process-inject block
        const auto& pi = p.process_inject;
        ss << "process-inject {\n";
        ss << "    set allocator \"" << pi.allocator << "\";\n";
        ss << "    set min_alloc \"" << pi.min_alloc << "\";\n";
        ss << "    set startrwx \"" << (pi.startrwx ? "true" : "false") << "\";\n";
        ss << "    set userwx \"" << (pi.userwx ? "true" : "false") << "\";\n";
        ss << "    execute {\n";
        for (const auto& exe : pi.execute_order) {
            ss << "        " << exe << ";\n";
        }
        ss << "    }\n";
        ss << "}\n\n";

        // post-ex block
        const auto& pe = p.post_ex;
        ss << "post-ex {\n";
        ss << "    set spawnto_x86 \"" << escape(pe.spawnto_x86) << "\";\n";
        ss << "    set spawnto_x64 \"" << escape(pe.spawnto_x64) << "\";\n";
        ss << "    set amsi_disable \"" << (pe.amsi_disable ? "true" : "false") << "\";\n";
        ss << "    set keylogger \"" << escape(pe.keylogger) << "\";\n";
        ss << "}\n\n";

        // https-certificate
        const auto& cert = p.https_cert;
        ss << "https-certificate {\n";
        ss << "    set CN \"" << escape(cert.CN) << "\";\n";
        ss << "    set O \"" << escape(cert.O) << "\";\n";
        ss << "    set OU \"" << escape(cert.OU) << "\";\n";
        ss << "    set C \"" << escape(cert.C) << "\";\n";
        ss << "    set ST \"" << escape(cert.ST) << "\";\n";
        ss << "    set L \"" << escape(cert.L) << "\";\n";
        ss << "    set validity \"" << cert.validity << "\";\n";
        ss << "}\n";

        return ss.str();
    }

private:
    static std::string escape(const std::string& in) {
        std::string out;
        for (char c : in) {
            if (c == '"') out += "\\\"";
            else if (c == '\\') out += "\\\\";
            else out += c;
        }
        return out;
    }
};

} // namespace OstadC2
