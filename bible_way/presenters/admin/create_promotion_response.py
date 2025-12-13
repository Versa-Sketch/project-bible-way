from rest_framework.response import Response
from rest_framework import status


class CreatePromotionResponse:

    @staticmethod
    def promotion_created_successfully_response(promotion_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Promotion created successfully",
                "promotion_id": promotion_id
            },
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def validation_error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def invalid_media_type_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Invalid media type. Only images, videos, and audio files are allowed",
                "error_code": "INVALID_MEDIA_TYPE"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

