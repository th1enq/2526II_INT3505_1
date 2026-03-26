from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.services.library_service import library_service
from app.utils.pagination import parse_int

users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
def list_users() -> Any:
    """List users
    ---
    tags:
      - Users
    responses:
      200:
        description: Users list
    """
    return jsonify(library_service.list_users())


@users_bp.get("/users/<int:user_id>")
def get_user(user_id: int) -> Any:
    """Get one user detail
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: User detail
      404:
        description: User not found
    """
    payload = library_service.get_user_detail(user_id)
    if not payload:
        return jsonify({"error": "User not found"}), 404
    return jsonify(payload)


@users_bp.get("/users/<int:user_id>/loans")
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
    status = request.args.get("status", "").strip().lower()
    offset = parse_int(request.args.get("offset"), default=0, min_value=0)
    limit = parse_int(request.args.get("limit"), default=10, min_value=1, max_value=50)

    payload = library_service.get_user_loans(user_id=user_id, status=status, offset=offset, limit=limit)

    if payload.get("error"):
        return jsonify(payload), 404

    return jsonify(payload)


@users_bp.post("/users/<int:user_id>/loans")
def create_user_loan(user_id: int) -> Any:
    """Borrow a book for a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
      - name: payload
        in: body
        required: true
        schema:
          type: object
          required: [book_id]
          properties:
            book_id:
              type: integer
            days:
              type: integer
              default: 14
    responses:
      201:
        description: Loan created
      400:
        description: Invalid request
      404:
        description: User or book not found
      409:
        description: Book unavailable
    """
    body = request.get_json(silent=True) or {}
    book_id = body.get("book_id")
    days = parse_int(str(body.get("days", 14)), default=14, min_value=1, max_value=60)

    if not isinstance(book_id, int):
        return jsonify({"error": "book_id must be an integer"}), 400

    payload = library_service.create_user_loan(user_id=user_id, book_id=book_id, days=days)
    if payload.get("error"):
        return jsonify({"error": payload["error"]}), int(payload["status"])

    return jsonify(payload["data"]), 201
