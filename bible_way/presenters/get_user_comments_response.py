from rest_framework.response import Response
from rest_framework import status


class GetUserCommentsResponse:

    @staticmethod
    def user_comments_retrieved_successfully_response(comments_data: list) -> Response:
        return Response(
            {
                "success": True,
                "message": "User comments retrieved successfully",
                "data": comments_data
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

