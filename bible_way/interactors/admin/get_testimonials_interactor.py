from bible_way.storage import UserDB
from bible_way.presenters.admin.get_testimonials_response import AdminGetTestimonialsResponse
from rest_framework.response import Response


class AdminGetTestimonialsInteractor:
    def __init__(self, storage: UserDB, response: AdminGetTestimonialsResponse):
        self.storage = storage
        self.response = response

    def get_testimonials_interactor(self, limit: int = 10, offset: int = 0, status_filter: str = 'all') -> Response:
        try:
            if limit < 1:
                return self.response.validation_error_response("Limit must be greater than 0")
            
            if offset < 0:
                return self.response.validation_error_response("Offset must be greater than or equal to 0")
            
            if status_filter not in ['all', 'pending', 'verified']:
                return self.response.validation_error_response("Status filter must be 'all', 'pending', or 'verified'")
            
            result = self.storage.get_all_testimonials_admin(limit=limit, offset=offset, status_filter=status_filter)
            
            return self.response.testimonials_retrieved_successfully_response(
                testimonials_data=result['testimonials'],
                pagination_data={
                    'limit': result['limit'],
                    'offset': result['offset'],
                    'total_count': result['total_count'],
                    'has_next': result['has_next'],
                    'has_previous': result['has_previous']
                }
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve testimonials: {str(e)}")

