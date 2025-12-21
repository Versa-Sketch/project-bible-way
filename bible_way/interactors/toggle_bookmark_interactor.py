from bible_way.storage import UserDB
from bible_way.presenters.toggle_bookmark_response import ToggleBookmarkResponse
from rest_framework.response import Response
from bible_way.models import Book, User


class ToggleBookmarkInteractor:
    def __init__(self, storage: UserDB, response: ToggleBookmarkResponse):
        self.storage = storage
        self.response = response

    def toggle_bookmark_interactor(self, user_id: str, book_id: str) -> Response:
        # Validate required fields
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        book_id = book_id.strip()
        
        try:
            # Verify book exists
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            # Verify user exists
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.response.validation_error_response("User not found")
            
            # Check if bookmark already exists
            existing_bookmark = self.storage.get_bookmark_by_user_and_book(
                user_id=user_id,
                book_id=book_id
            )
            
            if existing_bookmark:
                # Bookmark exists, delete it
                self.storage.delete_bookmark(
                    bookmark_id=str(existing_bookmark.bookmark_id),
                    user_id=user_id
                )
                return self.response.bookmark_deleted_successfully_response()
            else:
                # Bookmark doesn't exist, create it
                bookmark = self.storage.create_bookmark(
                    user_id=user_id,
                    book_id=book_id
                )
                return self.response.bookmark_created_successfully_response(str(bookmark.bookmark_id))
            
        except Exception as e:
            return self.response.error_response(f"Failed to toggle bookmark: {str(e)}")
