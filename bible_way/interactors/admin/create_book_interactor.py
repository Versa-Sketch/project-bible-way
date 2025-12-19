from bible_way.storage import UserDB
from bible_way.presenters.admin.create_book_response import CreateBookResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
import os


class CreateBookInteractor:
    def __init__(self, storage: UserDB, response: CreateBookResponse):
        self.storage = storage
        self.response = response

    def create_book_interactor(self, title: str, category_id: str, age_group_id: str, language_id: str,
                               cover_image_file=None, description: str = None) -> Response:
        if not title or not title.strip():
            return self.response.validation_error_response("Title is required")
        
        if not category_id or (isinstance(category_id, str) and not category_id.strip()):
            return self.response.validation_error_response("Category is required")
        
        if not age_group_id or (isinstance(age_group_id, str) and not age_group_id.strip()):
            return self.response.validation_error_response("Age group is required")
        
        if not language_id or (isinstance(language_id, str) and not language_id.strip()):
            return self.response.validation_error_response("Language is required")
        
        category = self.storage.get_category_by_id(category_id)
        if not category:
            return self.response.validation_error_response(f"Category with id '{category_id}' does not exist")
        
        age_group = self.storage.get_age_group_by_id(age_group_id)
        if not age_group:
            return self.response.validation_error_response(f"Age group with id '{age_group_id}' does not exist")
        
        language = self.storage.get_language_by_id(language_id)
        if not language:
            return self.response.validation_error_response(f"Language with id '{language_id}' does not exist")
        
        final_cover_image_url = None
        
        if cover_image_file:
            try:
                book_id_preview = os.urandom(8).hex()
                image_key = f"books/cover_images/{book_id_preview}/{cover_image_file.name}"
                final_cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        
        try:
            book = self.storage.create_book(
                title=title.strip(),
                category_id=category_id,
                age_group_id=age_group_id,
                language_id=language_id,
                cover_image_url=final_cover_image_url,
                description=description.strip() if description else ''
            )
            
            return self.response.book_created_successfully_response(str(book.book_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create book: {str(e)}")
