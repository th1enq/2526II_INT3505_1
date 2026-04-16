from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

api_bp = Blueprint("api", __name__)


def _find_item(item_id: int):
    for item in current_app.config["ITEMS"]:
        if item["id"] == item_id:
            return item
    return None


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "flask-demo"}), 200


@api_bp.get("/api/info")
def app_info():
    return jsonify({"name": "flask-demo", "version": "1.0.0"}), 200


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


@api_bp.post("/api/math/sum")
def sum_numbers():
    payload = request.get_json(silent=True) or {}
    numbers = payload.get("numbers")

    if not isinstance(numbers, list) or not numbers:
        return jsonify({"error": "Field 'numbers' must be a non-empty list"}), 400

    if not all(isinstance(number, (int, float)) for number in numbers):
        return jsonify({"error": "All elements in 'numbers' must be numeric"}), 400

    return jsonify({"count": len(numbers), "sum": sum(numbers)}), 200


@api_bp.get("/api/items")
def list_items():
    return jsonify(current_app.config["ITEMS"]), 200


@api_bp.post("/api/items")
def create_item():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Field 'name' is required"}), 400

    item_id = current_app.config["NEXT_ITEM_ID"]
    current_app.config["NEXT_ITEM_ID"] = item_id + 1

    item = {
        "id": item_id,
        "name": name.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    current_app.config["ITEMS"].append(item)

    return jsonify(item), 201


@api_bp.get("/api/items/<int:item_id>")
def get_item(item_id: int):
    item = _find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


@api_bp.delete("/api/items/<int:item_id>")
def delete_item(item_id: int):
    item = _find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    current_app.config["ITEMS"] = [
        existing_item
        for existing_item in current_app.config["ITEMS"]
        if existing_item["id"] != item_id
    ]
    return "", 204
