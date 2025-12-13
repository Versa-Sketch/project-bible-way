"""
Error response presenters for WebSocket chat.

Provides standardized error responses for WebSocket connections.
"""

from typing import Dict, Any
from project_chat.websocket.utils import ErrorCodes


class ChatErrorResponse:
    """Error response formatting for WebSocket chat."""
    
    @staticmethod
    def invalid_token(request_id: str = None) -> Dict[str, Any]:
        """Invalid or missing JWT token."""
        response = {
            "type": "error",
            "error": "Invalid or missing authentication token",
            "error_code": ErrorCodes.INVALID_TOKEN
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def token_expired(request_id: str = None) -> Dict[str, Any]:
        """JWT token has expired."""
        response = {
            "type": "error",
            "error": "Authentication token has expired",
            "error_code": ErrorCodes.TOKEN_EXPIRED
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def user_not_found(request_id: str = None) -> Dict[str, Any]:
        """User not found."""
        response = {
            "type": "error",
            "error": "User not found",
            "error_code": ErrorCodes.USER_NOT_FOUND
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def conversation_not_found(request_id: str = None) -> Dict[str, Any]:
        """Conversation not found."""
        response = {
            "type": "error",
            "error": "Conversation not found",
            "error_code": ErrorCodes.CONVERSATION_NOT_FOUND
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def not_member(request_id: str = None) -> Dict[str, Any]:
        """User is not a member of the conversation."""
        response = {
            "type": "error",
            "error": "You are not a member of this conversation",
            "error_code": ErrorCodes.NOT_MEMBER
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def message_not_found(request_id: str = None) -> Dict[str, Any]:
        """Message not found."""
        response = {
            "type": "error",
            "error": "Message not found",
            "error_code": ErrorCodes.MESSAGE_NOT_FOUND
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def unauthorized(request_id: str = None) -> Dict[str, Any]:
        """User not authorized for this action."""
        response = {
            "type": "error",
            "error": "You are not authorized to perform this action",
            "error_code": ErrorCodes.UNAUTHORIZED
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def validation_error(error_message: str, request_id: str = None) -> Dict[str, Any]:
        """Validation error."""
        response = {
            "type": "error",
            "error": error_message,
            "error_code": ErrorCodes.VALIDATION_ERROR
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def rate_limit_exceeded(request_id: str = None) -> Dict[str, Any]:
        """Rate limit exceeded."""
        response = {
            "type": "error",
            "error": "Rate limit exceeded. Please try again later.",
            "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def edit_time_expired(request_id: str = None) -> Dict[str, Any]:
        """Message edit time limit expired."""
        response = {
            "type": "error",
            "error": "Message can only be edited within 24 hours of creation",
            "error_code": ErrorCodes.EDIT_TIME_EXPIRED
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def delete_time_expired(request_id: str = None) -> Dict[str, Any]:
        """Message delete time limit expired."""
        response = {
            "type": "error",
            "error": "Message can only be deleted within 7 days of creation",
            "error_code": ErrorCodes.DELETE_TIME_EXPIRED
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def invalid_action(request_id: str = None) -> Dict[str, Any]:
        """Invalid action requested."""
        response = {
            "type": "error",
            "error": "Invalid action",
            "error_code": ErrorCodes.INVALID_ACTION
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def server_error(request_id: str = None) -> Dict[str, Any]:
        """Internal server error."""
        response = {
            "type": "error",
            "error": "An internal server error occurred",
            "error_code": ErrorCodes.SERVER_ERROR
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def no_follow_relationship(request_id: str = None) -> Dict[str, Any]:
        """Sender doesn't follow receiver."""
        response = {
            "type": "error",
            "error": "You must follow this user to send messages",
            "error_code": ErrorCodes.NO_FOLLOW_RELATIONSHIP
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def post_not_found(request_id: str = None) -> Dict[str, Any]:
        """Post not found."""
        response = {
            "type": "error",
            "error": "Post not found",
            "error_code": ErrorCodes.POST_NOT_FOUND
        }
        if request_id:
            response["request_id"] = request_id
        return response
    
    @staticmethod
    def post_sharing_not_allowed(request_id: str = None) -> Dict[str, Any]:
        """Post sharing not allowed."""
        response = {
            "type": "error",
            "error": "You are not allowed to share this post",
            "error_code": ErrorCodes.POST_SHARING_NOT_ALLOWED
        }
        if request_id:
            response["request_id"] = request_id
        return response

