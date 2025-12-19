from bible_way.storage import UserDB
from bible_way.presenters.like_verse_response import LikeVerseResponse
from rest_framework.response import Response


class LikeVerseInteractor:
    def __init__(self, storage: UserDB, response: LikeVerseResponse):
        self.storage = storage
        self.response = response

    def like_verse_interactor(self, verse_id: str, user_id: str) -> Response:
        if not verse_id:
            return self.response.validation_error_response("Verse ID is required")
        
        try:
            reaction = self.storage.like_verse(verse_id=verse_id, user_id=user_id)
            
            return self.response.verse_liked_successfully_response(
                reaction_id=str(reaction.reaction_id),
                verse_id=verse_id
            )
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.verse_not_found_response()
            if "already liked" in error_message.lower():
                return self.response.already_liked_response()
            return self.response.error_response(f"Failed to like verse: {error_message}")
