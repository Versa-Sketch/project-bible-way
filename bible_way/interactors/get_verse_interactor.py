from bible_way.storage import UserDB
from bible_way.presenters.get_verse_response import GetVerseResponse
from rest_framework.response import Response


class GetVerseInteractor:
    def __init__(self, storage: UserDB, response: GetVerseResponse):
        self.storage = storage
        self.response = response

    def get_verse_interactor(self, user_id: str) -> Response:
        try:
            verse_data = self.storage.get_verse(user_id=user_id)
            
            if not verse_data:
                return self.response.verse_not_found_response()
            
            return self.response.verse_retrieved_successfully_response(verse_data=verse_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve verse: {str(e)}")

