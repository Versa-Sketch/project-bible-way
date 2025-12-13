"""
HTTP views for chat file uploads.

Handles file uploads via REST API endpoints.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from project_chat.storage.s3_utils import upload_chat_file_to_s3
from project_chat.websocket.utils import validate_uploaded_file, determine_file_type_from_filename, ErrorCodes
import uuid
from datetime import datetime


class ChatFileUploadView(APIView):
    """Handle file uploads for chat messages."""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Upload a file for chat messages.
        
        Request:
        - file (required): File to upload (multipart/form-data)
        - conversation_id (optional): Conversation ID for organizing files
        
        Returns:
        - file_url: S3 URL of uploaded file
        - file_type: IMAGE, VIDEO, or AUDIO
        - file_size: File size in bytes
        - file_name: Original filename
        """
        try:
            # Get file from request
            if 'file' not in request.FILES:
                return Response({
                    "success": False,
                    "error": "File is required",
                    "error_code": "VALIDATION_ERROR"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            file_obj = request.FILES['file']
            conversation_id = request.data.get('conversation_id')
            user_id = str(request.user.user_id)
            
            # Validate file
            is_valid, error_msg, file_type = validate_uploaded_file(file_obj)
            if not is_valid:
                # Map validation errors to error codes
                if "exceeds" in error_msg.lower() or "size" in error_msg.lower():
                    error_code = ErrorCodes.FILE_TOO_LARGE
                elif "invalid file type" in error_msg.lower() or "allowed" in error_msg.lower():
                    error_code = ErrorCodes.INVALID_FILE_TYPE
                else:
                    error_code = ErrorCodes.VALIDATION_ERROR
                
                return Response({
                    "success": False,
                    "error": error_msg,
                    "error_code": error_code
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique identifier for file
            file_uuid = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{file_uuid}_{file_obj.name}"
            
            # Upload to S3
            try:
                file_url = upload_chat_file_to_s3(
                    file_obj=file_obj,
                    filename=unique_filename,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    content_type=file_obj.content_type
                )
            except Exception as e:
                return Response({
                    "success": False,
                    "error": f"Failed to upload file: {str(e)}",
                    "error_code": ErrorCodes.FILE_UPLOAD_FAILED
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Return success response
            return Response({
                "success": True,
                "data": {
                    "file_url": file_url,
                    "file_type": file_type,
                    "file_size": file_obj.size,
                    "file_name": file_obj.name
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "error_code": ErrorCodes.SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
