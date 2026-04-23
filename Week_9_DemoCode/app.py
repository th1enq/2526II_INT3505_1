from typing import Any

from api_demo import create_app
from api_demo.services.openapi import generate_openapi_spec as _generate_openapi_spec

app = create_app()


def generate_openapi_spec() -> dict[str, Any]:
    return _generate_openapi_spec(app)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
