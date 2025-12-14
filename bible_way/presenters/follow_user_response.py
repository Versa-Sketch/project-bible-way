from rest_framework.response import Response
from rest_framework import status


class FollowUserResponse:

    @staticmethod
    def follow_success_response(conversation_id: str = None) -> Response:
        data = {
            "success": True,
            "message": "Followed successfully"
        }
        if conversation_id:
            data["conversation_id"] = conversation_id
        return Response(
            data,
            status=status.HTTP_200_OK
        )

    @staticmethod
    def already_following_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are already following this user",
                "error_code": "ALREADY_FOLLOWING"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def cannot_follow_yourself_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You cannot follow yourself",
                "error_code": "CANNOT_FOLLOW_YOURSELF"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def user_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "User to follow not found",
                "error_code": "USER_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

