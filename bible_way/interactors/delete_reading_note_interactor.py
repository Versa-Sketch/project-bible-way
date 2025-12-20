from bible_way.storage import UserDB
from bible_way.presenters.delete_reading_note_response import DeleteReadingNoteResponse
from rest_framework.response import Response


class DeleteReadingNoteInteractor:
    def __init__(self, storage: UserDB, response: DeleteReadingNoteResponse):
        self.storage = storage
        self.response = response

    def delete_reading_note_interactor(self, note_id: str, user_id: str) -> Response:
        if not note_id or not note_id.strip():
            return self.response.validation_error_response("note_id is required")
        
        note_id = note_id.strip()
        
        try:
            note = self.storage.get_reading_note_by_id(note_id)
            if not note:
                return self.response.note_not_found_response()
            
            if str(note.user.user_id) != user_id:
                return self.response.unauthorized_response()
            
            self.storage.delete_reading_note(note_id=note_id, user_id=user_id)
            
            return self.response.note_deleted_successfully_response()
            
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower() or "does not exist" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to delete note: {error_message}")
