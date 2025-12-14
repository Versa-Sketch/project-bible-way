from bible_way.storage import UserDB
from bible_way.presenters.admin.create_age_group_response import CreateAgeGroupResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from bible_way.models.book_reading import AgeGroupChoices
from bible_way.models import AgeGroup
from rest_framework.response import Response
import os


class CreateAgeGroupInteractor:
    def __init__(self, storage: UserDB, response: CreateAgeGroupResponse):
        self.storage = storage
        self.response = response

    def create_age_group_interactor(self, age_group_name: str, cover_image_file=None, description: str = None, display_order: int = 0) -> Response:
        # Validation
        if not age_group_name or not age_group_name.strip():
            return self.response.validation_error_response("Age group name is required")
        
        # Validate age_group_name is a valid choice
        valid_choices = [choice[0] for choice in AgeGroupChoices.choices]
        if age_group_name not in valid_choices:
            return self.response.validation_error_response(f"Invalid age group name. Must be one of: {', '.join(valid_choices)}")
        
        # Check if age group already exists
        try:
            existing_age_group = AgeGroup.objects.get(age_group_name=age_group_name)
            return self.response.validation_error_response(f"Age group '{age_group_name}' already exists")
        except AgeGroup.DoesNotExist:
            pass
        
        cover_image_url = None
        
        # Upload cover image to S3 if provided
        if cover_image_file:
            try:
                # Generate S3 key for age group cover image
                age_group_id_preview = os.urandom(8).hex()
                image_key = f"age_groups/cover_images/{age_group_id_preview}/{cover_image_file.name}"
                cover_image_url = s3_upload_file(cover_image_file, image_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload cover image: {str(e)}")
        
        try:
            # Create age group
            age_group = self.storage.create_age_group(
                age_group_name=age_group_name,
                cover_image_url=cover_image_url,
                description=description or '',
                display_order=display_order
            )
            
            # Build response data
            age_group_data = {
                "age_group_id": str(age_group.age_group_id),
                "age_group_name": age_group.age_group_name,
                "display_name": age_group.get_age_group_name_display(),
                "cover_image_url": age_group.cover_image_url,
                "description": age_group.description,
                "display_order": age_group.display_order,
                "created_at": age_group.age_group_created_at.isoformat() if age_group.age_group_created_at else None,
                "updated_at": age_group.age_group_updated_at.isoformat() if age_group.age_group_updated_at else None
            }
            
            return self.response.age_group_created_successfully_response(age_group_data)
        except Exception as e:
            return self.response.error_response(f"Failed to create age group: {str(e)}")

