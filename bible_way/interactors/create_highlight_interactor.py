from bible_way.storage import UserDB
from bible_way.presenters.create_highlight_response import CreateHighlightResponse
from bible_way.models import User, Book
from rest_framework.response import Response


class CreateHighlightInteractor:
    def __init__(self, storage: UserDB, response: CreateHighlightResponse):
        self.storage = storage
        self.response = response

    def create_highlight_interactor(self, user_id: str, book_id: str, block_id: str = None, chapter_id: str = None,
                                   start_offset: str = None, end_offset: str = None,
                                   color: str = 'yellow') -> Response:
        # Validation
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not start_offset or not start_offset.strip():
            return self.response.validation_error_response("start_offset is required")
        
        if not end_offset or not end_offset.strip():
            return self.response.validation_error_response("end_offset is required")
        
        user_id = user_id.strip()
        book_id = book_id.strip()
        
        # Validate user exists
        try:
            User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return self.response.user_not_found_response()
        
        # Validate book exists
        try:
            Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return self.response.book_not_found_response()
        
        try:
            highlight = self.storage.create_highlight(
                user_id=user_id,
                book_id=book_id,
                block_id=block_id.strip() if block_id else None,
                chapter_id=chapter_id.strip() if chapter_id else None,
                start_offset=start_offset.strip(),
                end_offset=end_offset.strip(),
                color=color or 'yellow'
            )
            
            return self.response.highlight_saved_successfully_response(str(highlight.highlight_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create highlight: {str(e)}")

