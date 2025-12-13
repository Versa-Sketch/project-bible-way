from bible_way.storage import UserDB
from bible_way.presenters.create_prayer_request_comment_response import CreatePrayerRequestCommentResponse
from rest_framework.response import Response


class CreatePrayerRequestCommentInteractor:
    def __init__(self, storage: UserDB, response: CreatePrayerRequestCommentResponse):
        self.storage = storage
        self.response = response

    def create_prayer_request_comment_interactor(self, prayer_request_id: str, user_id: str, description: str) -> Response:
        if not prayer_request_id:
            return self.response.validation_error_response("Prayer request ID is required")
        
        if not description or not description.strip():
            return self.response.validation_error_response("Description is required")
        
        try:
            comment = self.storage.create_prayer_request_comment(
                prayer_request_id=prayer_request_id,
                user_id=user_id,
                description=description
            )
            
            return self.response.comment_created_successfully_response(str(comment.comment_id))
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.prayer_request_not_found_response()
            return self.response.error_response(f"Failed to create comment: {error_message}")

