from bible_way.storage import UserDB
from bible_way.presenters.get_bookmarks_response import GetBookmarksResponse
from rest_framework.response import Response


class GetBookmarksInteractor:
    def __init__(self, storage: UserDB, response: GetBookmarksResponse):
        self.storage = storage
        self.response = response

    def get_bookmarks_interactor(self, user_id: str) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        try:
            bookmarks = self.storage.get_bookmarks_by_user(user_id=user_id)
            
            # Get all reading progress for this user (efficient batch fetch)
            reading_progress_dict = self.storage.get_reading_progress_by_user(user_id=user_id)
            
            bookmarks_data = []
            for bookmark in bookmarks:
                book_id = str(bookmark.book.book_id)
                book = bookmark.book
                
                # Get progress data for this book, default to 0.00 and None if not found
                progress_data = reading_progress_dict.get(book_id, {'progress_percentage': 0.00, 'block_id': None})
                progress_percentage = progress_data.get('progress_percentage', 0.00)
                block_id = progress_data.get('block_id')
                
                # Build book details
                book_details = {
                    "book_id": book_id,
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
                    "is_active": book.is_active
                }
                
                bookmarks_data.append({
                    "bookmark_id": str(bookmark.bookmark_id),
                    "book_id": book_id,
                    "book_title": book.title,
                    "progress_percentage": str(progress_percentage),
                    "block_id": block_id,
                    "book_details": book_details,
                    "created_at": bookmark.created_at.isoformat() if bookmark.created_at else None,
                    "updated_at": bookmark.updated_at.isoformat() if bookmark.updated_at else None
                })
            
            return self.response.bookmarks_retrieved_successfully_response(bookmarks_data)
            
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve bookmarks: {str(e)}")
