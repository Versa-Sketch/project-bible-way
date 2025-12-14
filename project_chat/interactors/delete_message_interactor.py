"""
Interactor for deleting messages.

Handles the business logic for deleting messages (7 day limit).
"""

from typing import Dict, Any
from project_chat.storage import ChatDB
from project_chat.presenters.message_response import MessageResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse
from project_chat.websocket.utils import can_delete_message


class DeleteMessageInteractor:
    """Interactor for deleting messages."""
    
    def __init__(self, storage: ChatDB, response: MessageResponse, error_response: ChatErrorResponse):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def delete_message_interactor(
        self,
        user_id: str,
        message_id: str,
        request_id: str = ""
    ) -> Dict[str, Any]:
        """
        Delete a message.
        
        Args:
            user_id: ID of the user deleting the message
            message_id: ID of the message to delete
            request_id: Request ID for acknowledgment
            
        Returns:
            Dictionary response for WebSocket
        """
        # Get message
        message = self.storage.get_message_by_id(message_id)
        if not message:
            return self.error_response.message_not_found(request_id)
        
        # Check ownership
        if not self.storage.check_message_ownership(message_id, user_id):
            return self.error_response.unauthorized(request_id)
        
        # Check if message can still be deleted (7 day limit)
        if not can_delete_message(message.created_at):
            return self.error_response.delete_time_expired(request_id)
        
        # Check if already deleted
        if message.is_deleted_for_everyone:
            return self.error_response.message_not_found(request_id)
        
        # Delete message (soft delete)
        deleted_message = self.storage.delete_message(message_id)
        if not deleted_message:
            return self.error_response.server_error(request_id)
        
        # Return success acknowledgment
        return self.response.success_ack(
            request_id=request_id,
            action="delete_message",
            data={
                "message_id": str(deleted_message.id),
                "conversation_id": str(deleted_message.conversation_id)
            }
        )
    
    def get_delete_broadcast(self, message_id: str, conversation_id: str) -> Dict[str, Any]:
        """Get formatted delete broadcast for other users."""
        return self.response.message_deleted_broadcast(message_id, conversation_id)

