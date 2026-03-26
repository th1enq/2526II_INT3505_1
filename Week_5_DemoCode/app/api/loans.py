from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from app.services.library_service import library_service
from app.utils.pagination import parse_int

loans_bp = Blueprint("loans", __name__)


@loans_bp.get("/loans")
def list_loans() -> Any:
    """List loans with optional status filter
    ---
    tags:
      - Loans
    parameters:
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
        description: Loans list
    """
    status = request.args.get("status", "").strip().lower()
    offset = parse_int(request.args.get("offset"), default=0, min_value=0)
    limit = parse_int(request.args.get("limit"), default=10, min_value=1, max_value=50)

    return jsonify(library_service.list_loans(status=status, offset=offset, limit=limit))


@loans_bp.patch("/loans/<int:loan_id>/return")
def return_loan(loan_id: int) -> Any:
    """Return a borrowed book
    ---
    tags:
      - Loans
    parameters:
      - name: loan_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Loan returned
      404:
        description: Loan not found
      409:
        description: Loan already returned
    """
    payload = library_service.return_loan(loan_id)
    if payload.get("error"):
        return jsonify({"error": payload["error"]}), int(payload["status"])

    return jsonify(payload["data"]), 200
