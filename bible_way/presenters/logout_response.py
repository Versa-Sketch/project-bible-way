from rest_framework.response import Response
from rest_framework import status


class LogoutResponse:
    
    @staticmethod
    def logout_success_response() -> Response:
        return Response(
            {
                "success": True,
                "message": "Logout successful"
            },
            status=status.HTTP_200_OK
        )
    
    @staticmethod
    def unauthorized_response() -> Response:
        return Response(
            {
                "success": False,
                "error": "Authentication required",
                "error_code": "UNAUTHORIZED"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

