from bible_way.storage import UserDB
from bible_way.presenters.get_reading_progress_response import GetReadingProgressResponse
from rest_framework.response import Response
from bible_way.models import Book, User


class GetReadingProgressInteractor:
    def __init__(self, storage: UserDB, response: GetReadingProgressResponse):
        self.storage = storage
        self.response = response

    def get_reading_progress_interactor(self, user_id: str, book_id: str) -> Response:
        # Validate required fields
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        book_id = book_id.strip()
        user_id = user_id.strip()
        
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
            
            # Get reading progress
            reading_progress = self.storage.get_reading_progress_by_user_and_book(
                user_id=user_id,
                book_id=book_id
            )
            
            if not reading_progress:
                return self.response.reading_progress_not_found_response()
            
            # Format response data
            progress_data = {
                "reading_progress_id": str(reading_progress.reading_progress_id),
                "book_id": str(reading_progress.book.book_id),
                "user_id": str(reading_progress.user.user_id),
                "progress_percentage": float(reading_progress.progress_percentage),
                "block_id": reading_progress.block_id if reading_progress.block_id else None,
                "chapter_id": str(reading_progress.chapter_id.chapter_id) if reading_progress.chapter_id else None,
                "last_read_at": reading_progress.last_read_at.isoformat() if reading_progress.last_read_at else None,
                "created_at": reading_progress.created_at.isoformat() if reading_progress.created_at else None,
                "updated_at": reading_progress.updated_at.isoformat() if reading_progress.updated_at else None
            }
            
            return self.response.reading_progress_retrieved_successfully_response(progress_data)
            
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve reading progress: {str(e)}")
