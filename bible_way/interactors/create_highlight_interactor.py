from bible_way.storage import UserDB
from bible_way.presenters.create_highlight_response import CreateHighlightResponse
from rest_framework.response import Response
from bible_way.models import Book, User, Chapters


class CreateHighlightInteractor:
    def __init__(self, storage: UserDB, response: CreateHighlightResponse):
        self.storage = storage
        self.response = response

    def create_highlight_interactor(self, user_id: str, book_id: str, chapter_id: str, block_id: str = None,
                                   start_offset: str = None, end_offset: str = None, 
                                   color: str = 'yellow') -> Response:
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not chapter_id or not chapter_id.strip():
            return self.response.validation_error_response("chapter_id is required")
        
        if not start_offset or not start_offset.strip():
            return self.response.validation_error_response("start_offset is required")
        
        if not end_offset or not end_offset.strip():
            return self.response.validation_error_response("end_offset is required")
        
        book_id = book_id.strip()
        chapter_id = chapter_id.strip()
        start_offset = start_offset.strip()
        end_offset = end_offset.strip()
        color = color.strip() if color else 'yellow'
        
        try:
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            try:
                Chapters.objects.get(chapter_id=chapter_id)
            except Chapters.DoesNotExist:
                return self.response.chapter_not_found_response()
            
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.response.validation_error_response("User not found")
            
            highlight = self.storage.create_highlight(
                user_id=user_id,
                book_id=book_id,
                chapter_id=chapter_id,
                block_id=block_id,
                start_offset=start_offset,
                end_offset=end_offset,
                color=color
            )
            
            return self.response.highlight_created_successfully_response(str(highlight.highlight_id))
            
        except Exception as e:
            return self.response.error_response(f"Failed to create highlight: {str(e)}")
