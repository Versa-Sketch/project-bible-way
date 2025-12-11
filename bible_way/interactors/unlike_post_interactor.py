from bible_way.storage import UserDB
from bible_way.presenters.unlike_post_response import UnlikePostResponse
from rest_framework.response import Response


class UnlikePostInteractor:
    def __init__(self, storage: UserDB, response: UnlikePostResponse):
        self.storage = storage
        self.response = response

    def unlike_post_interactor(self, post_id: str, user_id: str) -> Response:
        if not post_id:
            return self.response.validation_error_response("Post ID is required")
        
        try:
            self.storage.unlike_post(post_id=post_id, user_id=user_id)
            
            return self.response.post_unliked_successfully_response(post_id=post_id)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.post_not_found_response()
            if "not liked" in error_message.lower():
                return self.response.not_liked_response()
            return self.response.error_response(f"Failed to unlike post: {error_message}")

