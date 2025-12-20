from rest_framework.response import Response
from rest_framework import status


class DeleteReadingNoteResponse:

    @staticmethod
    def note_deleted_successfully_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "delete successfully"
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def note_not_found_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Note not found",
                "error_code": "NOTE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "You are not authorized to delete this note",
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
