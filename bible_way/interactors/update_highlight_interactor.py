from bible_way.storage import UserDB
from bible_way.presenters.update_highlight_response import UpdateHighlightResponse
from bible_way.models import Highlight, User, Book
from rest_framework.response import Response
import uuid


class UpdateHighlightInteractor:
    def __init__(self, storage: UserDB, response: UpdateHighlightResponse):
        self.storage = storage
        self.response = response

    def update_highlight_interactor(self, highlight_id: str, user_id: str, book_id: str,
                                    block_id: str = None, chapter_id: str = None, start_offset: str = None,
                                    end_offset: str = None) -> Response:
        # Validation
        if not highlight_id or not highlight_id.strip():
            return self.response.validation_error_response("highlight_id is required")
        
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        highlight_id = highlight_id.strip()
        user_id = user_id.strip()
        book_id = book_id.strip()
        
        # Validate user exists
        try:
            User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return self.response.validation_error_response("User not found")
        
        # Validate book exists
        try:
            Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return self.response.validation_error_response("Book not found")
        
        # Validate highlight exists and belongs to user
        try:
            highlight = Highlight.objects.get(highlight_id=highlight_id, user__user_id=user_id, book__book_id=book_id)
        except Highlight.DoesNotExist:
            return self.response.highlight_not_found_response()
        
        # If chapter_id is provided but not a valid UUID, generate a new one
        processed_chapter_id = None
        if chapter_id:
            chapter_id = chapter_id.strip()
            if chapter_id:
                try:
                    # Try to validate as UUID
                    uuid.UUID(chapter_id)
                    processed_chapter_id = chapter_id
                except (ValueError, TypeError):
                    # If not a valid UUID, generate a new one
                    processed_chapter_id = str(uuid.uuid4())
        
        # Process block_id if provided
        processed_block_id = None
        if block_id:
            block_id = block_id.strip()
            if block_id:
                try:
                    # Try to validate as UUID
                    uuid.UUID(block_id)
                    processed_block_id = block_id
                except (ValueError, TypeError):
                    # If not a valid UUID, generate a new one
                    processed_block_id = str(uuid.uuid4())
        
        try:
            self.storage.update_highlight(
                highlight_id=highlight_id,
                user_id=user_id,
                book_id=book_id,
                block_id=processed_block_id,
                chapter_id=processed_chapter_id,
                start_offset=start_offset.strip() if start_offset else None,
                end_offset=end_offset.strip() if end_offset else None
            )
            
            return self.response.highlight_updated_successfully_response()
        except Exception as e:
            return self.response.error_response(f"Failed to update highlight: {str(e)}")

