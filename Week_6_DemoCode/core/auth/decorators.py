from functools import wraps

from flask_jwt_extended import get_jwt


def role_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_roles = set(claims.get("roles", []))
            if not token_roles.intersection(required_roles):
                return {
                    "message": "Forbidden: missing required role",
                    "required_roles": list(required_roles),
                    "token_roles": list(token_roles),
                }, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def scope_required(*required_scopes):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            token_scopes = set(claims.get("scopes", []))
            missing = [scope for scope in required_scopes if scope not in token_scopes]
            if missing:
                return {
                    "message": "Forbidden: missing required scope",
                    "required_scopes": list(required_scopes),
                    "missing_scopes": missing,
                }, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
