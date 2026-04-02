from flask import Flask
from flask_restx import Api

from core.api.auth_routes import create_auth_namespace
from core.api.oauth_routes import create_oauth_namespace
from core.api.protected_routes import create_protected_namespace
from core.config import Config
from core.extensions import jwt
from core.repositories.book_repository import BookRepository
from core.repositories.oauth_client_repository import OAuthClientRepository
from core.repositories.token_repository import TokenRepository
from core.repositories.user_repository import UserRepository
from core.services.auth_service import AuthService
from core.services.book_service import BookService
from core.services.user_service import UserService


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)

    user_repository = UserRepository()
    book_repository = BookRepository()
    token_repository = TokenRepository()
    oauth_client_repository = OAuthClientRepository()

    auth_service = AuthService(user_repository, token_repository, oauth_client_repository)
    book_service = BookService(book_repository)
    user_service = UserService(user_repository)

    authorizations = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Format: Bearer <your_access_or_refresh_token>",
        },
        "OAuth2Password": {
            "type": "oauth2",
            "flow": "password",
            "tokenUrl": "/oauth/token",
            "scopes": {
                "profile:read": "Read profile",
                "books:read": "Read books",
                "books:write": "Create books",
                "admin:read": "Read admin reports",
            },
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
        return auth_service.is_token_revoked(jwt_payload["jti"])

    api.add_namespace(create_auth_namespace(auth_service), path="/auth")
    api.add_namespace(create_oauth_namespace(auth_service), path="/oauth")
    api.add_namespace(create_protected_namespace(book_service), path="")

    @app.route("/")
    def index():
        return {
            "message": "Flask Authentication & Authorization Demo",
            "swagger": "/swagger",
            "login_demo_users": user_service.get_demo_credentials(),
            "oauth_demo_client": oauth_client_repository.list_demo_clients(),
        }

    return app
