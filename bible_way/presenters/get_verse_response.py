from rest_framework.response import Response
from rest_framework import status


class GetVerseResponse:

    @staticmethod
    def verse_retrieved_successfully_response(verse_data: dict) -> Response:
        return Response(
            {
                "success": True,
                "message": "Verse retrieved successfully",
                "data": verse_data
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def verse_not_found_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "No verse found",
                "data": None
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

