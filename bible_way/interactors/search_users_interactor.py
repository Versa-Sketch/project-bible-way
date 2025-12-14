from bible_way.storage import UserDB
from bible_way.presenters.search_users_response import SearchUsersResponse
from rest_framework.response import Response


class SearchUsersInteractor:
    def __init__(self, storage: UserDB, response: SearchUsersResponse):
        self.storage = storage
        self.response = response

    def search_users_interactor(self, query: str, limit: int = 20, current_user_id: str = None) -> Response:
        """
        Search users by username with partial matching.
        
        Args:
            query: Search term (minimum 2 characters)
            limit: Maximum number of results (default 20, max 50)
            current_user_id: Optional - to include follow status
            
        Returns:
            Response with list of matching users
        """
        # Validate query
        if not query or not query.strip():
            return self.response.validation_error_response("Search query is required")
        
        query = query.strip()
        

        
        # Validate maximum length
        if len(query) > 50:
            return self.response.validation_error_response("Search query must be less than 50 characters")
        
        # Validate and limit results count
        try:
            limit = int(limit)
            if limit < 1:
                limit = 20
            if limit > 50:
                limit = 50
        except (ValueError, TypeError):
            limit = 20
        
        try:
            # Search users
            result = self.storage.search_users(
                query=query,
                limit=limit,
                current_user_id=current_user_id
            )
            
            return self.response.search_success_response(
                users=result['users'],
                total_count=result['total_count'],
                query=result['query']
            )
        except Exception as e:
            return self.response.error_response(f"Failed to search users: {str(e)}")

