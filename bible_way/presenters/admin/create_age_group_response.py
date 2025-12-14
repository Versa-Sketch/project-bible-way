from rest_framework.response import Response
from rest_framework import status


class CreateAgeGroupResponse:

    @staticmethod
    def age_group_created_successfully_response(age_group_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "Age group created successfully",
                "data": age_group_data
            },
            status=status.HTTP_201_CREATED
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

