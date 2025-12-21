from bible_way.storage import UserDB
from bible_way.presenters.get_top_books_reading_progress_response import GetTopBooksReadingProgressResponse
from rest_framework.response import Response


class GetTopBooksReadingProgressInteractor:
    def __init__(self, storage: UserDB, response: GetTopBooksReadingProgressResponse):
        self.storage = storage
        self.response = response

    def get_top_books_reading_progress_interactor(self, user_id: str) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        try:
            # Get top 2 books by reading progress
            reading_progresses = self.storage.get_top_reading_progress_books(user_id=user_id, limit=2)
            
            # Get all bookmarked book IDs for the user (for efficient lookup)
            bookmarks = self.storage.get_bookmarks_by_user(user_id=user_id)
            bookmarked_book_ids = {str(bookmark.book.book_id) for bookmark in bookmarks}
            
            top_books_data = []
            for reading_progress in reading_progresses:
                book = reading_progress.book
                book_id_str = str(book.book_id)
                
                # Check if book is bookmarked
                is_bookmarked = book_id_str in bookmarked_book_ids
                
                # Build book details
                book_details = {
                    "book_id": book_id_str,
                    "title": book.title,
                    "description": book.description if book.description else "",
                    "cover_image_url": book.cover_image_url if book.cover_image_url else "",
                    "category_id": str(book.category.category_id) if book.category else None,
                    "category_name": book.category.get_category_name_display() if book.category else None,
                    "age_group_id": str(book.age_group.age_group_id) if book.age_group else None,
                    "age_group_name": book.age_group.get_age_group_name_display() if book.age_group else None,
                    "language_id": str(book.language.language_id) if book.language else None,
                    "language_name": book.language.get_language_name_display() if book.language else None,
                    "book_order": book.book_order if book.book_order else 0,
                    "is_active": book.is_active,
                    "is_bookmarked": is_bookmarked
                }
                
                # Build reading progress data
                progress_data = {
                    "reading_progress_id": str(reading_progress.reading_progress_id),
                    "book_id": book_id_str,
                    "progress_percentage": float(reading_progress.progress_percentage),
                    "block_id": reading_progress.block_id if reading_progress.block_id else None,
                    "chapter_id": str(reading_progress.chapter_id.chapter_id) if reading_progress.chapter_id else None,
                    "last_read_at": reading_progress.last_read_at.isoformat() if reading_progress.last_read_at else None,
                    "book_details": book_details,
                    "created_at": reading_progress.created_at.isoformat() if reading_progress.created_at else None,
                    "updated_at": reading_progress.updated_at.isoformat() if reading_progress.updated_at else None
                }
                
                top_books_data.append(progress_data)
            
            return self.response.top_books_retrieved_successfully_response(top_books_data)
            
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve top books: {str(e)}")

