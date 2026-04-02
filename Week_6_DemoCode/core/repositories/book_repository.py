class BookRepository:
    def __init__(self):
        self._books = [
            {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
            {"id": 2, "title": "Fluent Python", "author": "Luciano Ramalho"},
        ]

    def list_books(self):
        return self._books

    def create_book(self, title, author):
        new_book = {
            "id": len(self._books) + 1,
            "title": title,
            "author": author,
        }
        self._books.append(new_book)
        return new_book
