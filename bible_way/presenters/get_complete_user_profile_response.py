from rest_framework.response import Response
from rest_framework import status
from bible_way.storage.dtos import CompleteUserProfileResponseDTO


class GetCompleteUserProfileResponse:

    @staticmethod
    def complete_user_profile_success_response(response_dto: CompleteUserProfileResponseDTO) -> Response:
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
                    "followers_count": response_dto.followers_count,
                    "following_count": response_dto.following_count,
                    "is_following": response_dto.is_following
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
    def validation_error_response(message: str) -> Response:
        return Response(
            {
                "success": False,
                "error": message,
                "error_code": "VALIDATION_ERROR"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

