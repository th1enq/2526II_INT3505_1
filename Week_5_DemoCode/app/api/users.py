from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.services.library_service import library_service
from app.utils.pagination import parse_int

users_bp = Blueprint("users", __name__)


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
