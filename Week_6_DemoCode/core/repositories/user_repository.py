class UserRepository:
    def __init__(self):
        self._users = {
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

    def find_by_username(self, username):
        return self._users.get(username)

    def list_demo_credentials(self):
        return ["alice/alice123", "bob/bob123", "admin/admin123"]
