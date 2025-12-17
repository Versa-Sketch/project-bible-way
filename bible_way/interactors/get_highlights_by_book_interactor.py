from bible_way.storage import UserDB
from bible_way.presenters.get_highlights_by_book_response import GetHighlightsByBookResponse
from bible_way.models import Book
from rest_framework.response import Response


class GetHighlightsByBookInteractor:
    def __init__(self, storage: UserDB, response: GetHighlightsByBookResponse):
        self.storage = storage
        self.response = response

    def get_highlights_by_book_interactor(self, book_id: str, user_id: str = None) -> Response:
        # Validation
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        book_id = book_id.strip()
        
        # Validate book exists
        try:
            Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return self.response.book_not_found_response()
        
        try:
            highlights = self.storage.get_highlights_by_book_id(
                book_id=book_id,
                user_id=user_id.strip() if user_id else None
            )
            
            highlights_data = []
            for highlight in highlights:
                highlights_data.append({
                    "highlight_id": str(highlight.highlight_id),
                    "book_id": str(highlight.book.book_id),
                    "block_id": str(highlight.block_id) if highlight.block_id else None,
                    "chapter_id": str(highlight.chapter_id) if highlight.chapter_id else None,
                    "start_offset": highlight.start_offset,
                    "end_offset": highlight.end_offset,
                    "color": highlight.color,
                    "created_at": highlight.created_at.isoformat() if highlight.created_at else None,
                    "updated_at": highlight.updated_at.isoformat() if highlight.updated_at else None
                })
            
            return self.response.highlights_retrieved_successfully_response(highlights_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve highlights: {str(e)}")

