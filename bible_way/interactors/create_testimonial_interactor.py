from bible_way.storage import UserDB
from bible_way.presenters.create_testimonial_response import CreateTestimonialResponse
from rest_framework.response import Response


class CreateTestimonialInteractor:
    def __init__(self, storage: UserDB, response: CreateTestimonialResponse):
        self.storage = storage
        self.response = response

    def create_testimonial_interactor(self, user_id: str, description: str, rating: int, media_files: list = None) -> Response:
        if not description or not description.strip():
            return self.response.validation_error_response("Description is required")
        
        if rating is None:
            return self.response.validation_error_response("Rating is required")
        
        if rating < 1 or rating > 5:
            return self.response.validation_error_response("Rating must be between 1 and 5")
        
        try:
            testimonial = self.storage.create_testimonial(
                user_id=user_id,
                description=description,
                rating=rating
            )
            
            # Handle media file uploads
            if media_files:
                for media_file in media_files:
                    try:
                        if not media_file or not hasattr(media_file, 'name'):
                            continue
                        
                        media_type = self.storage.get_media_type_from_file(media_file)
                        
                        s3_url = self.storage.upload_file_to_s3(
                            testimonial=testimonial,
                            media_file=media_file,
                            user_id=user_id
                        )
                        
                        self.storage.create_media(
                            testimonial=testimonial,
                            s3_url=s3_url,
                            media_type=media_type
                        )
                    except Exception as e:
                        return self.response.error_response(f"Failed to upload media: {str(e)}")
            
            return self.response.testimonial_created_successfully_response(str(testimonial.testimonial_id))
        except Exception as e:
            return self.response.error_response(f"Failed to create testimonial: {str(e)}")

