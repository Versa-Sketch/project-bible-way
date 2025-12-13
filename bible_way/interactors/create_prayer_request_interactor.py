from bible_way.storage import UserDB
from bible_way.presenters.create_prayer_request_response import CreatePrayerRequestResponse
from rest_framework.response import Response


class CreatePrayerRequestInteractor:
    def __init__(self, storage: UserDB, response: CreatePrayerRequestResponse):
        self.storage = storage
        self.response = response

    def create_prayer_request_interactor(self, user_id: str, title: str, description: str) -> Response:
        if not title or not title.strip():
            return self.response.validation_error_response("Title is required")
        
        if not description or not description.strip():
            return self.response.validation_error_response("Description is required")
        
        try:
            prayer_request = self.storage.create_prayer_request(
                user_id=user_id,
                title=title,
                description=description
            )
            
            return self.response.prayer_request_created_successfully_response(str(prayer_request.prayer_request_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create prayer request: {str(e)}")

