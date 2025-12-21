from bible_way.storage import UserDB
from bible_way.presenters.admin.delete_verse_response import DeleteVerseResponse
from rest_framework.response import Response


class DeleteVerseInteractor:
    def __init__(self, storage: UserDB, response: DeleteVerseResponse):
        self.storage = storage
        self.response = response

    def delete_verse_interactor(self, verse_id: str) -> Response:
        if not verse_id or not verse_id.strip():
            return self.response.validation_error_response("verse_id is required")
        
        verse_id = verse_id.strip()
        
        try:
            # Check if verse exists
            verse = self.storage.get_verse_by_id(verse_id)
            if not verse:
                return self.response.verse_not_found_response()
            
            # Delete the verse
            self.storage.delete_verse(verse_id)
            
            return self.response.verse_deleted_successfully_response(verse_id)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.verse_not_found_response()
            return self.response.error_response(f"Failed to delete verse: {error_message}")

