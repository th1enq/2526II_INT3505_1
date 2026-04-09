import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/pagination_demo",
)


@contextmanager
def get_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
