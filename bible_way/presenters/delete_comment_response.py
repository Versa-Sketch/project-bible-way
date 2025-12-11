from rest_framework.response import Response
from rest_framework import status


class DeleteCommentResponse:

    @staticmethod
    def comment_deleted_successfully_response(comment_id: str, is_comment_creator: bool) -> Response:
        return Response(
            {
                "success": True,
                "message": "Comment deleted successfully",
                "comment_id": comment_id,
                "is_comment_creator": is_comment_creator
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def comment_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Comment not found",
                "error_code": "COMMENT_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized_response(is_comment_creator: bool) -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not authorized to delete this comment",
                "error_code": "UNAUTHORIZED",
                "is_comment_creator": is_comment_creator
            },
            status=status.HTTP_403_FORBIDDEN
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

