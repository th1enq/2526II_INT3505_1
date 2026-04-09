from datetime import datetime, timezone

import pytest

from app import _decode_cursor, _encode_cursor, _parse_positive_int


def test_parse_positive_int_default_when_none():
    assert _parse_positive_int(None, default=50) == 50


def test_parse_positive_int_cap_max():
    assert _parse_positive_int("9999", default=50, max_value=1000) == 1000


def test_parse_positive_int_invalid():
    with pytest.raises(ValueError):
        _parse_positive_int("0", default=50)


def test_cursor_roundtrip():
    created_at = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
    item_id = 123
    token = _encode_cursor(created_at, item_id)
    decoded_created_at, decoded_id = _decode_cursor(token)

    assert decoded_created_at == created_at
    assert decoded_id == item_id


def test_decode_cursor_invalid():
    with pytest.raises(ValueError):
        _decode_cursor("not-a-valid-base64")
