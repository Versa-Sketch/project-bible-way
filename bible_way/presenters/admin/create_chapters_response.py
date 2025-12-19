from rest_framework.response import Response
from rest_framework import status


class CreateChaptersResponse:

    @staticmethod
    def chapters_uploaded_successfully_response(chapters_count: int, book_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Chapters uploaded successfully",
                "chaptersCount": chapters_count,
                "book_id": book_id
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
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
