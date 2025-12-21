from bible_way.storage import UserDB
from bible_way.presenters.get_shared_post_response import GetSharedPostResponse
from rest_framework.response import Response
from django.db.models import Count, Q
from bible_way.models import ShareLinkContentTypeChoices
from bible_way.utils.s3_url_helper import get_presigned_url


class GetSharedPostInteractor:
    def __init__(self, storage: UserDB, response: GetSharedPostResponse):
        self.storage = storage
        self.response = response

    def get_shared_post_interactor(self, token: str) -> Response:
        # Validate token format
        if not token or not token.strip():
            return self.response.invalid_token_response()
        
        token = token.strip()
        
        try:
            # First check if share link exists and is active
            share_link = self.storage.get_share_link_by_token(token)
            if not share_link:
                return self.response.invalid_token_response()
            
            # Verify it's for a POST
            if share_link.content_type != ShareLinkContentTypeChoices.POST:
                return self.response.invalid_token_response()
            
            # Get post by share token (this will return None if post is deleted)
            post = self.storage.get_post_by_share_token(token)
            
            if not post:
                # Token is valid but post was deleted
                return self.response.post_not_found_response()
            
            # Get media for the post
            media_list = []
            for media in post.media.all():
                media_list.append({
                    'media_id': str(media.media_id),
                    'media_type': media.media_type,
                    'url': get_presigned_url(media.url)
                })
            
            # Get counts
            from bible_way.models import Reaction, Comment
            likes_count = Reaction.objects.filter(post=post, reaction_type='like').count()
            comments_count = Comment.objects.filter(post=post).count()
            
            # Build response data
            post_data = {
                'post_id': str(post.post_id),
                'user': {
                    'user_id': str(post.user.user_id),
                    'user_name': post.user.user_name,
                    'profile_picture_url': get_presigned_url(post.user.profile_picture_url) if post.user.profile_picture_url else ''
                },
                'title': post.title,
                'description': post.description,
                'media': media_list,
                'likes_count': likes_count,
                'comments_count': comments_count,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
            
            return self.response.post_retrieved_successfully_response(post_data=post_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve shared post: {str(e)}")

