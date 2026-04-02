from datetime import timedelta
from functools import wraps

from flask import Flask
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Api, Namespace, Resource, fields


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-me-at-least-32-bytes"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)

# In-memory revoked token store (for demo only).
revoked_tokens = set()

# Fake user database for demo purposes.
USERS = {
    "alice": {
        "password": "alice123",
        "roles": ["user"],
        "scopes": ["profile:read", "books:read"],
    },
    "bob": {
        "password": "bob123",
        "roles": ["user", "librarian"],
        "scopes": ["profile:read", "books:read", "books:write"],
    },
    "admin": {
        "password": "admin123",
        "roles": ["admin"],
        "scopes": [
            "profile:read",
            "books:read",
            "books:write",
            "admin:read",
        ],
    },
}

BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Fluent Python", "author": "Luciano Ramalho"},
]


authorizations = {
    "BearerAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Format: Bearer <your_access_or_refresh_token>",
    }
}

api = Api(
    app,
    version="1.0.0",
    title="Flask AuthN/AuthZ Demo API",
    description="Demo Authentication + Authorization using JWT, Refresh Token, Roles, and Scopes.",
    doc="/swagger",
    authorizations=authorizations,
)


@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in revoked_tokens


def role_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_roles = set(claims.get("roles", []))
            if not token_roles.intersection(required_roles):
                return {
                    "message": "Forbidden: missing required role",
                    "required_roles": list(required_roles),
                    "token_roles": list(token_roles),
                }, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def scope_required(*required_scopes):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_scopes = set(claims.get("scopes", []))
            missing = [scope for scope in required_scopes if scope not in token_scopes]
            if missing:
                return {
                    "message": "Forbidden: missing required scope",
                    "required_scopes": list(required_scopes),
                    "missing_scopes": missing,
                }, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


auth_ns = Namespace("auth", description="Authentication endpoints")
api.add_namespace(auth_ns, path="/auth")

login_request = auth_ns.model(
    "LoginRequest",
    {
        "username": fields.String(required=True, example="alice"),
        "password": fields.String(required=True, example="alice123"),
    },
)

refresh_response = auth_ns.model(
    "RefreshResponse",
    {
        "access_token": fields.String,
        "token_type": fields.String(example="Bearer"),
    },
)

login_response = auth_ns.model(
    "LoginResponse",
    {
        "access_token": fields.String,
        "refresh_token": fields.String,
        "token_type": fields.String(example="Bearer"),
        "roles": fields.List(fields.String),
        "scopes": fields.List(fields.String),
    },
)


@auth_ns.route("/login")
class LoginResource(Resource):
    @auth_ns.expect(login_request, validate=True)
    @auth_ns.response(200, "Login successful", login_response)
    @auth_ns.response(401, "Invalid credentials")
    def post(self):
        payload = auth_ns.payload
        username = payload["username"]
        password = payload["password"]

        user = USERS.get(username)
        if not user or user["password"] != password:
            return {"message": "Invalid username or password"}, 401

        claims = {"roles": user["roles"], "scopes": user["scopes"]}
        access_token = create_access_token(identity=username, additional_claims=claims)
        refresh_token = create_refresh_token(identity=username, additional_claims=claims)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "roles": user["roles"],
            "scopes": user["scopes"],
        }, 200


@auth_ns.route("/refresh")
class RefreshResource(Resource):
    @auth_ns.doc(security="BearerAuth")
    @auth_ns.response(200, "Token refreshed", refresh_response)
    @auth_ns.response(401, "Invalid refresh token")
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        claims = get_jwt()

        new_claims = {
            "roles": claims.get("roles", []),
            "scopes": claims.get("scopes", []),
        }
        new_access_token = create_access_token(identity=identity, additional_claims=new_claims)

        return {"access_token": new_access_token, "token_type": "Bearer"}, 200


@auth_ns.route("/logout")
class LogoutResource(Resource):
    @auth_ns.doc(security="BearerAuth")
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        revoked_tokens.add(jti)
        return {"message": "Access token revoked"}, 200


api_ns = Namespace("api", description="Protected business endpoints")
api.add_namespace(api_ns, path="")

book_model = api_ns.model(
    "Book",
    {
        "id": fields.Integer,
        "title": fields.String,
        "author": fields.String,
    },
)

book_create_request = api_ns.model(
    "BookCreateRequest",
    {
        "title": fields.String(required=True),
        "author": fields.String(required=True),
    },
)


@api_ns.route("/me")
class MeResource(Resource):
    @api_ns.doc(security="BearerAuth")
    @jwt_required()
    @scope_required("profile:read")
    def get(self):
        return {
            "username": get_jwt_identity(),
            "roles": get_jwt().get("roles", []),
            "scopes": get_jwt().get("scopes", []),
        }, 200


@api_ns.route("/admin/reports")
class AdminReportsResource(Resource):
    @api_ns.doc(security="BearerAuth")
    @jwt_required()
    @role_required("admin")
    @scope_required("admin:read")
    def get(self):
        return {
            "message": "Sensitive admin report data",
            "requested_by": get_jwt_identity(),
        }, 200


@api_ns.route("/books")
class BooksResource(Resource):
    @api_ns.doc(security="BearerAuth")
    @api_ns.marshal_list_with(book_model)
    @jwt_required()
    @scope_required("books:read")
    def get(self):
        return BOOKS, 200

    @api_ns.doc(security="BearerAuth")
    @api_ns.expect(book_create_request, validate=True)
    @jwt_required()
    @scope_required("books:write")
    @role_required("librarian", "admin")
    def post(self):
        payload = api_ns.payload
        new_book = {
            "id": len(BOOKS) + 1,
            "title": payload["title"],
            "author": payload["author"],
        }
        BOOKS.append(new_book)
        return new_book, 201


@app.route("/")
def index():
    return {
        "message": "Flask Authentication & Authorization Demo",
        "swagger": "/swagger",
        "login_demo_users": ["alice/alice123", "bob/bob123", "admin/admin123"],
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
