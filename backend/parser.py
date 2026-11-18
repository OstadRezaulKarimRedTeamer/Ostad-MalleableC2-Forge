"""
Malleable C2 Profile Lexer & AST Parser
Parses Cobalt Strike / Havoc Malleable C2 profiles into structured Profile objects.
"""

import re
from typing import List, Tuple, Optional, Any, Dict
from backend.models import (
    Profile, HttpTransaction, ClientSubBlock, ServerSubBlock,
    TransformBlock, TransformAction, TerminationAction,
    Header, Parameter, StageBlock, ProcessInjectBlock, PostExBlock, HttpsCertificate
)


class Token:
    def __init__(self, token_type: str, value: str, line: int):
        self.type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, L{self.line})"


class Lexer:
    """Tokenizes Malleable C2 syntax."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < self.length:
            c = self.text[self.pos]

            # Whitespace
            if c in ' \t\r':
                self.pos += 1
                continue
            if c == '\n':
                self.line += 1
                self.pos += 1
                continue

            # Comments
            if c == '#':
                while self.pos < self.length and self.text[self.pos] != '\n':
                    self.pos += 1
                continue

            # String literal
            if c == '"':
                start_line = self.line
                self.pos += 1
                str_val = []
                while self.pos < self.length:
                    sc = self.text[self.pos]
                    if sc == '\\':
                        self.pos += 1
                        if self.pos < self.length:
                            esc = self.text[self.pos]
                            if esc == 'n':
                                str_val.append('\n')
                            elif esc == 'r':
                                str_val.append('\r')
                            elif esc == 't':
                                str_val.append('\t')
                            elif esc == '"':
                                str_val.append('"')
                            elif esc == '\\':
                                str_val.append('\\')
                            elif esc == 'x':
                                # hex escape e.g. \x90
                                hex_str = self.text[self.pos+1:self.pos+3]
                                self.pos += 2
                                str_val.append(f"\\x{hex_str}")
                            else:
                                str_val.append(esc)
                        self.pos += 1
                    elif sc == '"':
                        self.pos += 1
                        break
                    elif sc == '\n':
                        self.line += 1
                        str_val.append(sc)
                        self.pos += 1
                    else:
                        str_val.append(sc)
                        self.pos += 1
                tokens.append(Token("STRING", "".join(str_val), start_line))
                continue

            # Punctuation
            if c == '{':
                tokens.append(Token("LBRACE", "{", self.line))
                self.pos += 1
                continue
            if c == '}':
                tokens.append(Token("RBRACE", "}", self.line))
                self.pos += 1
                continue
            if c == ';':
                tokens.append(Token("SEMICOLON", ";", self.line))
                self.pos += 1
                continue

            # Identifiers / Keywords
            if c.isalnum() or c in '-_.$%\\/':
                start = self.pos
                while self.pos < self.length and (
                    self.text[self.pos].isalnum() or self.text[self.pos] in '-_.$%\\/:'
                ):
                    self.pos += 1
                val = self.text[start:self.pos]
                tokens.append(Token("IDENT", val, self.line))
                continue

            # Unknown char
            self.pos += 1

        tokens.append(Token("EOF", "", self.line))
        return tokens


class Parser:
    """Parses token stream into AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def match(self, token_type: str, value: Optional[str] = None) -> bool:
        t = self.peek()
        if t.type == token_type:
            if value is None or t.value == value:
                self.advance()
                return True
        return False

    def expect(self, token_type: str, value: Optional[str] = None) -> Token:
        t = self.peek()
        if t.type != token_type or (value is not None and t.value != value):
            raise SyntaxError(f"Line {t.line}: Expected {token_type} '{value or ''}', got {t.type} '{t.value}'")
        return self.advance()

    def parse(self) -> Profile:
        profile = Profile()

        while self.peek().type != "EOF":
            t = self.peek()

            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val_tok = self.advance()
                val = val_tok.value
                self.match("SEMICOLON")

                # Map common top-level
                if key == "sample_name":
                    profile.sample_name = val
                elif key == "sleeptime":
                    try:
                        profile.sleeptime = int(val)
                    except ValueError:
                        pass
                elif key == "jitter":
                    try:
                        profile.jitter = int(val)
                    except ValueError:
                        pass
                elif key == "data_jitter":
                    try:
                        profile.data_jitter = int(val)
                    except ValueError:
                        pass
                elif key == "useragent":
                    profile.useragent = val
                elif key == "pipename":
                    profile.pipename = val
                elif key == "pipename_stager":
                    profile.pipename_stager = val
                else:
                    profile.global_settings[key] = val

            elif t.type == "IDENT" and t.value in ("http-get", "http-post", "http-stager"):
                block_name = self.advance().value
                verb = "GET" if block_name == "http-get" else "POST"
                tx = self._parse_http_block(verb)
                if block_name == "http-get":
                    profile.http_get = tx
                elif block_name == "http-post":
                    profile.http_post = tx
                elif block_name == "http-stager":
                    profile.http_stager = tx

            elif t.type == "IDENT" and t.value == "stage":
                self.advance()
                profile.stage = self._parse_stage_block()

            elif t.type == "IDENT" and t.value == "process-inject":
                self.advance()
                profile.process_inject = self._parse_process_inject_block()

            elif t.type == "IDENT" and t.value == "post-ex":
                self.advance()
                profile.post_ex = self._parse_post_ex_block()

            elif t.type == "IDENT" and t.value == "https-certificate":
                self.advance()
                profile.https_cert = self._parse_https_cert_block()

            else:
                # Skip unknown top-level token or generic block
                if t.type == "IDENT":
                    name = self.advance().value
                    if self.match("LBRACE"):
                        self._skip_block()
                else:
                    self.advance()

        return profile

    def _skip_block(self):
        depth = 1
        while depth > 0 and self.peek().type != "EOF":
            t = self.advance()
            if t.type == "LBRACE":
                depth += 1
            elif t.type == "RBRACE":
                depth -= 1

    def _parse_http_block(self, default_verb: str) -> HttpTransaction:
        self.expect("LBRACE")
        tx = HttpTransaction(verb=default_verb)

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()

            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val_tok = self.advance()
                val = val_tok.value
                # multiple uris can follow set uri "uri1" "uri2" ...
                if key == "uri":
                    tx.uris.append(val)
                    while self.peek().type == "STRING":
                        tx.uris.append(self.advance().value)
                elif key == "verb":
                    tx.verb = val
                self.match("SEMICOLON")

            elif t.type == "IDENT" and t.value == "client":
                self.advance()
                tx.client = self._parse_client_block()

            elif t.type == "IDENT" and t.value == "server":
                self.advance()
                tx.server = self._parse_server_block()

            else:
                self.advance()

        return tx

    def _parse_client_block(self) -> ClientSubBlock:
        self.expect("LBRACE")
        client = ClientSubBlock()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()

            if t.type == "IDENT" and t.value == "header":
                self.advance()
                name = self.expect("STRING").value
                val = self.expect("STRING").value
                self.match("SEMICOLON")
                client.headers.append(Header(name, val))

            elif t.type == "IDENT" and t.value == "parameter":
                self.advance()
                name = self.expect("STRING").value
                val = self.expect("STRING").value
                self.match("SEMICOLON")
                client.parameters.append(Parameter(name, val))

            elif t.type == "IDENT" and t.value in ("metadata", "id", "output"):
                tb_name = self.advance().value
                tb = self._parse_transform_block(tb_name)
                client.transform_blocks[tb_name] = tb

            else:
                self.advance()

        return client

    def _parse_server_block(self) -> ServerSubBlock:
        self.expect("LBRACE")
        server = ServerSubBlock()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()

            if t.type == "IDENT" and t.value == "header":
                self.advance()
                name = self.expect("STRING").value
                val = self.expect("STRING").value
                self.match("SEMICOLON")
                server.headers.append(Header(name, val))

            elif t.type == "IDENT" and t.value == "output":
                self.advance()
                server.output = self._parse_transform_block("output")

            else:
                self.advance()

        return server

    def _parse_transform_block(self, block_type: str) -> TransformBlock:
        self.expect("LBRACE")
        tb = TransformBlock(block_type=block_type)

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()

            if t.type == "IDENT" and t.value in ("base64", "base64url", "netbios", "netbiosu", "mask"):
                action = self.advance().value
                self.match("SEMICOLON")
                tb.transforms.append(TransformAction(action))

            elif t.type == "IDENT" and t.value in ("prepend", "append"):
                action = self.advance().value
                arg_tok = self.advance()
                arg = arg_tok.value
                self.match("SEMICOLON")
                tb.transforms.append(TransformAction(action, arg))

            elif t.type == "IDENT" and t.value == "print":
                self.advance()
                self.match("SEMICOLON")
                tb.termination = TerminationAction("print")

            elif t.type == "IDENT" and t.value == "header":
                self.advance()
                header_name = self.expect("STRING").value
                self.match("SEMICOLON")
                tb.termination = TerminationAction("header", header_name)

            elif t.type == "IDENT" and t.value == "parameter":
                self.advance()
                param_name = self.expect("STRING").value
                self.match("SEMICOLON")
                tb.termination = TerminationAction("parameter", param_name)

            elif t.type == "IDENT" and t.value == "uri-append":
                self.advance()
                self.match("SEMICOLON")
                tb.termination = TerminationAction("uri-append")

            else:
                self.advance()

        return tb

    def _parse_stage_block(self) -> StageBlock:
        self.expect("LBRACE")
        stage = StageBlock()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()
            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val = self.advance().value
                self.match("SEMICOLON")

                if key == "cleanup":
                    stage.cleanup = (val.lower() == "true")
                elif key == "sleep_mask":
                    stage.sleep_mask = (val.lower() == "true")
                elif key == "smartinject":
                    stage.smartinject = (val.lower() == "true")
                elif key == "stomppe":
                    stage.stomppe = (val.lower() == "true")
                elif key == "obfuscate":
                    stage.obfuscate = (val.lower() == "true")
                elif key == "userwx":
                    stage.userwx = (val.lower() == "true")
                elif key == "magic_mz_x86":
                    stage.magic_mz_x86 = val
                elif key == "magic_mz_x64":
                    stage.magic_mz_x64 = val
                elif key == "magic_pe":
                    stage.magic_pe = val
                elif key == "compile_time":
                    stage.compile_time = val
                else:
                    stage.raw_settings[key] = val

            elif t.type == "IDENT" and t.value in ("transform-x86", "transform-x64"):
                kind = self.advance().value
                self.expect("LBRACE")
                while not self.match("RBRACE") and self.peek().type != "EOF":
                    if self.match("IDENT", "prepend"):
                        val = self.advance().value
                        self.match("SEMICOLON")
                        if kind == "transform-x86":
                            stage.transform_x86_prepend = val
                        else:
                            stage.transform_x64_prepend = val
                    else:
                        self.advance()
            else:
                self.advance()

        return stage

    def _parse_process_inject_block(self) -> ProcessInjectBlock:
        self.expect("LBRACE")
        pi = ProcessInjectBlock()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()
            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val = self.advance().value
                self.match("SEMICOLON")

                if key == "allocator":
                    pi.allocator = val
                elif key == "min_alloc":
                    try:
                        pi.min_alloc = int(val)
                    except ValueError:
                        pass
                elif key == "startrwx":
                    pi.startrwx = (val.lower() == "true")
                elif key == "userwx":
                    pi.userwx = (val.lower() == "true")
                else:
                    pi.raw_settings[key] = val

            elif t.type == "IDENT" and t.value == "execute":
                self.advance()
                self.expect("LBRACE")
                order = []
                while not self.match("RBRACE") and self.peek().type != "EOF":
                    t_exec = self.advance()
                    if t_exec.type == "IDENT":
                        order.append(t_exec.value)
                        self.match("SEMICOLON")
                if order:
                    pi.execute_order = order
            else:
                self.advance()

        return pi

    def _parse_post_ex_block(self) -> PostExBlock:
        self.expect("LBRACE")
        pe = PostExBlock()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()
            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val = self.advance().value
                self.match("SEMICOLON")

                if key == "spawnto_x86":
                    pe.spawnto_x86 = val
                elif key == "spawnto_x64":
                    pe.spawnto_x64 = val
                elif key == "amsi_disable":
                    pe.amsi_disable = (val.lower() == "true")
                elif key == "keylogger":
                    pe.keylogger = val
                else:
                    pe.raw_settings[key] = val
            else:
                self.advance()

        return pe

    def _parse_https_cert_block(self) -> HttpsCertificate:
        self.expect("LBRACE")
        cert = HttpsCertificate()

        while not self.match("RBRACE") and self.peek().type != "EOF":
            t = self.peek()
            if t.type == "IDENT" and t.value == "set":
                self.advance()
                key = self.expect("IDENT").value
                val = self.advance().value
                self.match("SEMICOLON")

                if hasattr(cert, key):
                    if key == "validity":
                        try:
                            cert.validity = int(val)
                        except ValueError:
                            pass
                    else:
                        setattr(cert, key, val)
                else:
                    cert.raw_settings[key] = val
            else:
                self.advance()

        return cert


def parse_profile(content: str) -> Profile:
    """Convenience helper to tokenize and parse Malleable C2 profile text."""
    lexer = Lexer(content)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
