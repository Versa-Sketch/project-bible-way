from bible_way.storage import UserDB
from bible_way.presenters.get_all_verses_response import GetAllVersesResponse
from bible_way.models import User
from rest_framework.response import Response


class GetAllVersesInteractor:
    def __init__(self, storage: UserDB, response: GetAllVersesResponse):
        self.storage = storage
        self.response = response

    def get_all_verses_interactor(self, user_id: str = None) -> Response:
        # Validate user_id if provided
        if user_id:
            user_id = user_id.strip()
            if user_id:
                try:
                    User.objects.get(user_id=user_id)
                except User.DoesNotExist:
                    return self.response.validation_error_response("User not found")
        
        try:
            verses_data = self.storage.get_all_verses_with_like_count(user_id=user_id)
            
            return self.response.verses_retrieved_successfully_response(verses_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve verses: {str(e)}")

