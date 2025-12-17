from bible_way.storage import UserDB
from bible_way.presenters.get_specific_user_prayer_requests_response import GetSpecificUserPrayerRequestsResponse
from rest_framework.response import Response


class GetSpecificUserPrayerRequestsInteractor:
    def __init__(self, storage: UserDB, response: GetSpecificUserPrayerRequestsResponse):
        self.storage = storage
        self.response = response

    def get_specific_user_prayer_requests_interactor(self, user_id: str, current_user_id: str, limit: int = 10, offset: int = 0) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        if limit < 1:
            return self.response.validation_error_response("Limit must be greater than 0")
        
        if offset < 0:
            return self.response.validation_error_response("Offset must be greater than or equal to 0")
        
        target_user = self.storage.get_user_by_user_id(user_id)
        if not target_user:
            return self.response.user_not_found_response()
        
        try:
            result = self.storage.get_user_prayer_requests(
                user_id=user_id,
                limit=limit,
                offset=offset,
                current_user_id=current_user_id
            )
            
            return self.response.prayer_requests_retrieved_successfully_response(
                prayer_requests_data=result['prayer_requests'],
                pagination_data={
                    'limit': result['limit'],
                    'offset': result['offset'],
                    'total_count': result['total_count'],
                    'has_next': result['has_next'],
                    'has_previous': result['has_previous']
                }
            )
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve prayer requests: {str(e)}")

