from flask_jwt_extended import create_access_token, create_refresh_token


class AuthService:
    def __init__(self, user_repository, token_repository):
        self.user_repository = user_repository
        self.token_repository = token_repository

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
