class TokenRepository:
    def __init__(self):
        self._revoked_tokens = set()

    def revoke_token(self, jti):
        self._revoked_tokens.add(jti)

    def is_token_revoked(self, jti):
        return jti in self._revoked_tokens
