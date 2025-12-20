from bible_way.storage import UserDB
from bible_way.presenters.create_bookmark_response import CreateBookmarkResponse
from rest_framework.response import Response
from bible_way.models import Book, User


class CreateBookmarkInteractor:
    def __init__(self, storage: UserDB, response: CreateBookmarkResponse):
        self.storage = storage
        self.response = response

    def create_bookmark_interactor(self, user_id: str, book_id: str) -> Response:
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        book_id = book_id.strip()
        
        try:
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.response.validation_error_response("User not found")
            
            # Check if bookmark already exists for this user and book
            existing_bookmark = self.storage.get_bookmark_by_user_and_book(
                user_id=user_id,
                book_id=book_id
            )
            if existing_bookmark:
                return self.response.already_bookmarked_response()
            
            bookmark = self.storage.create_bookmark(
                user_id=user_id,
                book_id=book_id
            )
            
            return self.response.bookmark_created_successfully_response(str(bookmark.bookmark_id))
            
        except Exception as e:
            return self.response.error_response(f"Failed to create bookmark: {str(e)}")
