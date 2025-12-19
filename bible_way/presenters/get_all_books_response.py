from rest_framework.response import Response
from rest_framework import status


class GetAllBooksResponse:

    @staticmethod
    def books_retrieved_successfully_response(books_data, total_count) -> Response:
        return Response(
            {
                "success": True,
                "message": "Books retrieved successfully",
                "data": books_data,
                "total_count": total_count
            },
            status=status.HTTP_200_OK
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
