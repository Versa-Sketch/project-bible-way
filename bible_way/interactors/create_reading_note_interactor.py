from bible_way.storage import UserDB
from bible_way.presenters.create_reading_note_response import CreateReadingNoteResponse
from rest_framework.response import Response
from bible_way.models import Book, User
import uuid


class CreateReadingNoteInteractor:
    def __init__(self, storage: UserDB, response: CreateReadingNoteResponse):
        self.storage = storage
        self.response = response

    def create_reading_note_interactor(self, user_id: str, book_id: str, content: str,
                                      chapter_id: str = None, block_id: str = None) -> Response:
        # Validate required fields
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        if not content or not content.strip():
            return self.response.validation_error_response("content is required")
        
        if not block_id or not block_id.strip():
            return self.response.validation_error_response("block_id is required")
        
        # Clean inputs
        book_id = book_id.strip()
        user_id = user_id.strip()
        content = content.strip()
        block_id = block_id.strip()
        
        # Handle chapter_id: if not provided, generate a new UUID
        if not chapter_id or not chapter_id.strip():
            chapter_id = str(uuid.uuid4())
        else:
            chapter_id = chapter_id.strip()
        
        try:
            # Verify Book exists
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            # Verify User exists
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return self.response.user_not_found_response()
            
            # Create ReadingNote
            reading_note = self.storage.create_reading_note(
                user_id=user_id,
                book_id=book_id,
                content=content,
                chapter_id=chapter_id,
                block_id=block_id
            )
            
            return self.response.reading_note_created_successfully_response(str(reading_note.note_id))
            
        except Exception as e:
            return self.response.error_response(f"Failed to create reading note: {str(e)}")
