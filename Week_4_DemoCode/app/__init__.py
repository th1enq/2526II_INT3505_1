from flask import Flask
from flask_smorest import Api

from .routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.update(
        API_TITLE="Book Management API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/",
        OPENAPI_SWAGGER_UI_PATH="/docs",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        OPENAPI_JSON_PATH="openapi.json",
        API_SPEC_OPTIONS={
            "servers": [
                {
                    "url": "http://127.0.0.1:5001",
                    "description": "Local",
                },
                {
                    "url": "http://159.223.38.173:5001",
                    "description": "Server",
                },
            ]
        },
    )

    api = Api(app)
    register_routes(api)
    return app
