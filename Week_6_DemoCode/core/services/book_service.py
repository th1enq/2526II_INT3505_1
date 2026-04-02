class BookService:
    def __init__(self, book_repository):
        self.book_repository = book_repository

    def list_books(self):
        return self.book_repository.list_books()

    def create_book(self, title, author):
        return self.book_repository.create_book(title, author)
