from rest_framework.response import Response
from rest_framework import status


class DeletePostResponse:

    @staticmethod
    def post_deleted_successfully_response(post_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Post deleted successfully",
                "post_id": post_id
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
    def unauthorized_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not authorized to delete this post",
                "error_code": "UNAUTHORIZED"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def error_response(error_message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": error_message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

