from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.services.library_service import library_service
from app.utils.pagination import parse_int

books_bp = Blueprint("books", __name__)


@books_bp.get("/books/<int:book_id>")
def get_book(book_id: int) -> Any:
    """Get one book detail
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Book detail
      404:
        description: Book not found
    """
    payload = library_service.get_book_detail(book_id)
    if not payload:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(payload)


@books_bp.get("/books")
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
    offset = parse_int(request.args.get("offset"), default=0, min_value=0)
    limit = parse_int(request.args.get("limit"), default=10, min_value=1, max_value=50)

    return jsonify(library_service.books_offset_limit(query=query, offset=offset, limit=limit))


@books_bp.get("/books/page")
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
    page = parse_int(request.args.get("page"), default=1, min_value=1)
    size = parse_int(request.args.get("size"), default=10, min_value=1, max_value=50)

    return jsonify(library_service.books_page_based(query=query, page=page, size=size))


@books_bp.get("/books/cursor")
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
    limit = parse_int(request.args.get("limit"), default=10, min_value=1, max_value=50)

    payload = library_service.books_cursor(query=query, cursor=cursor, limit=limit)
    if payload is None:
        return jsonify({"error": "Invalid cursor"}), 400

    return jsonify(payload)
