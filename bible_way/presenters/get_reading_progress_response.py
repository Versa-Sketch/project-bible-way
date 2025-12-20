from rest_framework.response import Response
from rest_framework import status


class GetReadingProgressResponse:

    @staticmethod
    def reading_progress_retrieved_successfully_response(progress_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "Reading progress retrieved successfully",
                "data": progress_data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def reading_progress_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Reading progress not found",
                "error_code": "READING_PROGRESS_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def book_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Book not found",
                "error_code": "BOOK_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
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
