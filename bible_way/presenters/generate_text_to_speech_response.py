from rest_framework.response import Response
from rest_framework import status


class GenerateTextToSpeechResponse:

    @staticmethod
    def audio_generated_successfully_response(
        blocks_data: list,
        total_blocks: int,
        total_duration: float,
        audio_format: str
    ) -> Response:
        return Response(
            {
                "success": True,
                "message": f"Audio generated successfully for {total_blocks} block{'s' if total_blocks != 1 else ''}",
                "blocks": blocks_data,
                "total_blocks": total_blocks,
                "audio_format": audio_format,
                "total_duration": total_duration
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

