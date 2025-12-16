from bible_way.storage import UserDB
from bible_way.presenters.admin.create_verse_response import CreateVerseResponse
from rest_framework.response import Response


class CreateVerseInteractor:
    def __init__(self, storage: UserDB, response: CreateVerseResponse):
        self.storage = storage
        self.response = response

    def create_verse_interactor(self, title: str, description: str) -> Response:
        if not description or not description.strip():
            return self.response.validation_error_response("Description is required")
        
        try:
            
            verse = self.storage.create_verse(
                title=title,
                description=description
            )
            
            return self.response.verse_created_successfully_response(str(verse.verse_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create verse: {str(e)}")

