from bible_way.storage import UserDB
from bible_way.presenters.get_complete_user_profile_response import GetCompleteUserProfileResponse
from rest_framework.response import Response


class GetCompleteUserProfileInteractor:
    def __init__(self, storage: UserDB, response: GetCompleteUserProfileResponse):
        self.storage = storage
        self.response = response

    def get_complete_user_profile_interactor(self, user_id: str, current_user: str | None = None) -> Response:
        # Validate user_id
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        # Validate current_user if provided
        current_user_id = None
        if current_user:
            current_user = current_user.strip()
            if current_user:
                # Verify current_user exists
                current_user_obj = self.storage.get_user_by_user_id(current_user)
                if not current_user_obj:
                    return self.response.validation_error_response("Invalid current_user")
                current_user_id = current_user
        
        # Get complete user profile
        response_dto = self.storage.get_complete_user_profile(user_id=user_id, current_user_id=current_user_id)
        
        if not response_dto:
            return self.response.user_not_found_response()
        
        return self.response.complete_user_profile_success_response(response_dto=response_dto)

