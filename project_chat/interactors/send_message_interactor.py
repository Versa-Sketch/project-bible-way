"""
Interactor for sending messages in conversations.

Handles the business logic for creating and sending messages.
"""

from typing import Optional, Dict, Any
from project_chat.storage import ChatDB
from project_chat.presenters.message_response import MessageResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse
from project_chat.websocket.utils import validate_message_data, ErrorCodes
from project_chat.models import Message, ConversationTypeChoices


class SendMessageInteractor:
    """Interactor for sending messages."""
    
    def __init__(self, storage: ChatDB, response: MessageResponse, error_response: ChatErrorResponse):
        self.storage = storage
        self.response = response
        self.error_response = error_response
    
    def send_message_interactor(
        self,
        user_id: str,
        conversation_id: str,
        text: str = "",
        file=None,
        reply_to_id: Optional[str] = None,
        shared_post_id: Optional[str] = None,
        request_id: str = ""
    ) -> Dict[str, Any]:
        """
        Send a message in a conversation.
        
        Args:
            user_id: ID of the user sending the message
            conversation_id: ID of the conversation
            text: Message text content
            file: Optional file attachment
            reply_to_id: Optional ID of message being replied to
            request_id: Request ID for acknowledgment
            
        Returns:
            Dictionary response for WebSocket
        """
        try:
            # Validate conversation exists
            conversation = self.storage.get_conversation_by_id(conversation_id)
            if not conversation:
                return self.error_response.conversation_not_found(request_id)
            
            # Check user is a member
            if not self.storage.check_user_membership(user_id, conversation_id):
                return self.error_response.not_member(request_id)
            
            # Check follow relationship for DIRECT conversations
            if conversation.type == ConversationTypeChoices.DIRECT:
                # Get conversation members (should be 2 for DIRECT)
                members = self.storage.get_conversation_members(conversation_id)
                if len(members) == 2:
                    receiver_id = str(members[0].user_id) if str(members[0].user_id) != user_id else str(members[1].user_id)
                    # Check if sender follows receiver (one-way follow check)
                    if not self.storage.check_follow_relationship(user_id, receiver_id):
                        return self.error_response.no_follow_relationship(request_id)
            
            # Validate post if shared_post_id is provided
            if shared_post_id:
                from bible_way.storage import UserDB
                user_db = UserDB()
                post = user_db.get_post_by_id(shared_post_id)
                if not post:
                    return self.error_response.post_not_found(request_id)
                # Optionally check if user has access to the post (for future privacy features)
            
            # Validate message data
            data = {
                'conversation_id': conversation_id,
                'content': text,
                'file': file,
                'shared_post_id': shared_post_id
            }
            is_valid, error_msg = validate_message_data(data)
            if not is_valid:
                return self.error_response.validation_error(error_msg, request_id)
            
            # Create message
            message = self.storage.create_message(
                conversation_id=conversation_id,
                sender_id=user_id,
                text=text,
                file=file,
                reply_to_id=reply_to_id,
                shared_post_id=shared_post_id
            )
            
            if not message:
                return self.error_response.server_error(request_id)
            
            # Return success acknowledgment
            return self.response.success_ack(
                request_id=request_id,
                action="send_message",
                data={
                    "message_id": str(message.id),
                    "created_at": message.created_at.isoformat() if message.created_at else None
                }
            )
        except Exception as e:
            import traceback
            print(f"Error in send_message_interactor: {e}")
            print(traceback.format_exc())
            return self.error_response.server_error(request_id)
    
    def get_message_for_broadcast(self, message: Message) -> Dict[str, Any]:
        """Get formatted message for broadcasting to other users."""
        return self.response.message_sent_broadcast(message)

