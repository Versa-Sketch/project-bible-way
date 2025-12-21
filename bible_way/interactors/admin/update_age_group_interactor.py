from bible_way.storage import UserDB
from bible_way.presenters.admin.update_age_group_response import UpdateAgeGroupResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
import os


class UpdateAgeGroupInteractor:
    def __init__(self, storage: UserDB, response: UpdateAgeGroupResponse):
        self.storage = storage
        self.response = response

    def update_age_group_interactor(self, age_group_id: str, cover_image_file=None, cover_image_url: str = None, description: str = None) -> Response:
        # Validation
        if not age_group_id or not age_group_id.strip():
            return self.response.validation_error_response("age_group_id is required")
        
        age_group_id = age_group_id.strip()
        
        # Check if age group exists
        age_group = self.storage.get_age_group_by_id(age_group_id)
        if not age_group:
            return self.response.age_group_not_found_response()
        
        # Handle cover image - prioritize file upload over URL
        final_cover_image_url = None
        if cover_image_file:
            try:
                # Generate S3 key for age group cover image
                image_key = f"age_groups/cover_images/{age_group_id}/{cover_image_file.name}"
                final_cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        elif cover_image_url is not None:
            final_cover_image_url = cover_image_url.strip() if cover_image_url.strip() else None
        
        try:
            # Update age group (only provided fields)
            updated_age_group = self.storage.update_age_group(
                age_group_id=age_group_id,
                cover_image_url=final_cover_image_url,
                description=description.strip() if description else None
            )
            
            # Build response data
            age_group_data = {
                "age_group_id": str(updated_age_group.age_group_id),
                "age_group_name": updated_age_group.age_group_name,
                "display_name": updated_age_group.get_age_group_name_display(),
                "cover_image_url": updated_age_group.cover_image_url,
                "description": updated_age_group.description,
                "display_order": updated_age_group.display_order,
                "created_at": updated_age_group.age_group_created_at.isoformat() if updated_age_group.age_group_created_at else None,
                "updated_at": updated_age_group.age_group_updated_at.isoformat() if updated_age_group.age_group_updated_at else None
            }
            
            return self.response.age_group_updated_successfully_response(age_group_data)
        except Exception as e:
            error_message = str(e)
            if "not found" in error_message.lower():
                return self.response.age_group_not_found_response()
            return self.response.error_response(f"Failed to update age group: {error_message}")

