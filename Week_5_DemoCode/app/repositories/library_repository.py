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

    def list_users(self) -> List[Dict[str, Any]]:
        return self.users

    def list_books(self) -> List[Dict[str, Any]]:
        return self.books

    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        return next((book for book in self.books if book["id"] == book_id), None)

    def list_loans(self) -> List[Dict[str, Any]]:
        return self.loans

    def list_user_loans(self, user_id: int) -> List[Dict[str, Any]]:
        return [item for item in self.loans if item["user_id"] == user_id]

    def get_loan(self, loan_id: int) -> Optional[Dict[str, Any]]:
        return next((loan for loan in self.loans if loan["id"] == loan_id), None)

    def is_book_on_active_loan(self, book_id: int) -> bool:
        return any(loan for loan in self.loans if loan["book_id"] == book_id and loan["status"] == "active")

    def create_loan(self, user_id: int, book_id: int, days: int = 14) -> Dict[str, Any]:
        next_id = max((loan["id"] for loan in self.loans), default=0) + 1
        loan_date = date.today()
        due_date = loan_date + timedelta(days=days)
        payload = {
            "id": next_id,
            "user_id": user_id,
            "book_id": book_id,
            "loan_date": str(loan_date),
            "due_date": str(due_date),
            "status": "active",
        }
        self.loans.append(payload)
        return payload

    def mark_loan_returned(self, loan_id: int) -> Optional[Dict[str, Any]]:
        loan = self.get_loan(loan_id)
        if not loan:
            return None
        loan["status"] = "returned"
        return loan


library_repository = LibraryRepository()
