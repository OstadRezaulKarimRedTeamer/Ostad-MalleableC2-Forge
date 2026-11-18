"""
Malleable C2 Transform Engine
Implements standard Cobalt Strike & C2 transformation primitives:
base64, base64url, netbios, netbiosu, mask (XOR), prepend, and append.
"""

import base64
import os
from typing import List, Tuple, Union, Any


def netbios_encode(data: bytes, uppercase: bool = False) -> str:
    """Encode bytes using NetBIOS encoding (each byte split into two nibbles + 'a' or 'A')."""
    base_char = ord('A') if uppercase else ord('a')
    out = []
    for b in data:
        low = (b & 0x0F) + base_char
        high = ((b >> 4) & 0x0F) + base_char
        out.append(chr(high))
        out.append(chr(low))
    return "".join(out)


def netbios_decode(text: str, uppercase: bool = False) -> bytes:
    """Decode NetBIOS encoded string back to bytes."""
    base_char = ord('A') if uppercase else ord('a')
    text = text.strip()
    if len(text) % 2 != 0:
        text = text[:-1]
    out = bytearray()
    for i in range(0, len(text), 2):
        high = ord(text[i]) - base_char
        low = ord(text[i + 1]) - base_char
        b = ((high & 0x0F) << 4) | (low & 0x0F)
        out.append(b)
    return bytes(out)


def netbiosu_encode(data: bytes) -> str:
    """NetBIOS uppercase encoding."""
    return netbios_encode(data, uppercase=True)


def netbiosu_decode(text: str) -> bytes:
    """NetBIOS uppercase decoding."""
    return netbios_decode(text, uppercase=True)


def mask_encode(data: bytes, key: bytes = None) -> bytes:
    """
    Cobalt Strike XOR mask transform.
    Prepends a 4-byte random key, then XORs data with the key.
    """
    if key is None or len(key) != 4:
        key = os.urandom(4)
    masked = bytearray(key)
    for i, b in enumerate(data):
        masked.append(b ^ key[i % 4])
    return bytes(masked)


def mask_decode(data: bytes) -> bytes:
    """
    Decode Cobalt Strike XOR mask transform.
    Reads first 4 bytes as key, then unmasks the remainder.
    """
    if len(data) < 4:
        return data
    key = data[:4]
    payload = data[4:]
    unmasked = bytearray()
    for i, b in enumerate(payload):
        unmasked.append(b ^ key[i % 4])
    return bytes(unmasked)


def base64url_encode(data: bytes) -> str:
    """Base64 URL-safe encoding without padding."""
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')


def base64url_decode(text: str) -> bytes:
    """Base64 URL-safe decoding with auto padding."""
    text = text.strip()
    missing_padding = len(text) % 4
    if missing_padding:
        text += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(text.encode('ascii'))


def apply_transform(data: bytes, transform_type: str, arg: str = "") -> bytes:
    """Apply a single transform step."""
    t = transform_type.lower().strip()
    if t == "base64":
        return base64.b64encode(data)
    elif t == "base64url":
        return base64url_encode(data).encode('ascii')
    elif t == "netbios":
        return netbios_encode(data, uppercase=False).encode('ascii')
    elif t == "netbiosu":
        return netbiosu_encode(data).encode('ascii')
    elif t == "mask":
        return mask_encode(data)
    elif t == "prepend":
        return arg.encode('utf-8', errors='ignore') + data
    elif t == "append":
        return data + arg.encode('utf-8', errors='ignore')
    return data


def reverse_transform(data: bytes, transform_type: str, arg: str = "") -> bytes:
    """Reverse a single transform step."""
    t = transform_type.lower().strip()
    if t == "base64":
        try:
            return base64.b64decode(data)
        except Exception:
            return data
    elif t == "base64url":
        try:
            return base64url_decode(data.decode('ascii', errors='ignore'))
        except Exception:
            return data
    elif t == "netbios":
        try:
            return netbios_decode(data.decode('ascii', errors='ignore'), uppercase=False)
        except Exception:
            return data
    elif t == "netbiosu":
        try:
            return netbiosu_decode(data.decode('ascii', errors='ignore'))
        except Exception:
            return data
    elif t == "mask":
        return mask_decode(data)
    elif t == "prepend":
        prefix = arg.encode('utf-8', errors='ignore')
        if data.startswith(prefix):
            return data[len(prefix):]
        return data
    elif t == "append":
        suffix = arg.encode('utf-8', errors='ignore')
        if data.endswith(suffix):
            return data[:-len(suffix)]
        return data
    return data


class TransformPipeline:
    """Executes a sequence of transforms on payload data."""

    def __init__(self, steps: List[Tuple[str, str]] = None):
        # List of (action, argument) e.g. [('mask', ''), ('base64url', ''), ('prepend', 'session=')]
        self.steps = steps or []

    def add_step(self, action: str, arg: str = ""):
        self.steps.append((action, arg))

    def execute(self, data: bytes) -> bytes:
        curr = data
        for action, arg in self.steps:
            curr = apply_transform(curr, action, arg)
        return curr

    def reverse(self, data: bytes) -> bytes:
        curr = data
        # Reverse in reverse order
        for action, arg in reversed(self.steps):
            curr = reverse_transform(curr, action, arg)
        return curr
