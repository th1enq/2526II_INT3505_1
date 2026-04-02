from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields


def create_auth_namespace(auth_service):
    auth_ns = Namespace("auth", description="Authentication endpoints")

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
            result = auth_service.login(payload["username"], payload["password"])
            if not result:
                return {"message": "Invalid username or password"}, 401
            return result, 200

    @auth_ns.route("/refresh")
    class RefreshResource(Resource):
        @auth_ns.doc(security="BearerAuth")
        @auth_ns.response(200, "Token refreshed", refresh_response)
        @auth_ns.response(401, "Invalid refresh token")
        @jwt_required(refresh=True)
        def post(self):
            identity = get_jwt_identity()
            claims = get_jwt()
            return auth_service.refresh_access_token(identity, claims), 200

    @auth_ns.route("/logout")
    class LogoutResource(Resource):
        @auth_ns.doc(security="BearerAuth")
        @jwt_required()
        def post(self):
            jti = get_jwt()["jti"]
            auth_service.revoke_token(jti)
            return {"message": "Access token revoked"}, 200

    return auth_ns
