from bible_way.storage import UserDB
from bible_way.presenters.like_comment_response import LikeCommentResponse
from rest_framework.response import Response


class LikeCommentInteractor:
    def __init__(self, storage: UserDB, response: LikeCommentResponse):
        self.storage = storage
        self.response = response

    def like_comment_interactor(self, comment_id: str, user_id: str) -> Response:
        if not comment_id:
            return self.response.validation_error_response("Comment ID is required")
        
        try:
            reaction = self.storage.like_comment(comment_id=comment_id, user_id=user_id)
            
            return self.response.comment_liked_successfully_response(
                reaction_id=str(reaction.reaction_id),
                comment_id=comment_id
            )
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.comment_not_found_response()
            if "already liked" in error_message.lower():
                return self.response.already_liked_response()
            return self.response.error_response(f"Failed to like comment: {error_message}")

