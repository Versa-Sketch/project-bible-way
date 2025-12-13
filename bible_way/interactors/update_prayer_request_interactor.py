from bible_way.storage import UserDB
from bible_way.presenters.update_prayer_request_response import UpdatePrayerRequestResponse
from rest_framework.response import Response


class UpdatePrayerRequestInteractor:
    def __init__(self, storage: UserDB, response: UpdatePrayerRequestResponse):
        self.storage = storage
        self.response = response

    def update_prayer_request_interactor(self, prayer_request_id: str, user_id: str, title: str = None, description: str = None) -> Response:
        if not prayer_request_id:
            return self.response.validation_error_response("Prayer request ID is required")
        
        try:
            self.storage.update_prayer_request(
                prayer_request_id=prayer_request_id,
                user_id=user_id,
                title=title,
                description=description
            )
            
            return self.response.prayer_request_updated_successfully_response()
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.prayer_request_not_found_response()
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to update prayer request: {error_message}")

