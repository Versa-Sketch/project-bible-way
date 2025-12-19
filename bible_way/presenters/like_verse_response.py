from rest_framework.response import Response
from rest_framework import status


class LikeVerseResponse:

    @staticmethod
    def verse_liked_successfully_response(reaction_id: str, verse_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "Verse liked successfully",
                "reaction_id": reaction_id,
                "verse_id": verse_id,
                "reaction_type": "like"
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
    def verse_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Verse not found",
                "error_code": "VERSE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def already_liked_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You have already liked this verse",
                "error_code": "ALREADY_LIKED"
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
