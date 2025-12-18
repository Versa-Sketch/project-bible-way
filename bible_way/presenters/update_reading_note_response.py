from rest_framework.response import Response
from rest_framework import status


class UpdateReadingNoteResponse:

    @staticmethod
    def reading_note_updated_successfully_response(note_id: str) -> Response:
        return Response(
            {
                "success": True,
                "message": "updated successfully",
                "note_id": note_id
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def note_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Reading note not found",
                "error_code": "NOTE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not authorized to update this reading note",
                "error_code": "UNAUTHORIZED"
            },
            status=status.HTTP_403_FORBIDDEN
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
