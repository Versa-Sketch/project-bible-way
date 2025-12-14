"""
Interactor for marking messages as read.

Handles the business logic for updating read receipts.
"""

from typing import Dict, Any, Optional
from project_chat.storage import ChatDB
from project_chat.presenters.message_response import MessageResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse


class MarkReadInteractor:
    """Interactor for marking messages as read."""
    
    def __init__(self, storage: ChatDB, response: MessageResponse, error_response: ChatErrorResponse):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def mark_read_interactor(
        self,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str] = None,
        request_id: str = ""
    ) -> Dict[str, Any]:
        """
        Mark messages as read in a conversation.
        
        Args:
            user_id: ID of the user marking as read
            conversation_id: ID of the conversation
            message_id: Optional specific message ID to mark as read
            request_id: Request ID for acknowledgment
            
        Returns:
            Dictionary response for WebSocket
        """
        # Validate conversation exists
        conversation = self.storage.get_conversation_by_id(conversation_id)
        if not conversation:
            return self.error_response.conversation_not_found(request_id)
        
        # Check user is a member
        if not self.storage.check_user_membership(user_id, conversation_id):
            return self.error_response.not_member(request_id)
        
        # Update read receipt
        if message_id:
            # Mark specific message as read
            receipt = self.storage.create_message_read_receipt(user_id, message_id, conversation_id)
            if not receipt:
                return self.error_response.message_not_found(request_id)
        else:
            # Mark all messages in conversation as read
            success = self.storage.update_read_receipt(user_id, conversation_id)
            if not success:
                return self.error_response.server_error(request_id)
        
        # Return success acknowledgment
        from datetime import datetime
        return self.response.success_ack(
            request_id=request_id,
            action="mark_read",
            data={
                "conversation_id": conversation_id,
                "last_read_at": datetime.now().isoformat()
            }
        )
    
    def get_read_receipt_broadcast(
        self,
        user_id: str,
        conversation_id: str,
        last_read_at: str
    ) -> Dict[str, Any]:
        """Get formatted read receipt broadcast for other users."""
        return self.response.read_receipt_updated(user_id, conversation_id, last_read_at)

