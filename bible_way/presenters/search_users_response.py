from rest_framework.response import Response
from rest_framework import status


class SearchUsersResponse:

    @staticmethod
    def search_success_response(users: list, total_count: int, query: str) -> Response:
        return Response(
            {
                "success": True,
                "data": users,
                "total_count": total_count,
                "query": query
            },
            status=status.HTTP_200_OK
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

