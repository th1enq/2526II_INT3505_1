class OAuthClientRepository:
    def __init__(self):
        self._clients = {
            "demo-client": {
                "client_secret": "demo-secret",
                "allowed_grants": ["password", "refresh_token"],
            }
        }

    def validate_client(self, client_id, client_secret, grant_type):
        client = self._clients.get(client_id)
        if not client:
            return False
        if client["client_secret"] != client_secret:
            return False
        return grant_type in client["allowed_grants"]

    def list_demo_clients(self):
        return ["demo-client/demo-secret"]
