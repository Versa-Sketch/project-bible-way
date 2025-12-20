from bible_way.storage import UserDB
from bible_way.presenters.get_reading_notes_response import GetReadingNotesResponse
from rest_framework.response import Response
from bible_way.models import Book


class GetReadingNotesInteractor:
    def __init__(self, storage: UserDB, response: GetReadingNotesResponse):
        self.storage = storage
        self.response = response

    def get_reading_notes_interactor(self, user_id: str, book_id: str) -> Response:
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        book_id = book_id.strip()
        user_id = user_id.strip()
        
        try:
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            reading_notes = self.storage.get_reading_notes_by_user_and_book(user_id=user_id, book_id=book_id)
            
            reading_notes_data = []
            for note in reading_notes:
                reading_notes_data.append({
                    "note_id": str(note.note_id),
                    "book_id": str(note.book.book_id),
                    "user_id": str(note.user.user_id),
                    "content": note.content,
                    "chapter_id": str(note.chapter_id) if note.chapter_id else None
                })
            
            return self.response.reading_notes_retrieved_successfully_response(reading_notes_data)
            
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve reading notes: {str(e)}")
