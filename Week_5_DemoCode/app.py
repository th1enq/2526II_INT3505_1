from __future__ import annotations

import base64
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Library API - Resource Tree and Pagination Demo",
    "uiversion": 3,
}
swagger = Swagger(app)

USERS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

BOOKS: List[Dict[str, Any]] = [
    {
        "id": i,
        "title": f"Python Patterns Vol {i}",
        "author": f"Author {((i - 1) % 6) + 1}",
        "category": ["backend", "api", "devops", "data"][i % 4],
    }
    for i in range(1, 101)
]

LOANS: List[Dict[str, Any]] = [
    {
        "id": i,
        "user_id": ((i - 1) % 3) + 1,
        "book_id": ((i * 7) % 100) + 1,
        "loan_date": str(date(2026, 1, 1) + timedelta(days=i)),
        "due_date": str(date(2026, 1, 15) + timedelta(days=i)),
        "status": "returned" if i % 4 == 0 else "active",
    }
    for i in range(1, 61)
]


def _find_user(user_id: int) -> Optional[Dict[str, Any]]:
    return next((user for user in USERS if user["id"] == user_id), None)


def _apply_book_search(items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    query_norm = query.lower().strip()
    if not query_norm:
        return items
    return [
        item
        for item in items
        if query_norm in item["title"].lower()
        or query_norm in item["author"].lower()
        or query_norm in item["category"].lower()
    ]


def _parse_int(name: str, default: int, min_value: int = 0, max_value: int = 200) -> int:
    value = request.args.get(name, default)
    try:
        parsed = int(value)
    except (ValueError, TypeError):
        parsed = default
    return max(min_value, min(parsed, max_value))


def _encode_cursor(last_id: int) -> str:
    return base64.urlsafe_b64encode(f"book:{last_id}".encode("utf-8")).decode("utf-8")


def _decode_cursor(cursor: str) -> Optional[int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        prefix, value = raw.split(":", 1)
        if prefix != "book":
            return None
        return int(value)
    except Exception:
        return None


@app.get("/health")
def health() -> Any:
    """Simple health check
    ---
    tags:
      - System
    responses:
      200:
        description: API is healthy
    """
    return jsonify({"status": "ok"})


@app.get("/users/<int:user_id>/loans")
def user_loans(user_id: int) -> Any:
    """Resource tree example: get loans of one user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [active, returned]
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: User loans list
      404:
        description: User not found
    """
    user = _find_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    status = request.args.get("status", "").strip().lower()
    offset = _parse_int("offset", default=0, min_value=0)
    limit = _parse_int("limit", default=10, min_value=1, max_value=50)

    items = [item for item in LOANS if item["user_id"] == user_id]
    if status in {"active", "returned"}:
        items = [item for item in items if item["status"] == status]

    total = len(items)
    page = items[offset : offset + limit]

    return jsonify(
        {
            "user": user,
            "pagination": {
                "strategy": "offset-limit",
                "offset": offset,
                "limit": limit,
                "returned": len(page),
                "total": total,
            },
            "data": page,
        }
    )


@app.get("/books")
def list_books_offset() -> Any:
    """Search books with offset-limit pagination
    ---
    tags:
      - Books
    parameters:
      - name: q
        in: query
        required: false
        schema:
          type: string
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: Offset-limit result
    """
    query = request.args.get("q", "")
    offset = _parse_int("offset", default=0, min_value=0)
    limit = _parse_int("limit", default=10, min_value=1, max_value=50)

    filtered = _apply_book_search(BOOKS, query)
    page = filtered[offset : offset + limit]

    return jsonify(
        {
            "pagination": {
                "strategy": "offset-limit",
                "offset": offset,
                "limit": limit,
                "returned": len(page),
                "total": len(filtered),
                "has_next": offset + limit < len(filtered),
            },
            "data": page,
        }
    )


@app.get("/books/page")
def list_books_page_based() -> Any:
    """Search books with page-based pagination
    ---
    tags:
      - Books
    parameters:
      - name: q
        in: query
        required: false
        schema:
          type: string
      - name: page
        in: query
        required: false
        schema:
          type: integer
          default: 1
      - name: size
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: Page-based result
    """
    query = request.args.get("q", "")
    page = _parse_int("page", default=1, min_value=1)
    size = _parse_int("size", default=10, min_value=1, max_value=50)

    filtered = _apply_book_search(BOOKS, query)
    total = len(filtered)
    total_pages = max((total + size - 1) // size, 1)
    start = (page - 1) * size
    end = start + size
    rows = filtered[start:end]

    return jsonify(
        {
            "pagination": {
                "strategy": "page-based",
                "page": page,
                "size": size,
                "returned": len(rows),
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
            },
            "data": rows,
        }
    )


@app.get("/books/cursor")
def list_books_cursor() -> Any:
    """Search books with cursor pagination
    ---
    tags:
      - Books
    parameters:
      - name: q
        in: query
        required: false
        schema:
          type: string
      - name: cursor
        in: query
        required: false
        schema:
          type: string
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: Cursor result
      400:
        description: Invalid cursor
    """
    query = request.args.get("q", "")
    cursor = request.args.get("cursor", "")
    limit = _parse_int("limit", default=10, min_value=1, max_value=50)

    filtered = _apply_book_search(BOOKS, query)
    filtered = sorted(filtered, key=lambda item: item["id"])

    start_idx = 0
    if cursor:
        last_id = _decode_cursor(cursor)
        if last_id is None:
            return jsonify({"error": "Invalid cursor"}), 400

        for idx, book in enumerate(filtered):
            if book["id"] > last_id:
                start_idx = idx
                break
        else:
            start_idx = len(filtered)

    rows = filtered[start_idx : start_idx + limit]
    next_cursor = _encode_cursor(rows[-1]["id"]) if len(rows) == limit and rows else None

    return jsonify(
        {
            "pagination": {
                "strategy": "cursor",
                "cursor": cursor or None,
                "limit": limit,
                "returned": len(rows),
                "next_cursor": next_cursor,
            },
            "data": rows,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
