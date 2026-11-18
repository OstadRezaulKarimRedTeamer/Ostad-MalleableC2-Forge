#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <random>
#include <algorithm>
#include <sstream>
#include <cmath>

namespace OstadC2 {

class Transforms {
public:
    static std::string netbios_encode(const std::vector<uint8_t>& data, bool uppercase = false) {
        char base_char = uppercase ? 'A' : 'a';
        std::string result;
        result.reserve(data.size() * 2);
        for (uint8_t b : data) {
            char high = static_cast<char>(((b >> 4) & 0x0F) + base_char);
            char low  = static_cast<char>((b & 0x0F) + base_char);
            result.push_back(high);
            result.push_back(low);
        }
        return result;
    }

    static std::vector<uint8_t> netbios_decode(const std::string& text, bool uppercase = false) {
        char base_char = uppercase ? 'A' : 'a';
        std::vector<uint8_t> result;
        if (text.size() < 2) return result;
        result.reserve(text.size() / 2);
        for (size_t i = 0; i + 1 < text.size(); i += 2) {
            uint8_t high = static_cast<uint8_t>(text[i] - base_char);
            uint8_t low  = static_cast<uint8_t>(text[i + 1] - base_char);
            result.push_back(((high & 0x0F) << 4) | (low & 0x0F));
        }
        return result;
    }

    static std::vector<uint8_t> mask_encode(const std::vector<uint8_t>& data, const std::vector<uint8_t>& custom_key = {}) {
        std::vector<uint8_t> key = custom_key;
        if (key.size() != 4) {
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution<uint16_t> dis(1, 255);
            key = { static_cast<uint8_t>(dis(gen)), static_cast<uint8_t>(dis(gen)),
                    static_cast<uint8_t>(dis(gen)), static_cast<uint8_t>(dis(gen)) };
        }
        std::vector<uint8_t> result;
        result.reserve(4 + data.size());
        result.insert(result.end(), key.begin(), key.end());
        for (size_t i = 0; i < data.size(); ++i) {
            result.push_back(data[i] ^ key[i % 4]);
        }
        return result;
    }

    static std::vector<uint8_t> mask_decode(const std::vector<uint8_t>& data) {
        if (data.size() < 4) return data;
        std::vector<uint8_t> key(data.begin(), data.begin() + 4);
        std::vector<uint8_t> result;
        result.reserve(data.size() - 4);
        for (size_t i = 4; i < data.size(); ++i) {
            result.push_back(data[i] ^ key[(i - 4) % 4]);
        }
        return result;
    }

    static std::string base64_encode(const std::vector<uint8_t>& data) {
        static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        std::string out;
        int val = 0, valb = -6;
        for (uint8_t c : data) {
            val = (val << 8) + c;
            valb += 8;
            while (valb >= 0) {
                out.push_back(b64_table[(val >> valb) & 0x3F]);
                valb -= 6;
            }
        }
        if (valb > -6) out.push_back(b64_table[((val << 8) >> (valb + 8)) & 0x3F]);
        while (out.size() % 4) out.push_back('=');
        return out;
    }

    static std::vector<uint8_t> base64_decode(const std::string& in) {
        std::vector<uint8_t> out;
        std::vector<int> T(256, -1);
        for (int i = 0; i < 64; i++) {
            static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
            T[b64_table[i]] = i;
        }
        int val = 0, valb = -8;
        for (unsigned char c : in) {
            if (T[c] == -1) break;
            val = (val << 6) + T[c];
            valb += 6;
            if (valb >= 0) {
                out.push_back(char((val >> valb) & 0xFF));
                valb -= 8;
            }
        }
        return out;
    }

    static std::string base64url_encode(const std::vector<uint8_t>& data) {
        std::string s = base64_encode(data);
        for (char& c : s) {
            if (c == '+') c = '-';
            else if (c == '/') c = '_';
        }
        while (!s.empty() && s.back() == '=') {
            s.pop_back();
        }
        return s;
    }

    static std::vector<uint8_t> base64url_decode(std::string in) {
        for (char& c : in) {
            if (c == '-') c = '+';
            else if (c == '_') c = '/';
        }
        while (in.size() % 4 != 0) {
            in.push_back('=');
        }
        return base64_decode(in);
    }

    // Feature 12: Shannon Entropy Calculation
    static double calculate_shannon_entropy(const std::vector<uint8_t>& data) {
        if (data.empty()) return 0.0;
        std::map<uint8_t, size_t> freqs;
        for (uint8_t b : data) freqs[b]++;

        double entropy = 0.0;
        double len = static_cast<double>(data.size());
        for (const auto& pair : freqs) {
            double p = pair.second / len;
            entropy -= p * (std::log(p) / std::log(2.0));
        }
        return entropy;
    }

    // Feature 17: Gaussian / Normal Distribution Jitter
    static uint32_t calculate_gaussian_jitter(uint32_t sleep_ms, uint32_t jitter_pct) {
        if (jitter_pct == 0) return sleep_ms;
        std::random_device rd;
        std::mt19937 gen(rd());
        double stddev = (sleep_ms * (jitter_pct / 100.0)) / 3.0; // 99.7% of values within jitter range
        std::normal_distribution<double> dist(static_cast<double>(sleep_ms), stddev);
        double sample = dist(gen);
        return static_cast<uint32_t>(std::max<double>(1000.0, sample));
    }

    // Feature: Data Jitter / Packet Size Randomization
    static std::vector<uint8_t> apply_data_jitter(const std::vector<uint8_t>& data, uint32_t jitter_pct) {
        if (jitter_pct == 0) return data;
        std::random_device rd;
        std::mt19937 gen(rd());
        size_t max_noise = (data.size() * jitter_pct) / 100;
        if (max_noise == 0) max_noise = 8;
        std::uniform_int_distribution<size_t> dis(1, max_noise);
        size_t noise_len = dis(gen);

        std::vector<uint8_t> padded = data;
        padded.reserve(data.size() + noise_len);
        for (size_t i = 0; i < noise_len; ++i) {
            padded.push_back(static_cast<uint8_t>(dis(gen) % 256));
        }
        return padded;
    }
};

class TransformPipeline {
public:
    struct Step {
        std::string action;
        std::string arg;
    };

    std::vector<Step> steps;

    void add_step(const std::string& action, const std::string& arg = "") {
        steps.push_back({action, arg});
    }

    std::vector<uint8_t> execute(const std::vector<uint8_t>& input) const {
        std::vector<uint8_t> curr = input;
        for (const auto& s : steps) {
            if (s.action == "mask") {
                curr = Transforms::mask_encode(curr);
            } else if (s.action == "base64") {
                std::string s_b64 = Transforms::base64_encode(curr);
                curr.assign(s_b64.begin(), s_b64.end());
            } else if (s.action == "base64url") {
                std::string s_url = Transforms::base64url_encode(curr);
                curr.assign(s_url.begin(), s_url.end());
            } else if (s.action == "netbios") {
                std::string s_nb = Transforms::netbios_encode(curr, false);
                curr.assign(s_nb.begin(), s_nb.end());
            } else if (s.action == "netbiosu") {
                std::string s_nbu = Transforms::netbios_encode(curr, true);
                curr.assign(s_nbu.begin(), s_nbu.end());
            } else if (s.action == "prepend") {
                std::vector<uint8_t> res(s.arg.begin(), s.arg.end());
                res.insert(res.end(), curr.begin(), curr.end());
                curr = res;
            } else if (s.action == "append") {
                curr.insert(curr.end(), s.arg.begin(), s.arg.end());
            }
        }
        return curr;
    }

    std::vector<uint8_t> reverse(const std::vector<uint8_t>& input) const {
        std::vector<uint8_t> curr = input;
        for (auto it = steps.rbegin(); it != steps.rend(); ++it) {
            const auto& s = *it;
            if (s.action == "mask") {
                curr = Transforms::mask_decode(curr);
            } else if (s.action == "base64") {
                std::string s_b64(curr.begin(), curr.end());
                curr = Transforms::base64_decode(s_b64);
            } else if (s.action == "base64url") {
                std::string s_url(curr.begin(), curr.end());
                curr = Transforms::base64url_decode(s_url);
            } else if (s.action == "netbios") {
                std::string s_nb(curr.begin(), curr.end());
                curr = Transforms::netbios_decode(s_nb, false);
            } else if (s.action == "netbiosu") {
                std::string s_nbu(curr.begin(), curr.end());
                curr = Transforms::netbios_decode(s_nbu, true);
            } else if (s.action == "prepend") {
                if (curr.size() >= s.arg.size()) {
                    bool match = true;
                    for (size_t i = 0; i < s.arg.size(); ++i) {
                        if (curr[i] != static_cast<uint8_t>(s.arg[i])) { match = false; break; }
                    }
                    if (match) curr.erase(curr.begin(), curr.begin() + s.arg.size());
                }
            } else if (s.action == "append") {
                if (curr.size() >= s.arg.size()) {
                    bool match = true;
                    size_t start = curr.size() - s.arg.size();
                    for (size_t i = 0; i < s.arg.size(); ++i) {
                        if (curr[start + i] != static_cast<uint8_t>(s.arg[i])) { match = false; break; }
                    }
                    if (match) curr.erase(curr.begin() + start, curr.end());
                }
            }
        }
        return curr;
    }
};

} // namespace OstadC2
