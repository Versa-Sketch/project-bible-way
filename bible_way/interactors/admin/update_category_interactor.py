from bible_way.storage import UserDB
from bible_way.presenters.admin.update_category_response import UpdateCategoryResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
import os


class UpdateCategoryInteractor:
    def __init__(self, storage: UserDB, response: UpdateCategoryResponse):
        self.storage = storage
        self.response = response

    def update_category_interactor(self, category_id: str, cover_image_file=None, cover_image_url: str = None, description: str = None) -> Response:
        # Validation
        if not category_id or not category_id.strip():
            return self.response.validation_error_response("category_id is required")
        
        category_id = category_id.strip()
        
        # Check if category exists
        category = self.storage.get_category_by_id(category_id)
        if not category:
            return self.response.category_not_found_response()
        
        # Handle cover image - prioritize file upload over URL
        final_cover_image_url = None
        if cover_image_file:
            try:
                # Generate S3 key for category cover image
                image_key = f"categories/cover_images/{category_id}/{cover_image_file.name}"
                final_cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        elif cover_image_url is not None:
            final_cover_image_url = cover_image_url.strip() if cover_image_url.strip() else None
        
        try:
            # Update category (only provided fields)
            updated_category = self.storage.update_category(
                category_id=category_id,
                cover_image_url=final_cover_image_url,
                description=description.strip() if description else None
            )
            
            # Build response data
            category_data = {
                "category_id": str(updated_category.category_id),
                "category_name": updated_category.category_name,
                "display_name": updated_category.get_category_name_display(),
                "cover_image_url": updated_category.cover_image_url,
                "description": updated_category.description,
                "display_order": updated_category.display_order,
                "created_at": updated_category.created_at.isoformat() if updated_category.created_at else None,
                "updated_at": updated_category.updated_at.isoformat() if updated_category.updated_at else None
            }
            
            return self.response.category_updated_successfully_response(category_data)
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.category_not_found_response()
            return self.response.error_response(f"Failed to update category: {error_message}")

