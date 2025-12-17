from rest_framework.response import Response
from rest_framework import status


class GetAllBooksResponse:

    @staticmethod
    def books_retrieved_successfully_response(books_data: list, total_count: int, limit: int = None, offset: int = 0) -> Response:
        response_data = {
            "success": True,
            "message": "Books retrieved successfully",
            "data": books_data,
            "total_count": total_count
        }
        
        # Add pagination info if limit is provided
        if limit is not None:
            response_data["pagination"] = {
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total_count,
                "has_previous": offset > 0
            }
        
        return Response(response_data, status=status.HTTP_200_OK)

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

