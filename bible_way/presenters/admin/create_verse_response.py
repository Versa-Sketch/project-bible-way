from rest_framework.response import Response
from rest_framework import status


class CreateVerseResponse:

    @staticmethod
    def verse_created_successfully_response(verse_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Verse created successfully",
                "verse_id": verse_id
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
    def verse_already_exists_today_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "A verse has already been created today. Only one verse can be added per day.",
                "error_code": "VERSE_ALREADY_EXISTS_TODAY"
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

