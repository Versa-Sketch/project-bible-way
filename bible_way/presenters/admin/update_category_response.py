from rest_framework.response import Response
from rest_framework import status


class UpdateCategoryResponse:

    @staticmethod
    def category_updated_successfully_response(category_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "Category updated successfully",
                "data": category_data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def category_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Category not found",
                "error_code": "CATEGORY_NOT_FOUND"
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

