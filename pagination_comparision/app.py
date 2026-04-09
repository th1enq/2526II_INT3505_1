from __future__ import annotations

import base64
import datetime as dt
import logging
import time
import uuid
from typing import Optional

from flask import Flask, jsonify, request

from db import get_conn

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True,
)
app.logger.handlers = logging.getLogger().handlers
app.logger.setLevel(logging.INFO)

ITEMS_ORDERED_QUERY = """
    SELECT id, created_at, payload
    FROM items
    ORDER BY created_at DESC, id DESC
    OFFSET %s
    LIMIT %s
"""


def _parse_positive_int(value: str, default: int, max_value: int = 1000) -> int:
    if value is None:
        return default
    parsed = int(value)
    if parsed <= 0:
        raise ValueError("Value must be positive")
    return min(parsed, max_value)


def _encode_cursor(created_at: dt.datetime, item_id: int) -> str:
    raw = f"{created_at.isoformat()}|{item_id}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def _decode_cursor(cursor: str) -> tuple[dt.datetime, int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        created_at_raw, item_id_raw = raw.split("|", 1)
        return dt.datetime.fromisoformat(created_at_raw), int(item_id_raw)
    except Exception as exc:
        raise ValueError("Invalid cursor") from exc


def _execute_timed_query(query: str, params: tuple, strategy: str):
    started = time.perf_counter()
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    elapsed_ms = (time.perf_counter() - started) * 1000
    app.logger.info(
        "strategy=%s query_time_ms=%.3f rows=%s",
        strategy,
        elapsed_ms,
        len(rows),
    )
    return rows


def _execute_ordered_items_window(offset: int, limit: int, strategy: str):
    return _execute_timed_query(ITEMS_ORDERED_QUERY, (offset, limit), strategy=strategy)


def _execute_timed_insert(payload: str, created_at: Optional[dt.datetime]):
    query = """
        INSERT INTO items (created_at, payload)
        VALUES (COALESCE(%s, NOW()), %s)
        RETURNING id, created_at, payload
    """
    started = time.perf_counter()
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(query, (created_at, payload))
        row = cursor.fetchone()
        conn.commit()
    elapsed_ms = (time.perf_counter() - started) * 1000
    app.logger.info(
        "strategy=insert query_time_ms=%.3f inserted_id=%s",
        elapsed_ms,
        row["id"],
    )
    return row


def _parse_created_at(value: object) -> Optional[dt.datetime]:
    if value is None:
        return None
    try:
        return dt.datetime.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError("created_at must be ISO format") from exc


@app.get("/health")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/insert")
def insert_item():
    data = request.get_json(silent=True) or {}
    payload = str(data.get("payload") or f"insert-{uuid.uuid4()}")

    try:
        created_at = _parse_created_at(data.get("created_at"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    row = _execute_timed_insert(payload, created_at)
    return jsonify({"inserted": row}), 201


@app.get("/offset")
def offset_pagination():
    try:
        offset = int(request.args.get("offset", 0))
        limit = _parse_positive_int(request.args.get("limit"), default=50)
        if offset < 0:
            raise ValueError("Offset must be >= 0")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    rows = _execute_ordered_items_window(offset, limit, strategy="offset")

    return jsonify(
        {
            "strategy": "offset",
            "offset": offset,
            "limit": limit,
            "count": len(rows),
            "items": rows,
        }
    )


@app.get("/page")
def page_size_pagination():
    try:
        page = _parse_positive_int(request.args.get("page"), default=1)
        size = _parse_positive_int(request.args.get("size"), default=50)
        offset = (page - 1) * size
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    rows = _execute_ordered_items_window(offset, size, strategy="page-size")

    return jsonify(
        {
            "strategy": "page-size",
            "page": page,
            "size": size,
            "count": len(rows),
            "items": rows,
        }
    )


@app.get("/cursor")
def cursor_pagination():
    try:
        limit = _parse_positive_int(request.args.get("limit"), default=50)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    cursor_token: Optional[str] = request.args.get("cursor")

    base_query = """
        SELECT id, created_at, payload
        FROM items
    """
    params: list = []

    if cursor_token:
        try:
            cursor_created_at, cursor_id = _decode_cursor(cursor_token)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        base_query += " WHERE (created_at, id) < (%s, %s) "
        params.extend([cursor_created_at, cursor_id])

    base_query += " ORDER BY created_at DESC, id DESC LIMIT %s "
    params.append(limit)

    rows = _execute_timed_query(base_query, tuple(params), strategy="cursor")

    next_cursor = None
    if rows:
        last = rows[-1]
        next_cursor = _encode_cursor(last["created_at"], last["id"])

    return jsonify(
        {
            "strategy": "cursor",
            "limit": limit,
            "count": len(rows),
            "next_cursor": next_cursor,
            "items": rows,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
