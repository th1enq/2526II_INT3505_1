from flask import Flask, request, jsonify
import jwt
import datetime
import uuid

app = Flask(__name__)

USERS = {
    "alice": "password123",
    "bob":   "secret",
}

JWT_SECRET = "super-secret-key"  
session_store: dict[str, str] = {}   # { session_id -> username }


@app.route("/stateful/login", methods=["POST"])
def stateful_login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) != password:
        return jsonify({"error": "Invalid credentials"}), 401

    session_id = str(uuid.uuid4())
    session_store[session_id] = username
    print(f"[STATEFUL] Session created. Store {len(session_store)} session(s): {session_store}")

    return jsonify({
        "session_id": session_id,
    })


@app.route("/stateful/profile", methods=["GET"])
def stateful_profile():
    session_id = request.headers.get("X-Session-ID")
    username = session_store.get(session_id)     

    if not username:
        return jsonify({"error": "Not authenticated – session is not found"}), 401

    return jsonify({
        "username": username,
    })


@app.route("/stateful/logout", methods=["POST"])
def stateful_logout():
    session_id = request.headers.get("X-Session-ID")
    removed = session_store.pop(session_id, None)

    if removed:
        return jsonify({"message": "Logged out – session removed"})
    return jsonify({"error": "Session not found"}), 404



@app.route("/stateless/login", methods=["POST"])
def stateless_login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) != password:
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({
        "token": token,
    })


@app.route("/stateless/profile", methods=["GET"])
def stateless_profile():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization: Bearer <token>"}), 401

    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token is invalid"}), 401

    return jsonify({
        "username": payload["sub"],
        "expires": payload["exp"],
    })

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    print(f"Server starting at port {port}")
    app.run(debug=False, port=port, use_reloader=False)

