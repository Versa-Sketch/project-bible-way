from rest_framework.response import Response
from rest_framework import status


class CreateBookmarkResponse:

    @staticmethod
    def bookmark_created_successfully_response(bookmark_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Bookmark created successfully",
                "bookmark_id": bookmark_id
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
    
    @staticmethod
    def already_bookmarked_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "already book_marked",
                "error_code": "ALREADY_BOOKMARKED"
            },
            status=status.HTTP_400_BAD_REQUEST
        )