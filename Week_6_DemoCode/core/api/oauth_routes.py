from flask import request
from flask_restx import Namespace, Resource


def create_oauth_namespace(auth_service):
    oauth_ns = Namespace("oauth", description="OAuth2 endpoints")

    @oauth_ns.route("/token")
    class OAuthTokenResource(Resource):
        @oauth_ns.doc(
            params={
                "grant_type": "password or refresh_token",
                "client_id": "OAuth2 client id",
                "client_secret": "OAuth2 client secret",
                "username": "Required for password grant",
                "password": "Required for password grant",
                "scope": "Optional space-delimited scopes",
                "refresh_token": "Required for refresh_token grant",
            }
        )
        @oauth_ns.response(200, "OAuth token issued")
        @oauth_ns.response(400, "OAuth error")
        @oauth_ns.response(401, "OAuth client/user authentication failed")
        def post(self):
            # Accept both query params and form-data for easier Swagger/curl testing.
            request_data = request.values
            grant_type = request_data.get("grant_type")
            client_id = request_data.get("client_id")
            client_secret = request_data.get("client_secret")

            if grant_type == "password":
                return auth_service.oauth_password_grant(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=request_data.get("username"),
                    password=request_data.get("password"),
                    requested_scope=request_data.get("scope"),
                )

            if grant_type == "refresh_token":
                return auth_service.oauth_refresh_grant(
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=request_data.get("refresh_token"),
                )

            return {
                "error": "unsupported_grant_type",
                "error_description": "grant_type must be password or refresh_token",
            }, 400

    return oauth_ns
