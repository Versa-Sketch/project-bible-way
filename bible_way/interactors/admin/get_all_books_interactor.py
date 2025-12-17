from bible_way.storage import UserDB
from bible_way.presenters.admin.get_all_books_response import GetAllBooksResponse
from rest_framework.response import Response


class GetAllBooksInteractor:
    def __init__(self, storage: UserDB, response: GetAllBooksResponse):
        self.storage = storage
        self.response = response

    def get_all_books_interactor(self, limit: int = None, offset: int = 0) -> Response:
        # Validate limit
        if limit is not None:
            try:
                limit = int(limit)
                if limit < 1:
                    return self.response.validation_error_response("Limit must be greater than 0")
                if limit > 100:
                    limit = 100  # Cap at 100
            except (ValueError, TypeError):
                return self.response.validation_error_response("Invalid limit value")
        
        # Validate offset
        try:
            offset = int(offset) if offset else 0
            if offset < 0:
                return self.response.validation_error_response("Offset must be greater than or equal to 0")
        except (ValueError, TypeError):
            offset = 0
        
        # Default ordering: newest first
        order_by = '-created_at'
        
        try:
            result = self.storage.get_all_books_admin(
                limit=limit,
                offset=offset,
                order_by=order_by
            )
            
            return self.response.books_retrieved_successfully_response(
                books_data=result['books'],
                total_count=result['total_count'],
                limit=limit,
                offset=offset
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve books: {str(e)}")

