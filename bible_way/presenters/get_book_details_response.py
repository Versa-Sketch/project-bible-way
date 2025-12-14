from rest_framework.response import Response
from rest_framework import status


class GetBookDetailsResponse:

    @staticmethod
    def book_details_retrieved_successfully_response(book_data: dict, chapters_data: list) -> Response:
        return Response(
            {
                "success": True,
                "message": "Book details retrieved successfully",
                "data": {
                    "book": book_data,
                    "chapters": chapters_data
                }
            },
            status=status.HTTP_200_OK
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
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

