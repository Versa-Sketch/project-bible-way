from bible_way.storage import UserDB
from bible_way.presenters.delete_chapter_response import DeleteChapterResponse
from rest_framework.response import Response


class DeleteChapterInteractor:
    def __init__(self, storage: UserDB, response: DeleteChapterResponse):
        self.storage = storage
        self.response = response

    def delete_chapter_interactor(self, chapter_id: str) -> Response:
        if not chapter_id or not chapter_id.strip():
            return self.response.validation_error_response("chapter_id is required")
        
        chapter_id = chapter_id.strip()
        
        try:
            # Check if chapter exists
            chapter = self.storage.get_chapter_by_id(chapter_id)
            if not chapter:
                return self.response.chapter_not_found_response()
            
            # Delete the chapter
            self.storage.delete_chapter(chapter_id)
            
            return self.response.chapter_deleted_successfully_response(chapter_id)
            
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.chapter_not_found_response()
            return self.response.error_response(f"Failed to delete chapter: {error_message}")

