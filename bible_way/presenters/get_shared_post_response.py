from rest_framework.response import Response
from rest_framework import status


class GetSharedPostResponse:
    def post_retrieved_successfully_response(self, post_data: dict) -> Response:
        return Response({
            "success": True,
            "message": "Post retrieved successfully",
            "data": post_data
        }, status=status.HTTP_200_OK)
    
    def invalid_token_response(self) -> Response:
        return Response({
            "success": False,
            "error": "Invalid or expired share link",
            "error_code": "INVALID_SHARE_TOKEN"
        }, status=status.HTTP_404_NOT_FOUND)
    
    def post_not_found_response(self) -> Response:
        return Response({
            "success": False,
            "error": "Post no longer available",
            "error_code": "POST_NOT_FOUND"
        }, status=status.HTTP_404_NOT_FOUND)
    
    def error_response(self, error_message: str) -> Response:
        return Response({
            "success": False,
            "error": error_message,
            "error_code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

