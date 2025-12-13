from bible_way.storage import UserDB
from bible_way.presenters.admin.create_promotion_response import CreatePromotionResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
from decimal import Decimal
import json
import os


class CreatePromotionInteractor:
    def __init__(self, storage: UserDB, response: CreatePromotionResponse):
        self.storage = storage
        self.response = response

    def create_promotion_interactor(self, title: str, description: str, price: str, redirect_link: str, meta_data_str: str = None, media_file=None, image_files: list = None) -> Response:
        if not title or not title.strip():
            return self.response.validation_error_response("Title is required")
        
        if not price:
            return self.response.validation_error_response("Price is required")
        
        try:
            price_decimal = Decimal(str(price))
        except (ValueError, TypeError):
            return self.response.validation_error_response("Invalid price format")
        
        if not redirect_link or not redirect_link.strip():
            return self.response.validation_error_response("Redirect link is required")
        
        meta_data = None
        if meta_data_str:
            try:
                meta_data = json.loads(meta_data_str)
            except json.JSONDecodeError:
                return self.response.validation_error_response("Invalid JSON format for meta_data")
        
        media_id = None
        if media_file:
            try:
                media_type = self.storage.get_media_type_from_file(media_file)
                media_key = f"promotions/media/{os.urandom(16).hex()}/{media_file.name}"
                media_url = s3_upload_file(media_file, media_key)
                
                from bible_way.models import Media
                media = Media.objects.create(
                    media_type=media_type,
                    url=media_url
                )
                media_id = str(media.media_id)
            except Exception as e:
                error_message = str(e)
                return self.response.error_response(f"Failed to upload media: {error_message}")
        
        try:
            promotion = self.storage.create_promotion(
                title=title,
                description=description or '',
                price=price_decimal,
                redirect_link=redirect_link,
                meta_data=meta_data,
                media_id=media_id
            )
            
            image_urls = []
            if image_files:
                for index, image_file in enumerate(image_files):
                    try:
                        image_key = f"promotions/images/{promotion.promotion_id}/{os.urandom(8).hex()}/{image_file.name}"
                        image_url = s3_upload_file(image_file, image_key)
                        image_urls.append(image_url)
                    except Exception as e:
                        return self.response.error_response(f"Failed to upload image {index + 1}: {str(e)}")
            
            if image_urls:
                self.storage.create_promotion_images(promotion, image_urls)
            
            return self.response.promotion_created_successfully_response(str(promotion.promotion_id))
        except Exception as e:
            error_message = str(e)
            if "Media not found" in error_message:
                return self.response.validation_error_response("Media not found")
            return self.response.error_response(f"Failed to create promotion: {error_message}")

