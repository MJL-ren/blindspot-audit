#!/usr/bin/env python3
"""Render untrusted strings without terminal or bidi control effects."""

from __future__ import annotations

import unicodedata
from typing import Any


UNSAFE_UNICODE_CATEGORIES = {"Cc", "Cf", "Cs", "Zl", "Zp"}


def _visible_escape(character: str) -> str:
    codepoint = ord(character)
    if codepoint <= 0xFF:
        return f"\\x{codepoint:02x}"
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    return f"\\U{codepoint:08x}"


def safe_display_text(value: Any) -> str:
    """Escape control/format characters while preserving ordinary Unicode."""
    text = str(value)
    return "".join(
        _visible_escape(character)
        if unicodedata.category(character) in UNSAFE_UNICODE_CATEGORIES
        else character
        for character in text
    )
