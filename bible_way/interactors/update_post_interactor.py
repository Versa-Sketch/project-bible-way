from bible_way.storage import UserDB
from bible_way.presenters.update_post_response import UpdatePostResponse
from rest_framework.response import Response


class UpdatePostInteractor:
    def __init__(self, storage: UserDB, response: UpdatePostResponse):
        self.storage = storage
        self.response = response

    def update_post_interactor(self, post_id: str, user_id: str, title: str = None, description: str = None) -> Response:
        if title is None and description is None:
            return self.response.validation_error_response("At least one field (title or description) must be provided")
        
        try:
            post = self.storage.get_post_by_id(post_id)
            if not post:
                return self.response.post_not_found_response()
            
            updated_post = self.storage.update_post(
                post_id=post_id,
                user_id=user_id,
                title=title,
                description=description
            )
            
            return self.response.post_updated_successfully_response(str(updated_post.post_id))
            
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to update post: {error_message}")

