from bible_way.storage import UserDB
from bible_way.presenters.delete_highlight_response import DeleteHighlightResponse
from rest_framework.response import Response


class DeleteHighlightInteractor:
    def __init__(self, storage: UserDB, response: DeleteHighlightResponse):
        self.storage = storage
        self.response = response

    def delete_highlight_interactor(self, highlight_id: str, user_id: str) -> Response:
        if not highlight_id or not highlight_id.strip():
            return self.response.validation_error_response("highlight_id is required")
        
        highlight_id = highlight_id.strip()
        
        try:
            highlight = self.storage.get_highlight_by_id(highlight_id)
            if not highlight:
                return self.response.highlight_not_found_response()
            
            if str(highlight.user.user_id) != user_id:
                return self.response.unauthorized_response()
            
            self.storage.delete_highlight(highlight_id=highlight_id, user_id=user_id)
            
            return self.response.highlight_deleted_successfully_response()
            
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower() or "does not exist" in error_message.lower():
                return self.response.unauthorized_response()
            return self.response.error_response(f"Failed to delete highlight: {error_message}")
