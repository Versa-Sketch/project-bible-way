from bible_way.storage import UserDB
from bible_way.presenters.get_comments_response import GetCommentsResponse
from rest_framework.response import Response


class GetCommentsInteractor:
    def __init__(self, storage: UserDB, response: GetCommentsResponse):
        self.storage = storage
        self.response = response

    def get_comments_interactor(self, post_id: str) -> Response:
        if not post_id:
            return self.response.validation_error_response("Post ID is required")
        
        try:
            comments_data = self.storage.get_comments_by_post(post_id=post_id)
            
            return self.response.comments_retrieved_successfully_response(
                post_id=post_id,
                comments_data=comments_data
            )
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.post_not_found_response()
            return self.response.error_response(f"Failed to retrieve comments: {error_message}")

