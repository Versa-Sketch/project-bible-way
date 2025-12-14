from bible_way.storage import UserDB
from bible_way.presenters.admin.create_category_response import CreateCategoryResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from bible_way.models.book_reading import CategoryChoices
from bible_way.models import Category
from rest_framework.response import Response
import os


class CreateCategoryInteractor:
    def __init__(self, storage: UserDB, response: CreateCategoryResponse):
        self.storage = storage
        self.response = response

    def create_category_interactor(self, category_name: str, cover_image_file=None, description: str = None, display_order: int = 0) -> Response:
        # Validation
        if not category_name or not category_name.strip():
            return self.response.validation_error_response("Category name is required")
        
        # Validate category_name is a valid choice
        valid_choices = [choice[0] for choice in CategoryChoices.choices]
        if category_name not in valid_choices:
            return self.response.validation_error_response(f"Invalid category name. Must be one of: {', '.join(valid_choices)}")
        
        # Check if category already exists
        try:
            existing_category = Category.objects.get(category_name=category_name)
            return self.response.validation_error_response(f"Category '{category_name}' already exists")
        except Category.DoesNotExist:
            pass
        
        cover_image_url = None
        
        # Upload cover image to S3 if provided
        if cover_image_file:
            try:
                # Generate S3 key for category cover image
                category_id_preview = os.urandom(8).hex()
                image_key = f"categories/cover_images/{category_id_preview}/{cover_image_file.name}"
                cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        
        try:
            # Create category
            category = self.storage.create_category(
                category_name=category_name,
                cover_image_url=cover_image_url,
                description=description or '',
                display_order=display_order
            )
            
            # Build response data
            category_data = {
                "category_id": str(category.category_id),
                "category_name": category.category_name,
                "display_name": category.get_category_name_display(),
                "cover_image_url": category.cover_image_url,
                "description": category.description,
                "display_order": category.display_order,
                "created_at": category.created_at.isoformat() if category.created_at else None,
                "updated_at": category.updated_at.isoformat() if category.updated_at else None
            }
            
            return self.response.category_created_successfully_response(category_data)
        except Exception as e:
            return self.response.error_response(f"Failed to create category: {str(e)}")

