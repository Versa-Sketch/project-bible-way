"""
Response presenters for WebSocket chat messages.

Returns dictionary responses that will be sent as JSON over WebSocket.
"""

from typing import Optional, Dict, Any
from project_chat.models import Message, Conversation


class MessageResponse:
    """Response formatting for message-related WebSocket actions."""
    
    @staticmethod
    def success_ack(request_id: str, action: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format a successful acknowledgment response."""
        response = {
            "type": "ack",
            "action": action,
            "request_id": request_id,
            "ok": True,
        }
        if data:
            response["data"] = data
        return response
    
    @staticmethod
    def error_ack(request_id: str, action: str, error: str, error_code: str) -> Dict[str, Any]:
        """Format an error acknowledgment response."""
        return {
            "type": "ack",
            "action": action,
            "request_id": request_id,
            "ok": False,
            "error": error,
            "error_code": error_code
        }
    
    @staticmethod
    def message_sent_broadcast(message: Message) -> Dict[str, Any]:
        """Format a message sent broadcast (sent to other users)."""
        data = {
            "message_id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "sender_id": str(message.sender.user_id),
            "sender_name": message.sender.username,
            "sender_email": message.sender.email,
            "text": message.text,
            "file": {
                "url": message.file,
                "type": message.file_type,
                "size": message.file_size,
                "name": message.file_name
            } if message.file else None,
            "reply_to_id": str(message.reply_to_id) if message.reply_to else None,
            "created_at": message.created_at.isoformat() if message.created_at else None,
            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
            "is_deleted_for_everyone": message.is_deleted_for_everyone,
        }
        
        # Add post preview if message shares a post
        if message.shared_post:
            data["shared_post"] = {
                "post_id": str(message.shared_post.post_id),
                "title": message.shared_post.title,
                "description": message.shared_post.description[:200] if message.shared_post.description else "",  # Preview
                "created_at": message.shared_post.created_at.isoformat() if message.shared_post.created_at else None,
                "media": [
                    {
                        "media_id": str(media.media_id),
                        "media_type": media.media_type,
                        "url": media.url
                    }
                    for media in message.shared_post.media.all()[:3]  # Limit to 3 media items for preview
                ]
            }
        
        return {
            "type": "message.sent",
            "data": data
        }
    
    @staticmethod
    def message_edited_broadcast(message: Message) -> Dict[str, Any]:
        """Format a message edited broadcast."""
        return {
            "type": "message.edited",
            "data": {
                "message_id": str(message.id),
                "conversation_id": str(message.conversation_id),
                "text": message.text,
                "edited_at": message.edited_at.isoformat() if message.edited_at else None,
            }
        }
    
    @staticmethod
    def message_deleted_broadcast(message_id: str, conversation_id: str) -> Dict[str, Any]:
        """Format a message deleted broadcast."""
        return {
            "type": "message.deleted",
            "data": {
                "message_id": message_id,
                "conversation_id": conversation_id,
            }
        }
    
    @staticmethod
    def connection_established(user_id: str) -> Dict[str, Any]:
        """Format a connection established message."""
        return {
            "type": "connection.established",
            "data": {
                "user_id": user_id,
                "message": "WebSocket connection established"
            }
        }
    
    @staticmethod
    def typing_indicator(user_id: str, user_name: str, conversation_id: str, is_typing: bool) -> Dict[str, Any]:
        """Format a typing indicator broadcast."""
        return {
            "type": "typing",
            "data": {
                "user_id": user_id,
                "user_name": user_name,
                "conversation_id": conversation_id,
                "is_typing": is_typing
            }
        }
    
    @staticmethod
    def read_receipt_updated(user_id: str, conversation_id: str, last_read_at: str) -> Dict[str, Any]:
        """Format a read receipt update broadcast."""
        return {
            "type": "read_receipt.updated",
            "data": {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "last_read_at": last_read_at
            }
        }
    
    @staticmethod
    def conversation_joined(conversation: Conversation) -> Dict[str, Any]:
        """Format a conversation joined response."""
        return {
            "type": "conversation.joined",
            "data": {
                "conversation_id": str(conversation.id),
                "type": conversation.type,
                "name": conversation.name,
            }
        }
    
    @staticmethod
    def conversation_left(conversation_id: str) -> Dict[str, Any]:
        """Format a conversation left response."""
        return {
            "type": "conversation.left",
            "data": {
                "conversation_id": conversation_id,
            }
        }
    
    @staticmethod
    def presence_status_broadcast(user_id: str, is_online: bool, conversation_id: str, last_seen: Optional[str] = None) -> Dict[str, Any]:
        """Format a presence status broadcast."""
        data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "is_online": is_online
        }
        if last_seen:
            data["last_seen"] = last_seen
        return {
            "type": "presence.updated",
            "data": data
        }

