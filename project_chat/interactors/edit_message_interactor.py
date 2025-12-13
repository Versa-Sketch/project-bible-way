"""
Interactor for editing messages.

Handles the business logic for editing messages (24 hour limit).
"""

from typing import Dict, Any
from project_chat.storage import ChatDB
from project_chat.presenters.message_response import MessageResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse
from project_chat.websocket.utils import can_edit_message, ErrorCodes
from project_chat.models import Message


class EditMessageInteractor:
    """Interactor for editing messages."""
    
    def __init__(self, storage: ChatDB, response: MessageResponse, error_response: ChatErrorResponse):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def edit_message_interactor(
        self,
        user_id: str,
        message_id: str,
        text: str,
        request_id: str = ""
    ) -> Dict[str, Any]:
        """
        Edit a message.
        
        Args:
            user_id: ID of the user editing the message
            message_id: ID of the message to edit
            text: New text content
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
        
        # Check if message can still be edited (24 hour limit)
        if not can_edit_message(message.created_at):
            return self.error_response.edit_time_expired(request_id)
        
        # Check if message is deleted
        if message.is_deleted_for_everyone:
            return self.error_response.message_not_found(request_id)
        
        # Validate text
        if not text or not text.strip():
            return self.error_response.validation_error("Message text cannot be empty", request_id)
        
        # Update message
        updated_message = self.storage.update_message(message_id, text=text)
        if not updated_message:
            return self.error_response.server_error(request_id)
        
        # Return success acknowledgment
        return self.response.success_ack(
            request_id=request_id,
            action="edit_message",
            data={
                "message_id": str(updated_message.id),
                "text": updated_message.text,
                "edited_at": updated_message.edited_at.isoformat() if updated_message.edited_at else None
            }
        )
    
    def get_message_for_broadcast(self, message: Message) -> Dict[str, Any]:
        """Get formatted message for broadcasting edit to other users."""
        return self.response.message_edited_broadcast(message)

