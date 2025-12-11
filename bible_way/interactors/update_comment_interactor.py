import uuid
from bible_way.storage import UserDB
from bible_way.presenters.update_comment_response import UpdateCommentResponse
from rest_framework.response import Response


class UpdateCommentInteractor:
    def __init__(self, storage: UserDB, response: UpdateCommentResponse):
        self.storage = storage
        self.response = response

    def update_comment_interactor(self, comment_id: str, user_id: str, description: str) -> Response:
        if not comment_id:
            return self.response.validation_error_response("Comment ID is required")
        
        if not description or not description.strip():
            return self.response.validation_error_response("Comment description is required")
        
        try:
            comment = self.storage.get_comment_by_id(comment_id)
            if not comment:
                return self.response.comment_not_found_response()
            
            updated_comment = self.storage.update_comment(
                comment_id=comment_id,
                user_id=user_id,
                description=description
            )
            
            return self.response.comment_updated_successfully_response(str(updated_comment.comment_id), is_comment_creator=True)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.comment_not_found_response()
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response(is_comment_creator=False)
            return self.response.error_response(f"Failed to update comment: {error_message}")

