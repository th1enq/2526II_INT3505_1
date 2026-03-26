from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.repositories.library_repository import library_repository
from app.utils.pagination import decode_cursor, encode_cursor


class LibraryService:
    @staticmethod
    def search_books(query: str) -> List[Dict[str, Any]]:
        query_norm = query.lower().strip()
        items = library_repository.list_books()
        if not query_norm:
            return items

        return [
            item
            for item in items
            if query_norm in item["title"].lower()
            or query_norm in item["author"].lower()
            or query_norm in item["category"].lower()
        ]

    @staticmethod
    def get_user_loans(user_id: int, status: str, offset: int, limit: int) -> Dict[str, Any]:
        user = library_repository.get_user(user_id)
        if not user:
            return {"error": "User not found"}

        items = library_repository.list_user_loans(user_id)
        if status in {"active", "returned"}:
            items = [item for item in items if item["status"] == status]

        total = len(items)
        page = items[offset : offset + limit]

        return {
            "user": user,
            "pagination": {
                "strategy": "offset-limit",
                "offset": offset,
                "limit": limit,
                "returned": len(page),
                "total": total,
            },
            "data": page,
        }

    @staticmethod
    def books_offset_limit(query: str, offset: int, limit: int) -> Dict[str, Any]:
        filtered = LibraryService.search_books(query)
        page = filtered[offset : offset + limit]

        return {
            "pagination": {
                "strategy": "offset-limit",
                "offset": offset,
                "limit": limit,
                "returned": len(page),
                "total": len(filtered),
                "has_next": offset + limit < len(filtered),
            },
            "data": page,
        }

    @staticmethod
    def books_page_based(query: str, page: int, size: int) -> Dict[str, Any]:
        filtered = LibraryService.search_books(query)
        total = len(filtered)
        total_pages = max((total + size - 1) // size, 1)
        start = (page - 1) * size
        end = start + size
        rows = filtered[start:end]

        return {
            "pagination": {
                "strategy": "page-based",
                "page": page,
                "size": size,
                "returned": len(rows),
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
            },
            "data": rows,
        }

    @staticmethod
    def books_cursor(query: str, cursor: str, limit: int) -> Dict[str, Any] | None:
        filtered = sorted(LibraryService.search_books(query), key=lambda item: item["id"])

        start_idx = 0
        if cursor:
            last_id = decode_cursor(cursor)
            if last_id is None:
                return None

            for idx, book in enumerate(filtered):
                if book["id"] > last_id:
                    start_idx = idx
                    break
            else:
                start_idx = len(filtered)

        rows = filtered[start_idx : start_idx + limit]
        next_cursor = encode_cursor(rows[-1]["id"]) if len(rows) == limit and rows else None

        return {
            "pagination": {
                "strategy": "cursor",
                "cursor": cursor or None,
                "limit": limit,
                "returned": len(rows),
                "next_cursor": next_cursor,
            },
            "data": rows,
        }


library_service = LibraryService()
