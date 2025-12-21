from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import UserProfileResponseDTO


class UserProfileResponse:

    @staticmethod
    def user_profile_success_response(response_dto: UserProfileResponseDTO) -> Response:
        return Response(
            {
                "success": True,
                "message": "User profile retrieved successfully",
                "data": {
                    "user_id": str(response_dto.user_id),
                    "user_name": response_dto.user_name,
                    "email": response_dto.email,
                    "country": response_dto.country,
                    "age": response_dto.age,
                    "preferred_language": response_dto.preferred_language,
                    "profile_picture_url": response_dto.profile_picture_url,
                    "is_admin": response_dto.is_admin,
                    "following_count": response_dto.following_count,
                    "followers_count": response_dto.followers_count
                }
            },
            status=status.HTTP_200_OK
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
    def invalid_user_name_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "User name is required",
                "error_code": "INVALID_USER_NAME"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

