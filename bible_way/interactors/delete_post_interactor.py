from bible_way.storage import UserDB
from bible_way.presenters.delete_post_response import DeletePostResponse
from rest_framework.response import Response


class DeletePostInteractor:
    def __init__(self, storage: UserDB, response: DeletePostResponse):
        self.storage = storage
        self.response = response

    def delete_post_interactor(self, post_id: str, user_id: str) -> Response:
        try:
            post = self.storage.get_post_by_id(post_id)
            if not post:
                return self.response.post_not_found_response()
            
            self.storage.delete_post(post_id=post_id, user_id=user_id)
            
            return self.response.post_deleted_successfully_response(post_id)
            
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to delete post: {error_message}")

