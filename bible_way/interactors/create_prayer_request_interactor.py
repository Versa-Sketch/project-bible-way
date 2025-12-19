from bible_way.storage import UserDB
from bible_way.presenters.create_prayer_request_response import CreatePrayerRequestResponse
from rest_framework.response import Response


class CreatePrayerRequestInteractor:
    def __init__(self, storage: UserDB, response: CreatePrayerRequestResponse):
        self.storage = storage
        self.response = response

    def create_prayer_request_interactor(self, user_id: str, description: str, media_files: list = None) -> Response:
        if not description or not description.strip():
            return self.response.validation_error_response("Description is required")
        
        try:
            prayer_request = self.storage.create_prayer_request(
                user_id=user_id,
                description=description
            )
            
            # Handle media file uploads
            if media_files:
                for media_file in media_files:
                    try:
                        if not media_file or not hasattr(media_file, 'name'):
                            continue
                        
                        media_type = self.storage.get_media_type_from_file(media_file)
                        
                        s3_url = self.storage.upload_file_to_s3(
                            prayer_request=prayer_request,
                            media_file=media_file,
                            user_id=user_id
                        )
                        
                        self.storage.create_media(
                            prayer_request=prayer_request,
                            s3_url=s3_url,
                            media_type=media_type
                        )
                    except Exception as e:
                        return self.response.error_response(f"Failed to upload media: {str(e)}")
            
            return self.response.prayer_request_created_successfully_response(str(prayer_request.prayer_request_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create prayer request: {str(e)}")

