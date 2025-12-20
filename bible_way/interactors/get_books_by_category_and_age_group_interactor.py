from bible_way.storage import UserDB
from bible_way.presenters.get_books_by_category_and_age_group_response import GetBooksByCategoryAndAgeGroupResponse
from rest_framework.response import Response


class GetBooksByCategoryAndAgeGroupInteractor:
    def __init__(self, storage: UserDB, response: GetBooksByCategoryAndAgeGroupResponse):
        self.storage = storage
        self.response = response

    def get_books_by_category_and_age_group_interactor(self, user_id: str, category_id: str, age_group_id: str) -> Response:
        if not category_id or (isinstance(category_id, str) and not category_id.strip()):
            return self.response.validation_error_response("Category is required")
        
        if not age_group_id or (isinstance(age_group_id, str) and not age_group_id.strip()):
            return self.response.validation_error_response("Age group is required")
        
        category = self.storage.get_category_by_id(category_id)
        if not category:
            return self.response.validation_error_response(f"Category with id '{category_id}' does not exist")
        
        age_group = self.storage.get_age_group_by_id(age_group_id)
        if not age_group:
            return self.response.validation_error_response(f"Age group with id '{age_group_id}' does not exist")
        
        try:
            books = self.storage.get_books_by_category_and_age_group(category_id, age_group_id)
            
            # Get all bookmarked book IDs for the user
            bookmarks = self.storage.get_bookmarks_by_user(user_id)
            bookmarked_book_ids = {str(bookmark.book.book_id) for bookmark in bookmarks}
            
            books_data = []
            for book in books:
                book_id_str = str(book.book_id)
                books_data.append({
                    "book_id": book_id_str,
                    "title": book.title,
                    "description": book.description,
                    "category_id": str(book.category.category_id),
                    "age_group_id": str(book.age_group.age_group_id),
                    "language_id": str(book.language.language_id),
                    "cover_image_url": book.cover_image_url,
                    "book_order": book.book_order,
                    "is_active": book.is_active,
                    "is_bookmarked": book_id_str in bookmarked_book_ids,
                    "created_at": book.created_at.isoformat() if book.created_at else None,
                    "updated_at": book.updated_at.isoformat() if book.updated_at else None
                })
            
            return self.response.books_retrieved_successfully_response(books_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve books: {str(e)}")
