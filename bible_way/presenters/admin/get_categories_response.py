from rest_framework.response import Response
from rest_framework import status


class GetCategoriesResponse:

    @staticmethod
    def categories_retrieved_successfully_response(categories_data: list) -> Response:
        return Response(
            {
                "success": True,
                "message": "Categories retrieved successfully",
                "data": categories_data
            },
            status=status.HTTP_200_OK
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

