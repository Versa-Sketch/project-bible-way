from bible_way.storage import UserDB
from bible_way.presenters.get_testimonials_response import GetTestimonialsResponse
from rest_framework.response import Response


class GetTestimonialsInteractor:
    def __init__(self, storage: UserDB, response: GetTestimonialsResponse):
        self.storage = storage
        self.response = response

    def get_testimonials_interactor(self, limit: int = 10, offset: int = 0) -> Response:
        try:
            if limit < 1:
                return self.response.validation_error_response("Limit must be greater than 0")
            
            if offset < 0:
                return self.response.validation_error_response("Offset must be greater than or equal to 0")
            
            result = self.storage.get_all_testimonials(limit=limit, offset=offset)
            
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

