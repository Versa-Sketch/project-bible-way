from bible_way.storage import UserDB
from bible_way.presenters.get_all_books_response import GetAllBooksResponse
from rest_framework.response import Response


class GetAllBooksInteractor:
    def __init__(self, storage: UserDB, response: GetAllBooksResponse):
        self.storage = storage
        self.response = response

    def get_all_books_interactor(self) -> Response:
        try:
            books = self.storage.get_all_books()
            
            books_data = []
            for book in books:
                books_data.append({
                    "book_id": str(book.book_id),
                    "title": book.title
                })
            
            return self.response.books_retrieved_successfully_response(
                books_data=books_data,
                total_count=len(books_data)
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve books: {str(e)}")
