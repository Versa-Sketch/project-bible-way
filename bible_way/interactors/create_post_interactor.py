from bible_way.storage import UserDB
from bible_way.presenters.create_post_response import CreatePostResponse
from rest_framework.response import Response


class CreatePostInteractor:
    def __init__(self, storage: UserDB, response: CreatePostResponse):
        self.storage = storage
        self.response = response

    def create_post_interactor(self, user_id: str, title: str, description: str, media_urls: list) -> Response:
        # Validate that at least one media URL is provided
        if not media_urls or len(media_urls) == 0:
            return self.response.no_media_provided_response()
        
        # Validate title and description (both optional)
        title = title.strip() if title else ''
        description = description.strip() if description else ''
        
        try:
            # Create the post
            post = self.storage.create_post(
                user_id=user_id,
                title=title,
                description=description
            )
            
            # Process each media URL
            for media_url in media_urls:
                try:
                    # Validate URL format
                    if not isinstance(media_url, str) or not media_url.strip():
                        return self.response.validation_error_response("Invalid media URL provided")
                    
                    media_url = media_url.strip()
                    
                    # Download file from URL and upload to S3
                    s3_url = self.storage.download_and_upload_to_s3(
                        post=post,
                        media_url=media_url,
                        user_id=user_id
                    )
                    
                    # Determine media type from S3 URL (or original URL)
                    media_type = self.storage._determine_media_type_from_url(s3_url)
                    
                    # Create Media record with the S3 URL (linked to post)
                    self.storage.create_media(
                        post=post,
                        s3_url=s3_url,
                        media_type=media_type
                    )
                except Exception as e:
                    # If one URL fails, return error
                    return self.response.s3_upload_error_response(str(e))
            
            # Return success response
            return self.response.post_created_successfully_response(str(post.post_id))
            
        except Exception as e:
            return self.response.validation_error_response(f"Failed to create post: {str(e)}")

