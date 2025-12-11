from bible_way.storage import UserDB
from bible_way.presenters.unlike_comment_response import UnlikeCommentResponse
from rest_framework.response import Response


class UnlikeCommentInteractor:
    def __init__(self, storage: UserDB, response: UnlikeCommentResponse):
        self.storage = storage
        self.response = response

    def unlike_comment_interactor(self, comment_id: str, user_id: str) -> Response:
        if not comment_id:
            return self.response.validation_error_response("Comment ID is required")
        
        try:
            self.storage.unlike_comment(comment_id=comment_id, user_id=user_id)
            
            return self.response.comment_unliked_successfully_response(comment_id=comment_id)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.comment_not_found_response()
            if "not liked" in error_message.lower():
                return self.response.not_liked_response()
            return self.response.error_response(f"Failed to unlike comment: {error_message}")

