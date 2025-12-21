from rest_framework.response import Response
from rest_framework import status


class GetTopBooksReadingProgressResponse:

    @staticmethod
    def top_books_retrieved_successfully_response(books_data: list) -> Response:
        return Response(
            {
                "success": True,
                "message": "Top books retrieved successfully",
                "data": books_data
            },
            status=status.HTTP_200_OK
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

