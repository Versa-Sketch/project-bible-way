from bible_way.storage import UserDB
from bible_way.presenters.get_book_details_response import GetBookDetailsResponse
from rest_framework.response import Response


class GetBookDetailsInteractor:
    def __init__(self, storage: UserDB, response: GetBookDetailsResponse):
        self.storage = storage
        self.response = response

    def get_book_details_interactor(self, book_id: str, user_id: str) -> Response:
        if not book_id or (isinstance(book_id, str) and not book_id.strip()):
            return self.response.validation_error_response("Book ID is required")
        
        try:
            book = self.storage.get_book_by_id(book_id)
        except Exception:
            return self.response.validation_error_response(f"Book with id '{book_id}' does not exist")
        
        try:
            # Check if book is bookmarked by the user
            bookmark = self.storage.get_bookmark_by_user_and_book(user_id=user_id, book_id=book_id)
            is_bookmarked = bookmark is not None
            
            # Build book details dictionary
            book_data = {
                "book_id": str(book.book_id),
                "title": book.title,
                "description": book.description,
                "category_id": str(book.category.category_id) if book.category else None,
                "category_name": book.category.get_category_name_display() if book.category else None,
                "age_group_id": str(book.age_group.age_group_id) if book.age_group else None,
                "age_group_name": book.age_group.get_age_group_name_display() if book.age_group else None,
                "language_id": str(book.language.language_id) if book.language else None,
                "language_name": book.language.get_language_name_display() if book.language else None,
                "cover_image_url": book.cover_image_url,
                "book_order": book.book_order,
                "is_active": book.is_active,
                "is_bookmarked": is_bookmarked,
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None
            }
            
            return self.response.book_details_retrieved_successfully_response(book_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve book details: {str(e)}")

