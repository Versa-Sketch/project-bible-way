from bible_way.storage import UserDB
from bible_way.presenters.update_reading_note_response import UpdateReadingNoteResponse
from rest_framework.response import Response
import uuid


class UpdateReadingNoteInteractor:
    def __init__(self, storage: UserDB, response: UpdateReadingNoteResponse):
        self.storage = storage
        self.response = response

    def update_reading_note_interactor(self, note_id: str, user_id: str, content: str) -> Response:
        if not note_id or not note_id.strip():
            return self.response.validation_error_response("note_id is required")
        
        if not content or not content.strip():
            return self.response.validation_error_response("content is required")
        
        note_id = note_id.strip()
        content = content.strip()
        
        try:
            # Verify note exists
            reading_note = self.storage.get_reading_note_by_id(note_id)
            if not reading_note:
                return self.response.note_not_found_response()
            
            # Update reading note
            updated_note = self.storage.update_reading_note(
                note_id=note_id,
                user_id=user_id,
                content=content
            )
            
            return self.response.reading_note_updated_successfully_response(str(updated_note.note_id))
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.note_not_found_response()
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to update reading note: {error_message}")
