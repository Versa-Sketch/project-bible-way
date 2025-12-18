from bible_way.storage import UserDB
from bible_way.presenters.create_post_share_link_response import CreatePostShareLinkResponse
from rest_framework.response import Response
from bible_way.models import ShareLinkContentTypeChoices


class CreatePostShareLinkInteractor:
    def __init__(self, storage: UserDB, response: CreatePostShareLinkResponse):
        self.storage = storage
        self.response = response

    def create_post_share_link_interactor(self, post_id: str, user_id: str) -> Response:
        # Validate post_id
        if not post_id or not post_id.strip():
            return self.response.validation_error_response("post_id is required")
        
        post_id = post_id.strip()
        
        # Validate post exists
        post = self.storage.get_post_by_id(post_id)
        if not post:
            return self.response.post_not_found_response()
        
        # Validate user has permission (post owner or post is public - for now, all posts are shareable)
        # In future, you can add privacy settings here
        
        try:
            # Create share link
            share_link = self.storage.create_share_link(
                content_type=ShareLinkContentTypeChoices.POST,
                content_id=post_id,
                user_id=user_id
            )
            
            # Generate share URL
            share_url = f"/s/p/{share_link.share_token}"
            
            return self.response.share_link_created_successfully_response(
                share_url=share_url,
                share_token=share_link.share_token
            )
        except Exception as e:
            return self.response.error_response(f"Failed to create share link: {str(e)}")

