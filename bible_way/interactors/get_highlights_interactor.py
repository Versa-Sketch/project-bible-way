from bible_way.storage import UserDB
from bible_way.presenters.get_highlights_response import GetHighlightsResponse
from rest_framework.response import Response
from bible_way.models import Book


class GetHighlightsInteractor:
    def __init__(self, storage: UserDB, response: GetHighlightsResponse):
        self.storage = storage
        self.response = response

    def get_highlights_interactor(self, user_id: str, book_id: str) -> Response:
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        book_id = book_id.strip()
        user_id = user_id.strip()
        
        try:
            try:
                Book.objects.get(book_id=book_id)
            except Book.DoesNotExist:
                return self.response.book_not_found_response()
            
            highlights = self.storage.get_highlights_by_user_and_book(user_id=user_id, book_id=book_id)
            
            highlights_data = []
            for highlight in highlights:
                highlights_data.append({
                    "highlight_id": str(highlight.highlight_id),
                    "book_id": str(highlight.book.book_id),
                    "block_id": str(highlight.block_id) if highlight.block_id else None,
                    "start_offset": highlight.start_offset,
                    "end_offset": highlight.end_offset,
                    "color": highlight.color,
                    "created_at": highlight.created_at.isoformat() if highlight.created_at else None,
                    "updated_at": highlight.updated_at.isoformat() if highlight.updated_at else None
                })
            
            return self.response.highlights_retrieved_successfully_response(highlights_data)
            
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve highlights: {str(e)}")
