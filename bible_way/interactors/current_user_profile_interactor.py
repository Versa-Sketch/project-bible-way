from bible_way.models import User
from bible_way.storage import UserDB, UserProfileResponseDTO
from bible_way.presenters.user_profile_response import UserProfileResponse
from rest_framework.response import Response


class CurrentUserProfileInteractor:
    def __init__(self, storage: UserDB, response: UserProfileResponse):
        self.storage = storage
        self.response = response

    def get_current_user_profile_interactor(self, user_id: str) -> Response:
        user = self.storage.get_user_by_user_id(user_id)
        if not user:
            return self.response.user_not_found_response()
        
        response_dto = UserProfileResponseDTO(
            user_id=str(user.user_id),
            user_name=user.username,  # Map username to user_name for API response
            email=user.email,
            country=user.country,
            age=user.age,
            preferred_language=user.preferred_language,
            profile_picture_url=user.profile_picture_url,
            is_admin=user.is_staff
        )

        return self.response.user_profile_success_response(response_dto=response_dto)

