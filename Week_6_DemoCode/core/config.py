from datetime import timedelta


class Config:
    JWT_SECRET_KEY = "super-secret-key-change-me-at-least-32-bytes"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
