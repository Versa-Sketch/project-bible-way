from rest_framework.response import Response
from rest_framework import status


class GetSpecificUserPostsResponse:

    @staticmethod
    def user_posts_retrieved_successfully_response(posts_data: list, pagination_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "User posts retrieved successfully",
                "data": posts_data,
                "pagination": {
                    "limit": pagination_data['limit'],
                    "offset": pagination_data['offset'],
                    "total_count": pagination_data['total_count'],
                    "has_next": pagination_data['has_next'],
                    "has_previous": pagination_data['has_previous']
                }
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
    def user_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "User not found",
                "error_code": "USER_NOT_FOUND"
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

