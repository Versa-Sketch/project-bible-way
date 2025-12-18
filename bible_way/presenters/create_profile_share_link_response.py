from rest_framework.response import Response
from rest_framework import status


class CreateProfileShareLinkResponse:
    def share_link_created_successfully_response(self, share_url: str, share_token: str) -> Response:
        return Response({
            "success": True,
            "message": "Share link created successfully",
            "share_url": share_url,
            "share_token": share_token
        }, status=status.HTTP_201_CREATED)
    
    def validation_error_response(self, error_message: str) -> Response:
        return Response({
            "success": False,
            "error": error_message,
            "error_code": "VALIDATION_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def user_not_found_response(self) -> Response:
        return Response({
            "success": False,
            "error": "User not found",
            "error_code": "USER_NOT_FOUND"
        }, status=status.HTTP_404_NOT_FOUND)
    
    def error_response(self, error_message: str) -> Response:
        return Response({
            "success": False,
            "error": error_message,
            "error_code": "INTERNAL_ERROR"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

