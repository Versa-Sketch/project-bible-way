from bible_way.storage import UserDB
from bible_way.presenters.get_book_details_response import GetBookDetailsResponse
from bible_way.models import Book
from rest_framework.response import Response


class GetBookDetailsInteractor:
    def __init__(self, storage: UserDB, response: GetBookDetailsResponse):
        self.storage = storage
        self.response = response

    def get_book_details_interactor(self, book_id: str) -> Response:
        try:
            book = self.storage.get_book_by_id(book_id)
        except Book.DoesNotExist:
            return self.response.book_not_found_response()
        except Exception as e:
            return self.response.error_response(f"Error retrieving book: {str(e)}")
        
        if not book.is_active:
            return self.response.book_not_found_response()
        
        try:
            chapters = self.storage.get_book_chapters(book_id)
            
            book_data = {
                "book_id": str(book.book_id),
                "title": book.title,
                "description": book.description,
                "category_id": str(book.category.category_id),
                "category_name": book.category.category_name,
                "category_display_name": book.category.get_category_name_display(),
                "age_group_id": str(book.age_group.age_group_id),
                "age_group_name": book.age_group.age_group_name,
                "age_group_display_name": book.age_group.get_age_group_name_display(),
                "language_id": str(book.language.language_id),
                "language_name": book.language.language_name,
                "language_display_name": book.language.get_language_name_display(),
                "cover_image_url": book.cover_image_url,
                "author": book.author,
                "book_order": book.book_order,
                "total_chapters": book.total_chapters,
                "is_parsed": book.is_parsed,
                "is_active": book.is_active,
                "source_file_name": book.source_file_name,
                "source_file_url": book.source_file_url,
                "metadata": book.metadata,
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None
            }
            
            chapters_data = []
            for chapter in chapters:
                chapters_data.append({
                    "book_content_id": str(chapter.book_content_id),
                    "chapter_number": chapter.chapter_number,
                    "chapter_title": chapter.chapter_title,
                    "content_order": chapter.content_order,
                    "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                    "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
                })
            
            return self.response.book_details_retrieved_successfully_response(book_data, chapters_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve book details: {str(e)}")

