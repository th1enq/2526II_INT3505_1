from flask_jwt_extended import create_access_token, create_refresh_token, decode_token


class AuthService:
    def __init__(self, user_repository, token_repository, oauth_client_repository):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.oauth_client_repository = oauth_client_repository

    def login(self, username, password):
        user = self.user_repository.find_by_username(username)
        if not user or user["password"] != password:
            return None

        claims = {"roles": user["roles"], "scopes": user["scopes"]}
        access_token = create_access_token(identity=username, additional_claims=claims)
        refresh_token = create_refresh_token(identity=username, additional_claims=claims)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "roles": user["roles"],
            "scopes": user["scopes"],
        }

    def refresh_access_token(self, identity, claims):
        new_claims = {
            "roles": claims.get("roles", []),
            "scopes": claims.get("scopes", []),
        }
        new_access_token = create_access_token(identity=identity, additional_claims=new_claims)
        return {"access_token": new_access_token, "token_type": "Bearer"}

    def revoke_token(self, jti):
        self.token_repository.revoke_token(jti)

    def is_token_revoked(self, jti):
        return self.token_repository.is_token_revoked(jti)

    def oauth_password_grant(self, client_id, client_secret, username, password, requested_scope):
        if not self.oauth_client_repository.validate_client(client_id, client_secret, "password"):
            return {
                "error": "invalid_client",
                "error_description": "Client authentication failed",
            }, 401

        user = self.user_repository.find_by_username(username)
        if not user or user["password"] != password:
            return {
                "error": "invalid_grant",
                "error_description": "Invalid resource owner credentials",
            }, 401

        allowed_scopes = set(user["scopes"])
        requested_scopes = set((requested_scope or "").split()) if requested_scope else allowed_scopes
        if not requested_scopes.issubset(allowed_scopes):
            return {
                "error": "invalid_scope",
                "error_description": "Requested scope exceeds user permissions",
            }, 400

        claims = {"roles": user["roles"], "scopes": sorted(requested_scopes)}
        access_token = create_access_token(identity=username, additional_claims=claims)
        refresh_token = create_refresh_token(identity=username, additional_claims=claims)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 900,
            "scope": " ".join(sorted(requested_scopes)),
        }, 200

    def oauth_refresh_grant(self, client_id, client_secret, refresh_token):
        if not self.oauth_client_repository.validate_client(client_id, client_secret, "refresh_token"):
            return {
                "error": "invalid_client",
                "error_description": "Client authentication failed",
            }, 401

        if not refresh_token:
            return {
                "error": "invalid_request",
                "error_description": "refresh_token is required",
            }, 400

        try:
            decoded = decode_token(refresh_token)
        except Exception:
            return {
                "error": "invalid_grant",
                "error_description": "Invalid refresh token",
            }, 401

        if decoded.get("type") != "refresh":
            return {
                "error": "invalid_grant",
                "error_description": "Token is not a refresh token",
            }, 401

        if self.is_token_revoked(decoded.get("jti")):
            return {
                "error": "invalid_grant",
                "error_description": "Refresh token has been revoked",
            }, 401

        identity = decoded.get("sub")
        roles = decoded.get("roles", [])
        scopes = decoded.get("scopes", [])
        new_access_token = create_access_token(
            identity=identity,
            additional_claims={"roles": roles, "scopes": scopes},
        )

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 900,
            "scope": " ".join(scopes),
        }, 200
