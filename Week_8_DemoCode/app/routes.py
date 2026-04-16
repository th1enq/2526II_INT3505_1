from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "flask-demo"}), 200


@api_bp.post("/api/echo")
def echo_message():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")

    if not message:
        return jsonify({"error": "Field 'message' is required"}), 400

    return (
        jsonify(
            {
                "message": message,
                "received_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )
