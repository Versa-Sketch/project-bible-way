from bible_way.storage import UserDB
from bible_way.presenters.like_prayer_request_response import LikePrayerRequestResponse
from rest_framework.response import Response


class LikePrayerRequestInteractor:
    def __init__(self, storage: UserDB, response: LikePrayerRequestResponse):
        self.storage = storage
        self.response = response

    def like_prayer_request_interactor(self, prayer_request_id: str, user_id: str) -> Response:
        if not prayer_request_id:
            return self.response.validation_error_response("Prayer request ID is required")
        
        try:
            reaction = self.storage.like_prayer_request(
                prayer_request_id=prayer_request_id,
                user_id=user_id
            )
            
            return self.response.prayer_request_liked_successfully_response(
                reaction_id=str(reaction.reaction_id),
                prayer_request_id=prayer_request_id
            )
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.prayer_request_not_found_response()
            if "already liked" in error_message.lower():
                return self.response.already_liked_response()
            return self.response.error_response(f"Failed to like prayer request: {error_message}")

