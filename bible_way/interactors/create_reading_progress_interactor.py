from bible_way.storage import UserDB
from bible_way.presenters.create_reading_progress_response import CreateReadingProgressResponse
from rest_framework.response import Response
from bible_way.models import Book, User
from bible_way.models.book_reading import Chapters


class CreateReadingProgressInteractor:
    def __init__(self, storage: UserDB, response: CreateReadingProgressResponse):
        self.storage = storage
        self.response = response

    def create_reading_progress_interactor(self, user_id: str, book_id: str, chapter_id: str = None, progress_percentage: float = 0.0, block_id: str = None) -> Response:
        # Validate required fields
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if progress_percentage is None:
            return self.response.validation_error_response("progress_percentage is required")
        
        try:
            progress_percentage = float(progress_percentage)
            if progress_percentage < 0 or progress_percentage > 100:
                return self.response.validation_error_response("progress_percentage must be between 0 and 100")
        except (ValueError, TypeError):
            return self.response.validation_error_response("progress_percentage must be a valid number")
        
        book_id = book_id.strip()
        chapter_id = chapter_id.strip() if chapter_id else None
        block_id = block_id.strip() if block_id else None
        
        try:
            # Verify book exists
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            # Verify chapter exists if provided
            if chapter_id:
                try:
                    Chapters.objects.get(chapter_id=chapter_id)
                except Chapters.DoesNotExist:
                    return self.response.chapter_not_found_response()
            
            # Verify user exists
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.response.validation_error_response("User not found")
            
            # Create or update reading progress
            reading_progress = self.storage.create_or_update_reading_progress(
                user_id=user_id,
                book_id=book_id,
                chapter_id=chapter_id,
                progress_percentage=progress_percentage,
                block_id=block_id
            )
            
            return self.response.progress_updated_successfully_response(float(reading_progress.progress_percentage))
            
        except Exception as e:
            return self.response.error_response(f"Failed to update reading progress: {str(e)}")
