from bible_way.storage import UserDB
from bible_way.presenters.unlike_verse_response import UnlikeVerseResponse
from rest_framework.response import Response


class UnlikeVerseInteractor:
    def __init__(self, storage: UserDB, response: UnlikeVerseResponse):
        self.storage = storage
        self.response = response

    def unlike_verse_interactor(self, verse_id: str, user_id: str) -> Response:
        if not verse_id:
            return self.response.validation_error_response("Verse ID is required")
        
        try:
            self.storage.unlike_verse(verse_id=verse_id, user_id=user_id)
            
            return self.response.verse_unliked_successfully_response(verse_id=verse_id)
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.verse_not_found_response()
            if "haven't liked" in error_message.lower():
                return self.response.not_liked_response()
            return self.response.error_response(f"Failed to unlike verse: {error_message}")
