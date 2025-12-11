from bible_way.storage import UserDB
from bible_way.presenters.like_post_response import LikePostResponse
from rest_framework.response import Response


class LikePostInteractor:
    def __init__(self, storage: UserDB, response: LikePostResponse):
        self.storage = storage
        self.response = response

    def like_post_interactor(self, post_id: str, user_id: str) -> Response:
        if not post_id:
            return self.response.validation_error_response("Post ID is required")
        
        try:
            reaction = self.storage.like_post(post_id=post_id, user_id=user_id)
            
            return self.response.post_liked_successfully_response(
                reaction_id=str(reaction.reaction_id),
                post_id=post_id
            )
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.post_not_found_response()
            if "already liked" in error_message.lower():
                return self.response.already_liked_response()
            return self.response.error_response(f"Failed to like post: {error_message}")

