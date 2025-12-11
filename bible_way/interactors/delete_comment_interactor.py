import uuid
from bible_way.storage import UserDB
from bible_way.presenters.delete_comment_response import DeleteCommentResponse
from rest_framework.response import Response


class DeleteCommentInteractor:
    def __init__(self, storage: UserDB, response: DeleteCommentResponse):
        self.storage = storage
        self.response = response

    def delete_comment_interactor(self, comment_id: str, user_id: str) -> Response:
        if not comment_id:
            return self.response.validation_error_response("Comment ID is required")
        
        try:
            comment = self.storage.get_comment_by_id(comment_id)
            if not comment:
                return self.response.comment_not_found_response()
            
            self.storage.delete_comment(comment_id=comment_id, user_id=user_id)
            
            return self.response.comment_deleted_successfully_response(comment_id, is_comment_creator=True)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.comment_not_found_response()
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response(is_comment_creator=False)
            return self.response.error_response(f"Failed to delete comment: {error_message}")

