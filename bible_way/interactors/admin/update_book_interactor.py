from bible_way.storage import UserDB
from bible_way.presenters.admin.update_book_response import UpdateBookResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
import os


class UpdateBookInteractor:
    def __init__(self, storage: UserDB, response: UpdateBookResponse):
        self.storage = storage
        self.response = response

    def update_book_interactor(self, book_id: str, title: str = None, description: str = None, cover_image_file=None, cover_image_url: str = None) -> Response:
        # Validation
        if not book_id or not book_id.strip():
            return self.response.validation_error_response("book_id is required")
        
        book_id = book_id.strip()
        
        # Check if book exists
        try:
            book = self.storage.get_book_by_id(book_id)
        except Exception:
            return self.response.book_not_found_response()
        
        # Handle cover image - prioritize file upload over URL
        final_cover_image_url = None
        if cover_image_file:
            try:
                # Generate S3 key for book cover image
                image_key = f"books/cover_images/{book_id}/{cover_image_file.name}"
                final_cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        elif cover_image_url is not None:
            final_cover_image_url = cover_image_url.strip() if cover_image_url.strip() else None
        
        try:
            # Update book (only provided fields)
            updated_book = self.storage.update_book(
                book_id=book_id,
                title=title.strip() if title else None,
                description=description.strip() if description else None,
                cover_image_url=final_cover_image_url
            )
            
            # Refresh from DB to get related objects
            updated_book = self.storage.get_book_by_id(book_id)
            
            # Build response data
            book_data = {
                "book_id": str(updated_book.book_id),
                "title": updated_book.title,
                "description": updated_book.description,
                "cover_image_url": updated_book.cover_image_url,
                "category_id": str(updated_book.category.category_id),
                "category_name": updated_book.category.category_name,
                "age_group_id": str(updated_book.age_group.age_group_id),
                "age_group_name": updated_book.age_group.age_group_name,
                "language_id": str(updated_book.language.language_id),
                "language_name": updated_book.language.language_name,
                "book_order": updated_book.book_order,
                "is_active": updated_book.is_active,
                "created_at": updated_book.created_at.isoformat() if updated_book.created_at else None,
                "updated_at": updated_book.updated_at.isoformat() if updated_book.updated_at else None
            }
            
            return self.response.book_updated_successfully_response(book_data)
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.book_not_found_response()
            return self.response.error_response(f"Failed to update book: {error_message}")

