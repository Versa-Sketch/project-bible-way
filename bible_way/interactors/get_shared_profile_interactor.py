from bible_way.storage import UserDB
from bible_way.presenters.get_shared_profile_response import GetSharedProfileResponse
from rest_framework.response import Response
from django.db.models import Count
from bible_way.models import ShareLinkContentTypeChoices


class GetSharedProfileInteractor:
    def __init__(self, storage: UserDB, response: GetSharedProfileResponse):
        self.storage = storage
        self.response = response

    def get_shared_profile_interactor(self, token: str) -> Response:
        # Validate token format
        if not token or not token.strip():
            return self.response.invalid_token_response()
        
        token = token.strip()
        
        try:
            # First check if share link exists and is active
            share_link = self.storage.get_share_link_by_token(token)
            if not share_link:
                return self.response.invalid_token_response()
            
            # Verify it's for a PROFILE
            if share_link.content_type != ShareLinkContentTypeChoices.PROFILE:
                return self.response.invalid_token_response()
            
            # Get user profile by share token (this will return None if user is deleted)
            user = self.storage.get_profile_by_share_token(token)
            
            if not user:
                # Token is valid but user account was deleted or deactivated
                return self.response.user_not_found_response()
            
            # Check if user account is active
            if not user.is_active:
                return self.response.user_not_found_response()
            
            # Get follower and following counts
            from bible_way.models import UserFollowers
            followers_count = UserFollowers.objects.filter(followed_id__user_id=user.user_id).count()
            following_count = UserFollowers.objects.filter(follower_id__user_id=user.user_id).count()
            
            # Build response data
            profile_data = {
                'user_id': str(user.user_id),
                'user_name': user.user_name,
                'email': user.email,
                'country': user.country,
                'age': user.age,
                'preferred_language': user.preferred_language,
                'profile_picture_url': user.profile_picture_url or '',
                'is_admin': user.is_staff,
                'followers_count': followers_count,
                'following_count': following_count
            }
            
            return self.response.profile_retrieved_successfully_response(profile_data=profile_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve shared profile: {str(e)}")

