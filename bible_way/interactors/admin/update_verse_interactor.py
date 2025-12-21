from bible_way.storage import UserDB
from bible_way.presenters.admin.update_verse_response import UpdateVerseResponse
from rest_framework.response import Response


class UpdateVerseInteractor:
    def __init__(self, storage: UserDB, response: UpdateVerseResponse):
        self.storage = storage
        self.response = response

    def update_verse_interactor(self, verse_id: str, title: str = None, description: str = None) -> Response:
        if not verse_id or not verse_id.strip():
            return self.response.validation_error_response("verse_id is required")
        
        verse_id = verse_id.strip()
        
        # Check if verse exists
        verse = self.storage.get_verse_by_id(verse_id)
        if not verse:
            return self.response.verse_not_found_response()
        
        try:
            # Update verse (only provided fields)
            updated_verse = self.storage.update_verse(
                verse_id=verse_id,
                title=title,
                description=description
            )
            
            # Build response data
            verse_data = {
                "verse_id": str(updated_verse.verse_id),
                "title": updated_verse.title,
                "description": updated_verse.description,
                "created_at": updated_verse.created_at.isoformat() if updated_verse.created_at else None,
                "updated_at": updated_verse.updated_at.isoformat() if updated_verse.updated_at else None
            }
            
            return self.response.verse_updated_successfully_response(verse_data)
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.verse_not_found_response()
            return self.response.error_response(f"Failed to update verse: {error_message}")

