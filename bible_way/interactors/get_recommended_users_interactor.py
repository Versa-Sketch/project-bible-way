from bible_way.storage import UserDB
from bible_way.presenters.get_recommended_users_response import GetRecommendedUsersResponse
from rest_framework.response import Response


class GetRecommendedUsersInteractor:
    def __init__(self, storage: UserDB, response: GetRecommendedUsersResponse):
        self.storage = storage
        self.response = response

    def get_recommended_users_interactor(self, user_id: str, limit: int = 20) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        try:
            limit = int(limit)
            if limit < 1:
                limit = 20
            if limit > 20:
                limit = 20
        except (ValueError, TypeError):
            limit = 20
        
        user = self.storage.get_user_by_user_id(user_id)
        if not user:
            return self.response.user_not_found_response()
        
        try:
            result = self.storage.get_recommended_users(
                user_id=user_id,
                limit=limit
            )
            
            return self.response.success_response(
                users=result['users'],
                total_count=result['total_count']
            )
        except Exception as e:
            return self.response.error_response(f"Failed to get recommended users: {str(e)}")

