from bible_way.storage import UserDB
from bible_way.presenters.get_user_followers_response import GetUserFollowersResponse
from rest_framework.response import Response


class GetUserFollowersInteractor:
    def __init__(self, storage: UserDB, response: GetUserFollowersResponse):
        self.storage = storage
        self.response = response

    def get_user_followers_interactor(self, user_id: str) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        # Verify user exists
        user = self.storage.get_user_by_user_id(user_id)
        if not user:
            return self.response.user_not_found_response()
        
        try:
            result = self.storage.get_user_followers(user_id=user_id)
            
            return self.response.success_response(
                users=result['users'],
                total_count=result['total_count']
            )
        except Exception as e:
            return self.response.error_response(f"Failed to get user followers: {str(e)}")

