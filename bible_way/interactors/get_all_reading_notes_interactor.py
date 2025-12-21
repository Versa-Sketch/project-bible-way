from bible_way.storage import UserDB
from bible_way.presenters.get_all_reading_notes_response import GetAllReadingNotesResponse
from rest_framework.response import Response


class GetAllReadingNotesInteractor:
    def __init__(self, storage: UserDB, response: GetAllReadingNotesResponse):
        self.storage = storage
        self.response = response

    def get_all_reading_notes_interactor(self, user_id: str) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        try:
            notes_data = self.storage.get_all_reading_notes_by_user(user_id=user_id)
            return self.response.reading_notes_retrieved_successfully_response(notes_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve reading notes: {str(e)}")

