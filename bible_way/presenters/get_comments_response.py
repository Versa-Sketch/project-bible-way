from rest_framework.response import Response
from rest_framework import status


class GetCommentsResponse:

    @staticmethod
    def comments_retrieved_successfully_response(post_id: str, comments_data: list) -> Response:
        return Response(
            {
                "success": True,
                "message": "Comments retrieved successfully",
                "post_id": post_id,
                "data": comments_data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def post_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Post not found",
                "error_code": "POST_NOT_FOUND"
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

