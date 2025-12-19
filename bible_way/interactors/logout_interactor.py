from bible_way.storage import UserDB
from bible_way.presenters.logout_response import LogoutResponse
from rest_framework.response import Response


class LogoutInteractor:
    def __init__(self, storage: UserDB, response: LogoutResponse):
        self.storage = storage
        self.response = response
    
    def logout_interactor(self, user_id: str) -> Response:
        """
        Logout user
        
        Note: Since JWT tokens are stateless, logout is primarily handled client-side
        by removing tokens from storage. This endpoint validates the user is authenticated
        and returns success. The client should remove access_token and refresh_token.
        
        Args:
            user_id: User ID from authenticated request
            
        Returns:
            Response indicating logout success
        """
        # Verify user exists (optional validation)
        user = self.storage.get_user_by_user_id(user_id)
        if not user:
            return self.response.unauthorized_response()
        
        # Return success response
        # Client should remove tokens from storage (AsyncStorage/localStorage)
        return self.response.logout_success_response()

