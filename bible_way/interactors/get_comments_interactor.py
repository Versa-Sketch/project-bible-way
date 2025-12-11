import uuid
from bible_way.storage import UserDB
from bible_way.presenters.get_comments_response import GetCommentsResponse
from rest_framework.response import Response


class GetCommentsInteractor:
    def __init__(self, storage: UserDB, response: GetCommentsResponse):
        self.storage = storage
        self.response = response

    def get_comments_interactor(self, post_id: str, user_id: str = None) -> Response:
        if not post_id:
            return self.response.validation_error_response("Post ID is required")
        
        try:
            comments = self.storage.get_comments_by_post(post_id)
            
            comments_data = []
            for comment in comments:
                comment_data = {
                    "comment_id": str(comment.comment_id),
                    "user": {
                        "user_id": str(comment.user.user_id),
                        "user_name": comment.user.user_name,
                        "email": comment.user.email,
                        "profile_picture_url": comment.user.profile_picture_url or ""
                    },
                    "description": comment.description,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat(),
                    "is_comment_creator": False
                }
                
                if user_id and comment.user.user_id == uuid.UUID(user_id) if isinstance(user_id, str) else user_id:
                    comment_data["is_comment_creator"] = True
                
                comments_data.append(comment_data)
            
            return self.response.comments_retrieved_successfully_response(post_id, comments_data)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.post_not_found_response()
            return self.response.error_response(f"Failed to retrieve comments: {error_message}")

