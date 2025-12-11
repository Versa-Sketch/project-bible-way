from bible_way.storage import UserDB
from bible_way.presenters.create_comment_response import CreateCommentResponse
from rest_framework.response import Response


class CreateCommentInteractor:
    def __init__(self, storage: UserDB, response: CreateCommentResponse):
        self.storage = storage
        self.response = response

    def create_comment_interactor(self, post_id: str, user_id: str, description: str) -> Response:
        if not post_id:
            return self.response.validation_error_response("Post ID is required")
        
        if not description or not description.strip():
            return self.response.validation_error_response("Comment description is required")
        
        try:
            comment = self.storage.create_comment(
                post_id=post_id,
                user_id=user_id,
                description=description
            )
            
            return self.response.comment_created_successfully_response(str(comment.comment_id))
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.post_not_found_response()
            return self.response.error_response(f"Failed to create comment: {error_message}")

