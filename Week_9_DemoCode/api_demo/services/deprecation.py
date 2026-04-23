from flask import Response

from api_demo.config import DEPRECATION_HEADERS


def attach_deprecation_headers(response: Response) -> Response:
    for header, value in DEPRECATION_HEADERS.items():
        response.headers[header] = value
    return response
