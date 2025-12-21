from rest_framework.response import Response
from rest_framework import status


class GetAllVersesResponse:

    @staticmethod
    def verses_retrieved_successfully_response(verses_data: list) -> Response:
        message = "Verses retrieved successfully" if verses_data else "No verses found"
        return Response(
            {
                "success": True,
                "message": message,
                "data": verses_data,
                "total_count": len(verses_data)
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

