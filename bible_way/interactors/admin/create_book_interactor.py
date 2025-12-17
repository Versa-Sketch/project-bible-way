from bible_way.storage import UserDB
from bible_way.presenters.admin.create_book_response import CreateBookResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from bible_way.models import Category, AgeGroup, Language, Book
from rest_framework.response import Response
import os
import uuid


class CreateBookInteractor:
    def __init__(self, storage: UserDB, response: CreateBookResponse):
        self.storage = storage
        self.response = response

    def create_book_interactor(self, title: str, category_id: str, age_group_id: str, language_id: str,
                               source_file=None, cover_image_file=None, description: str = None,
                               book_order: int = 0) -> Response:
        # Validation
        if not title or not title.strip():
            return self.response.validation_error_response("Title is required")
        
        if not category_id:
            return self.response.validation_error_response("Category is required")
        
        if not age_group_id:
            return self.response.validation_error_response("Age group is required")
        
        if not language_id:
            return self.response.validation_error_response("Language is required")
        
        if not source_file:
            return self.response.validation_error_response("Source file (.md file) is required")
        
        # Validate category exists
        try:
            Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return self.response.validation_error_response(f"Category with id '{category_id}' does not exist")
        
        # Validate age_group exists
        try:
            AgeGroup.objects.get(age_group_id=age_group_id)
        except AgeGroup.DoesNotExist:
            return self.response.validation_error_response(f"Age group with id '{age_group_id}' does not exist")
        
        # Validate language exists
        try:
            Language.objects.get(language_id=language_id)
        except Language.DoesNotExist:
            return self.response.validation_error_response(f"Language with id '{language_id}' does not exist")
        
        # Generate preview ID for S3 folder structure
        book_id_preview = os.urandom(8).hex()
        
        source_file_url = None
        source_file_name = None
        
        # Upload source file to S3 (required)
        try:
            source_file_name = source_file.name
            source_key = f"books/{book_id_preview}/source_files/{source_file_name}"
            source_file_url = s3_upload_file(source_file, source_key)
        except Exception as e:
            return self.response.error_response(f"Failed to upload source file: {str(e)}")
        
        cover_image_url = None
        
        # Upload cover image to S3 if provided
        if cover_image_file:
            try:
                image_key = f"books/{book_id_preview}/cover_images/{cover_image_file.name}"
                cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        
        try:
            # Create book
            book = self.storage.create_book(
                title=title,
                category_id=category_id,
                age_group_id=age_group_id,
                language_id=language_id,
                cover_image_url=cover_image_url,
                description=description or '',
                book_order=book_order,
                source_file_name=source_file_name,
                source_file_url=source_file_url
            )
            
            # Build response data (only required fields)
            book_data = {
                "book_id": str(book.book_id),
                "source_file_url": book.source_file_url,
                "created_at": book.created_at.isoformat() if book.created_at else None,
                "updated_at": book.updated_at.isoformat() if book.updated_at else None
            }
            
            return self.response.book_created_successfully_response(book_data)
        except Exception as e:
            return self.response.error_response(f"Failed to create book: {str(e)}")
