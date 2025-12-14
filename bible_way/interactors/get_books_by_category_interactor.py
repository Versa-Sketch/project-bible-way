from bible_way.storage import UserDB
from bible_way.presenters.get_books_by_category_response import GetBooksByCategoryResponse
from bible_way.models import Category, AgeGroup, Language
from rest_framework.response import Response


class GetBooksByCategoryInteractor:
    def __init__(self, storage: UserDB, response: GetBooksByCategoryResponse):
        self.storage = storage
        self.response = response

    def get_books_by_category_interactor(self, category_id: str, age_group_id: str, language_id: str = None) -> Response:
        # Validate category_id exists
        try:
            Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return self.response.validation_error_response(f"Category with id '{category_id}' not found")
        
        # Validate age_group_id exists
        try:
            AgeGroup.objects.get(age_group_id=age_group_id)
        except AgeGroup.DoesNotExist:
            return self.response.validation_error_response(f"Age group with id '{age_group_id}' not found")
        
        # Validate language_id if provided
        if language_id:
            try:
                Language.objects.get(language_id=language_id)
            except Language.DoesNotExist:
                return self.response.validation_error_response(f"Language with id '{language_id}' not found")
        
        try:
            books = self.storage.get_books_by_category_and_age_group(
                category_id=category_id,
                age_group_id=age_group_id,
                language_id=language_id
            )
            
            books_data = []
            for book in books:
                books_data.append({
                    "book_id": str(book.book_id),
                    "title": book.title,
                    "cover_image_url": book.cover_image_url,
                    "book_order": book.book_order
                })
            
            return self.response.books_retrieved_successfully_response(books_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve books: {str(e)}")

