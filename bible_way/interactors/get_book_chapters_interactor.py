from bible_way.storage import UserDB
from bible_way.presenters.get_book_chapters_response import GetBookChaptersResponse
from rest_framework.response import Response


class GetBookChaptersInteractor:
    def __init__(self, storage: UserDB, response: GetBookChaptersResponse):
        self.storage = storage
        self.response = response

    def get_book_chapters_interactor(self, book_id: str) -> Response:
        if not book_id or (isinstance(book_id, str) and not book_id.strip()):
            return self.response.validation_error_response("Book ID is required")
        
        try:
            book = self.storage.get_book_by_id(book_id)
        except Exception:
            return self.response.validation_error_response(f"Book with id '{book_id}' does not exist")
        
        try:
            chapters = self.storage.get_book_chapters(book_id)
            
            chapters_data = []
            for chapter in chapters:
                chapters_data.append({
                    "chapter_id": str(chapter.chapter_id),
                    "book_id": str(chapter.book.book_id),
                    "title": chapter.title,
                    "description": chapter.description,
                    "chapter_number": chapter.chapter_number,
                    "chapter_name": chapter.chapter_name,
                    "chapter_url": chapter.chapter_url,
                    "metadata": chapter.metadata if chapter.metadata else {},
                    "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                    "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
                })
            
            return self.response.chapters_retrieved_successfully_response(chapters_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve chapters: {str(e)}")
