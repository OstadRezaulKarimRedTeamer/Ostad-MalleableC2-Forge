#pragma once

#include "MalleableModels.hpp"
#include <string>
#include <vector>
#include <sstream>
#include <stdexcept>
#include <cctype>

namespace OstadC2 {

enum class TokenType {
    IDENT,
    STRING,
    LBRACE,
    RBRACE,
    SEMICOLON,
    END_OF_FILE
};

struct Token {
    TokenType type;
    std::string value;
    int line;
};

class Lexer {
public:
    explicit Lexer(const std::string& source) : src(source), pos(0), line(1) {}

    std::vector<Token> tokenize() {
        std::vector<Token> tokens;
        while (pos < src.size()) {
            char c = src[pos];

            if (c == ' ' || c == '\t' || c == '\r') {
                pos++;
                continue;
            }
            if (c == '\n') {
                line++;
                pos++;
                continue;
            }
            if (c == '#') {
                while (pos < src.size() && src[pos] != '\n') pos++;
                continue;
            }

            if (c == '{') {
                tokens.push_back({TokenType::LBRACE, "{", line});
                pos++;
                continue;
            }
            if (c == '}') {
                tokens.push_back({TokenType::RBRACE, "}", line});
                pos++;
                continue;
            }
            if (c == ';') {
                tokens.push_back({TokenType::SEMICOLON, ";", line});
                pos++;
                continue;
            }

            if (c == '"') {
                pos++;
                std::string s;
                while (pos < src.size() && src[pos] != '"') {
                    if (src[pos] == '\\' && pos + 1 < src.size()) {
                        pos++;
                        char esc = src[pos];
                        if (esc == 'n') s += '\n';
                        else if (esc == 'r') s += '\r';
                        else if (esc == 't') s += '\t';
                        else if (esc == '"') s += '"';
                        else if (esc == '\\') s += '\\';
                        else s += esc;
                    } else if (src[pos] == '\n') {
                        line++;
                        s += src[pos];
                    } else {
                        s += src[pos];
                    }
                    pos++;
                }
                if (pos < src.size()) pos++; // skip closing '"'
                tokens.push_back({TokenType::STRING, s, line});
                continue;
            }

            if (std::isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_' || c == '.' || c == '%' || c == '\\' || c == '/') {
                size_t start = pos;
                while (pos < src.size() && (
                    std::isalnum(static_cast<unsigned char>(src[pos])) ||
                    src[pos] == '-' || src[pos] == '_' || src[pos] == '.' ||
                    src[pos] == '%' || src[pos] == '\\' || src[pos] == '/' || src[pos] == ':'
                )) {
                    pos++;
                }
                tokens.push_back({TokenType::IDENT, src.substr(start, pos - start), line});
                continue;
            }

            pos++;
        }

        tokens.push_back({TokenType::END_OF_FILE, "", line});
        return tokens;
    }

private:
    std::string src;
    size_t pos;
    int line;
};

class Parser {
public:
    explicit Parser(const std::vector<Token>& token_list) : tokens(token_list), idx(0) {}

    Profile parse() {
        Profile p;
        while (!is_at_end()) {
            const Token& t = peek();

            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                match(TokenType::SEMICOLON);

                if (key == "sample_name") p.sample_name = val;
                else if (key == "sleeptime") p.sleeptime = std::strtoul(val.c_str(), nullptr, 10);
                else if (key == "jitter") p.jitter = std::strtoul(val.c_str(), nullptr, 10);
                else if (key == "data_jitter") p.data_jitter = std::strtoul(val.c_str(), nullptr, 10);
                else if (key == "useragent") p.useragent = val;
                else if (key == "pipename") p.pipename = val;
                else if (key == "pipename_stager") p.pipename_stager = val;
                else p.global_settings[key] = val;
            }
            else if (t.type == TokenType::IDENT && t.value == "http-get") {
                advance();
                p.http_get = parse_http_block("GET");
            }
            else if (t.type == TokenType::IDENT && t.value == "http-post") {
                advance();
                p.http_post = parse_http_block("POST");
            }
            else if (t.type == TokenType::IDENT && t.value == "stage") {
                advance();
                p.stage = parse_stage_block();
            }
            else if (t.type == TokenType::IDENT && t.value == "process-inject") {
                advance();
                p.process_inject = parse_process_inject_block();
            }
            else if (t.type == TokenType::IDENT && t.value == "post-ex") {
                advance();
                p.post_ex = parse_post_ex_block();
            }
            else if (t.type == TokenType::IDENT && t.value == "https-certificate") {
                advance();
                p.https_cert = parse_https_cert_block();
            }
            else {
                if (t.type == TokenType::IDENT) {
                    advance();
                    if (match(TokenType::LBRACE)) {
                        skip_block();
                    }
                } else {
                    advance();
                }
            }
        }
        return p;
    }

private:
    std::vector<Token> tokens;
    size_t idx;

    bool is_at_end() const {
        return idx >= tokens.size() || tokens[idx].type == TokenType::END_OF_FILE;
    }

    const Token& peek() const {
        return tokens[idx];
    }

    const Token& advance() {
        if (!is_at_end()) idx++;
        return tokens[idx - 1];
    }

    bool match(TokenType type) {
        if (!is_at_end() && peek().type == type) {
            advance();
            return true;
        }
        return false;
    }

    Token expect(TokenType type) {
        if (is_at_end() || peek().type != type) {
            throw std::runtime_error("Unexpected token at line " + std::to_string(peek().line));
        }
        return advance();
    }

    void skip_block() {
        int depth = 1;
        while (depth > 0 && !is_at_end()) {
            Token t = advance();
            if (t.type == TokenType::LBRACE) depth++;
            else if (t.type == TokenType::RBRACE) depth--;
        }
    }

    HttpTransaction parse_http_block(const std::string& default_verb) {
        expect(TokenType::LBRACE);
        HttpTransaction tx;
        tx.verb = default_verb;

        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                if (key == "uri") {
                    tx.uris.push_back(val);
                    while (!is_at_end() && peek().type == TokenType::STRING) {
                        tx.uris.push_back(advance().value);
                    }
                } else if (key == "verb") {
                    tx.verb = val;
                }
                match(TokenType::SEMICOLON);
            }
            else if (t.type == TokenType::IDENT && t.value == "client") {
                advance();
                tx.client = parse_client_block();
            }
            else if (t.type == TokenType::IDENT && t.value == "server") {
                advance();
                tx.server = parse_server_block();
            }
            else {
                advance();
            }
        }
        return tx;
    }

    ClientSubBlock parse_client_block() {
        expect(TokenType::LBRACE);
        ClientSubBlock client;

        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "header") {
                advance();
                std::string name = expect(TokenType::STRING).value;
                std::string val = expect(TokenType::STRING).value;
                match(TokenType::SEMICOLON);
                client.headers.push_back({name, val});
            }
            else if (t.type == TokenType::IDENT && t.value == "parameter") {
                advance();
                std::string name = expect(TokenType::STRING).value;
                std::string val = expect(TokenType::STRING).value;
                match(TokenType::SEMICOLON);
                client.parameters.push_back({name, val});
            }
            else if (t.type == TokenType::IDENT && (t.value == "metadata" || t.value == "id" || t.value == "output")) {
                std::string bname = advance().value;
                client.transform_blocks[bname] = parse_transform_block(bname);
            }
            else {
                advance();
            }
        }
        return client;
    }

    ServerSubBlock parse_server_block() {
        expect(TokenType::LBRACE);
        ServerSubBlock server;

        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "header") {
                advance();
                std::string name = expect(TokenType::STRING).value;
                std::string val = expect(TokenType::STRING).value;
                match(TokenType::SEMICOLON);
                server.headers.push_back({name, val});
            }
            else if (t.type == TokenType::IDENT && t.value == "output") {
                advance();
                server.output = parse_transform_block("output");
                server.has_output = true;
            }
            else {
                advance();
            }
        }
        return server;
    }

    TransformBlock parse_transform_block(const std::string& block_type) {
        expect(TokenType::LBRACE);
        TransformBlock tb;
        tb.block_type = block_type;

        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && (
                t.value == "base64" || t.value == "base64url" ||
                t.value == "netbios" || t.value == "netbiosu" || t.value == "mask"
            )) {
                std::string act = advance().value;
                match(TokenType::SEMICOLON);
                tb.transforms.push_back({act, ""});
            }
            else if (t.type == TokenType::IDENT && (t.value == "prepend" || t.value == "append")) {
                std::string act = advance().value;
                std::string arg = advance().value;
                match(TokenType::SEMICOLON);
                tb.transforms.push_back({act, arg});
            }
            else if (t.type == TokenType::IDENT && t.value == "print") {
                advance();
                match(TokenType::SEMICOLON);
                tb.termination = {"print", ""};
                tb.has_termination = true;
            }
            else if (t.type == TokenType::IDENT && t.value == "header") {
                advance();
                std::string hname = expect(TokenType::STRING).value;
                match(TokenType::SEMICOLON);
                tb.termination = {"header", hname};
                tb.has_termination = true;
            }
            else if (t.type == TokenType::IDENT && t.value == "parameter") {
                advance();
                std::string pname = expect(TokenType::STRING).value;
                match(TokenType::SEMICOLON);
                tb.termination = {"parameter", pname};
                tb.has_termination = true;
            }
            else if (t.type == TokenType::IDENT && t.value == "uri-append") {
                advance();
                match(TokenType::SEMICOLON);
                tb.termination = {"uri-append", ""};
                tb.has_termination = true;
            }
            else {
                advance();
            }
        }
        return tb;
    }

    StageBlock parse_stage_block() {
        expect(TokenType::LBRACE);
        StageBlock s;
        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                match(TokenType::SEMICOLON);

                if (key == "cleanup") s.cleanup = (val == "true");
                else if (key == "sleep_mask") s.sleep_mask = (val == "true");
                else if (key == "smartinject") s.smartinject = (val == "true");
                else if (key == "stomppe") s.stomppe = (val == "true");
                else if (key == "obfuscate") s.obfuscate = (val == "true");
                else if (key == "userwx") s.userwx = (val == "true");
                else if (key == "magic_mz_x86") s.magic_mz_x86 = val;
                else if (key == "magic_mz_x64") s.magic_mz_x64 = val;
                else if (key == "magic_pe") s.magic_pe = val;
                else if (key == "compile_time") s.compile_time = val;
                else s.raw_settings[key] = val;
            }
            else if (t.type == TokenType::IDENT && (t.value == "transform-x86" || t.value == "transform-x64")) {
                std::string kind = advance().value;
                expect(TokenType::LBRACE);
                while (!match(TokenType::RBRACE) && !is_at_end()) {
                    if (match(TokenType::IDENT)) {
                        std::string arg = advance().value;
                        match(TokenType::SEMICOLON);
                        if (kind == "transform-x86") s.transform_x86_prepend = arg;
                        else s.transform_x64_prepend = arg;
                    } else {
                        advance();
                    }
                }
            } else {
                advance();
            }
        }
        return s;
    }

    ProcessInjectBlock parse_process_inject_block() {
        expect(TokenType::LBRACE);
        ProcessInjectBlock pi;
        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                match(TokenType::SEMICOLON);

                if (key == "allocator") pi.allocator = val;
                else if (key == "min_alloc") pi.min_alloc = std::strtoul(val.c_str(), nullptr, 10);
                else if (key == "startrwx") pi.startrwx = (val == "true");
                else if (key == "userwx") pi.userwx = (val == "true");
                else pi.raw_settings[key] = val;
            }
            else if (t.type == TokenType::IDENT && t.value == "execute") {
                advance();
                expect(TokenType::LBRACE);
                pi.execute_order.clear();
                while (!match(TokenType::RBRACE) && !is_at_end()) {
                    Token e = advance();
                    if (e.type == TokenType::IDENT) {
                        pi.execute_order.push_back(e.value);
                        match(TokenType::SEMICOLON);
                    }
                }
            } else {
                advance();
            }
        }
        return pi;
    }

    PostExBlock parse_post_ex_block() {
        expect(TokenType::LBRACE);
        PostExBlock pe;
        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                match(TokenType::SEMICOLON);

                if (key == "spawnto_x86") pe.spawnto_x86 = val;
                else if (key == "spawnto_x64") pe.spawnto_x64 = val;
                else if (key == "amsi_disable") pe.amsi_disable = (val == "true");
                else if (key == "keylogger") pe.keylogger = val;
                else pe.raw_settings[key] = val;
            } else {
                advance();
            }
        }
        return pe;
    }

    HttpsCertificate parse_https_cert_block() {
        expect(TokenType::LBRACE);
        HttpsCertificate c;
        while (!match(TokenType::RBRACE) && !is_at_end()) {
            Token t = peek();
            if (t.type == TokenType::IDENT && t.value == "set") {
                advance();
                std::string key = expect(TokenType::IDENT).value;
                std::string val = advance().value;
                match(TokenType::SEMICOLON);

                if (key == "CN") c.CN = val;
                else if (key == "O") c.O = val;
                else if (key == "OU") c.OU = val;
                else if (key == "C") c.C = val;
                else if (key == "ST") c.ST = val;
                else if (key == "L") c.L = val;
                else if (key == "validity") c.validity = std::strtoul(val.c_str(), nullptr, 10);
                else c.raw_settings[key] = val;
            } else {
                advance();
            }
        }
        return c;
    }
};

} // namespace OstadC2
