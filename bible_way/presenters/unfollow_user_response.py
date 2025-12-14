from rest_framework.response import Response
from rest_framework import status


class UnfollowUserResponse:

    @staticmethod
    def unfollow_success_response(conversation_id: str = None) -> Response:
        data = {
            "success": True,
            "message": "Unfollowed successfully"
        }
        if conversation_id:
            data["conversation_id"] = conversation_id
        return Response(
            data,
            status=status.HTTP_200_OK
        )

    @staticmethod
    def not_following_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not following this user",
                "error_code": "NOT_FOLLOWING"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def cannot_unfollow_yourself_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You cannot unfollow yourself",
                "error_code": "CANNOT_UNFOLLOW_YOURSELF"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def user_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "User to unfollow not found",
                "error_code": "USER_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

