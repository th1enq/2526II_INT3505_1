from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional


class LibraryRepository:
    def __init__(self) -> None:
        self.users: List[Dict[str, Any]] = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ]

        self.books: List[Dict[str, Any]] = [
            {
                "id": i,
                "title": f"Python Patterns Vol {i}",
                "author": f"Author {((i - 1) % 6) + 1}",
                "category": ["backend", "api", "devops", "data"][i % 4],
            }
            for i in range(1, 101)
        ]

        self.loans: List[Dict[str, Any]] = [
            {
                "id": i,
                "user_id": ((i - 1) % 3) + 1,
                "book_id": ((i * 7) % 100) + 1,
                "loan_date": str(date(2026, 1, 1) + timedelta(days=i)),
                "due_date": str(date(2026, 1, 15) + timedelta(days=i)),
                "status": "returned" if i % 4 == 0 else "active",
            }
            for i in range(1, 61)
        ]

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        return next((user for user in self.users if user["id"] == user_id), None)

    def list_books(self) -> List[Dict[str, Any]]:
        return self.books

    def list_user_loans(self, user_id: int) -> List[Dict[str, Any]]:
        return [item for item in self.loans if item["user_id"] == user_id]


library_repository = LibraryRepository()
