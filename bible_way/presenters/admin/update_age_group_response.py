from rest_framework.response import Response
from rest_framework import status


class UpdateAgeGroupResponse:

    @staticmethod
    def age_group_updated_successfully_response(age_group_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "Age group updated successfully",
                "data": age_group_data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def age_group_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Age group not found",
                "error_code": "AGE_GROUP_NOT_FOUND"
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

