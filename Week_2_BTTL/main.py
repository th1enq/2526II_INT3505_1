from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
        }, 200)


# Fake database
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

# GET /users/<id>
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)

    if not user:
        return jsonify({"error": "User not found"}), 404

    response = make_response(jsonify(user))
    response.headers["Cache-Control"] = "public, max-age=60"
    return response


# POST /users
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    new_user = {
        "id": len(users) + 1,
        "name": data["name"]
    }

    users.append(new_user)

    return jsonify(new_user), 201


# DELETE /users/<id>
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]

    return jsonify({"message": "deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
