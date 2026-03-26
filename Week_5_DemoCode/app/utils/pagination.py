from __future__ import annotations

import base64
from typing import Optional


def parse_int(value: str | None, default: int, min_value: int = 0, max_value: int = 200) -> int:
    try:
        parsed = int(value) if value is not None else default
    except (ValueError, TypeError):
        parsed = default
    return max(min_value, min(parsed, max_value))


def encode_cursor(last_id: int) -> str:
    return base64.urlsafe_b64encode(f"book:{last_id}".encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> Optional[int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        prefix, value = raw.split(":", 1)
        if prefix != "book":
            return None
        return int(value)
    except Exception:
        return None
