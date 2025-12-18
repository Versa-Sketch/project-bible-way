from bible_way.storage import UserDB
from bible_way.presenters.create_profile_share_link_response import CreateProfileShareLinkResponse
from rest_framework.response import Response
from bible_way.models import ShareLinkContentTypeChoices


class CreateProfileShareLinkInteractor:
    def __init__(self, storage: UserDB, response: CreateProfileShareLinkResponse):
        self.storage = storage
        self.response = response

    def create_profile_share_link_interactor(self, user_id: str, created_by_user_id: str) -> Response:
        # Validate user_id
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        # Validate user exists
        user = self.storage.get_user_by_user_id(user_id)
        if not user:
            return self.response.user_not_found_response()
        
        try:
            # Create share link
            share_link = self.storage.create_share_link(
                content_type=ShareLinkContentTypeChoices.PROFILE,
                content_id=user_id,
                user_id=created_by_user_id
            )
            
            # Generate share URL
            share_url = f"/s/u/{share_link.share_token}"
            
            return self.response.share_link_created_successfully_response(
                share_url=share_url,
                share_token=share_link.share_token
            )
        except Exception as e:
            return self.response.error_response(f"Failed to create share link: {str(e)}")

