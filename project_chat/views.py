"""
HTTP views for chat file uploads and conversation operations.

Handles file uploads and conversation retrieval via REST API endpoints.
"""

from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from project_chat.storage.s3_utils import upload_chat_file_to_s3
from project_chat.websocket.utils import validate_uploaded_file, determine_file_type_from_filename, ErrorCodes
from project_chat.storage import ChatDB
from project_chat.interactors.get_conversation_interactor import GetConversationInteractor
from project_chat.interactors.get_inbox_interactor import GetInboxInteractor
from project_chat.presenters.conversation_response import ConversationResponse
from project_chat.presenters.inbox_response import InboxResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse
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


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_conversation_view(request, conversation_id):
    """
    Get conversation details by ID.
    
    GET /api/chat/conversation/<conversation_id>/
    """
    user_id = str(request.user.user_id)
    
    interactor = GetConversationInteractor(
        storage=ChatDB(),
        response=ConversationResponse(),
        error_response=ChatErrorResponse()
    )
    
    result = interactor.get_conversation_interactor(
        conversation_id=conversation_id,
        user_id=user_id
    )
    
    # Convert dict response to Response object
    if result.get('success'):
        return Response(result, status=status.HTTP_200_OK)
    else:
        # Extract error details from WebSocket format
        error_code = result.get('error_code', 'INTERNAL_ERROR')
        error_message = result.get('error', 'An error occurred')
        
        # Format REST API error response
        error_response = {
            "success": False,
            "error": error_message,
            "error_code": error_code
        }
        
        if error_code == 'CONVERSATION_NOT_FOUND':
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)
        elif error_code == 'NOT_MEMBER':
            return Response(error_response, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_inbox_view(request):
    """
    Get inbox (all conversations) for current user.
    
    GET /api/chat/inbox/
    """
    user_id = str(request.user.user_id)
    
    interactor = GetInboxInteractor(
        storage=ChatDB(),
        response=InboxResponse()
    )
    
    result = interactor.get_inbox_interactor(user_id=user_id)
    
    if result.get('success'):
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
