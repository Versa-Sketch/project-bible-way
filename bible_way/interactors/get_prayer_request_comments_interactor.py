from bible_way.storage import UserDB
from bible_way.presenters.get_prayer_request_comments_response import GetPrayerRequestCommentsResponse
from rest_framework.response import Response


class GetPrayerRequestCommentsInteractor:
    def __init__(self, storage: UserDB, response: GetPrayerRequestCommentsResponse):
        self.storage = storage
        self.response = response

    def get_prayer_request_comments_interactor(self, prayer_request_id: str) -> Response:
        if not prayer_request_id:
            return self.response.validation_error_response("Prayer request ID is required")
        
        try:
            comments_data = self.storage.get_prayer_request_comments(prayer_request_id=prayer_request_id)
            
            return self.response.comments_retrieved_successfully_response(
                prayer_request_id=prayer_request_id,
                comments_data=comments_data
            )
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.prayer_request_not_found_response()
            return self.response.error_response(f"Failed to retrieve comments: {error_message}")

