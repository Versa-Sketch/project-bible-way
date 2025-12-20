from bible_way.storage import UserDB
from bible_way.presenters.delete_bookmark_response import DeleteBookmarkResponse
from rest_framework.response import Response


class DeleteBookmarkInteractor:
    def __init__(self, storage: UserDB, response: DeleteBookmarkResponse):
        self.storage = storage
        self.response = response

    def delete_bookmark_interactor(self, bookmark_id: str, user_id: str) -> Response:
        if not bookmark_id or not bookmark_id.strip():
            return self.response.validation_error_response("bookmark_id is required")
        
        bookmark_id = bookmark_id.strip()
        
        try:
            bookmark = self.storage.get_bookmark_by_id(bookmark_id)
            if not bookmark:
                return self.response.bookmark_not_found_response()
            
            if str(bookmark.user.user_id) != user_id:
                return self.response.unauthorized_response()
            
            self.storage.delete_bookmark(bookmark_id=bookmark_id, user_id=user_id)
            
            return self.response.bookmark_deleted_successfully_response()
            
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower() or "does not exist" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to delete bookmark: {error_message}")
