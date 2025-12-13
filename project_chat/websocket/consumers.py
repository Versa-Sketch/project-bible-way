"""
WebSocket consumers for real-time chat functionality.

Handles WebSocket connections, message sending, editing, deletion, and presence.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from typing import Dict, Any, Set
from datetime import datetime

from project_chat.storage import ChatDB
from project_chat.presenters.message_response import MessageResponse
from project_chat.presenters.chat_error_response import ChatErrorResponse
from project_chat.interactors.send_message_interactor import SendMessageInteractor
from project_chat.interactors.edit_message_interactor import EditMessageInteractor
from project_chat.interactors.delete_message_interactor import DeleteMessageInteractor
from project_chat.interactors.mark_read_interactor import MarkReadInteractor
from project_chat.websocket.utils import check_rate_limit, ErrorCodes
from project_chat.websocket.middleware import JWTAuthMiddleware

User = get_user_model()

# In-memory presence tracking (shared across all consumer instances)
_online_users: Dict[str, datetime] = {}


class UserChatConsumer(AsyncWebsocketConsumer):
    """
    Unified WebSocket consumer for user connections.
    
    Handles all conversations for a single user through one connection.
    Recommended approach for mobile and web applications.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.user_groups: Set[str] = set()  # Track joined groups
        self.storage = ChatDB()
        self.message_response = MessageResponse()
        self.error_response = ChatErrorResponse()
        self.send_message_interactor = SendMessageInteractor(
            self.storage, self.message_response, self.error_response
        )
        self.edit_message_interactor = EditMessageInteractor(
            self.storage, self.message_response, self.error_response
        )
        self.delete_message_interactor = DeleteMessageInteractor(
            self.storage, self.message_response, self.error_response
        )
        self.mark_read_interactor = MarkReadInteractor(
            self.storage, self.message_response, self.error_response
        )
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4008)  # Policy violation - authentication required
            return
        
        self.user_id = str(self.user.user_id)
        
        # Join user's personal group for notifications
        user_group = f"user_{self.user_id}"
        await self.channel_layer.group_add(user_group, self.channel_name)
        self.user_groups.add(user_group)
        
        # Accept connection
        await self.accept()
        
        # Update presence status (user is now online)
        _online_users[self.user_id] = datetime.now()
        
        # Send connection established message
        await self.send(text_data=json.dumps(
            self.message_response.connection_established(self.user_id)
        ))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Update presence status (user is now offline)
        if self.user_id in _online_users:
            del _online_users[self.user_id]
        
        # Leave all groups
        for group in self.user_groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        self.user_groups.clear()
    
    async def receive(self, text_data):
        """Handle messages received from WebSocket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("Invalid JSON format", "")
            ))
            return
        
        action = data.get('action')
        request_id = data.get('request_id', '')
        
        if not action:
            await self.send(text_data=json.dumps(
                self.error_response.invalid_action(request_id)
            ))
            return
        
        # Route to appropriate handler with exception handling
        try:
            if action == 'send_message':
                await self.handle_send_message(data, request_id)
            elif action == 'edit_message':
                await self.handle_edit_message(data, request_id)
            elif action == 'delete_message':
                await self.handle_delete_message(data, request_id)
            elif action == 'mark_read':
                await self.handle_mark_read(data, request_id)
            elif action == 'join_conversation':
                await self.handle_join_conversation(data, request_id)
            elif action == 'leave_conversation':
                await self.handle_leave_conversation(data, request_id)
            elif action == 'typing':
                await self.handle_typing(data, request_id)
            elif action == 'pong':
                # Heartbeat response
                pass
            elif action == 'get_presence':
                await self.handle_get_presence(data, request_id)
            else:
                await self.send(text_data=json.dumps(
                    self.error_response.invalid_action(request_id)
                ))
        except Exception as e:
            # Log the error for debugging
            import traceback
            print(f"Error handling action {action}: {e}")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps(
                self.error_response.server_error(request_id)
            ))
    
    async def handle_send_message(self, data: Dict[str, Any], request_id: str):
        """Handle send_message action."""
        try:
            conversation_id = data.get('conversation_id')
            text = data.get('content', '')
            reply_to_id = data.get('parent_message_id')
            shared_post_id = data.get('shared_post_id')
            file_url = data.get('file_url')  # S3 URL from HTTP upload
            file_type = data.get('file_type')  # IMAGE, VIDEO, or AUDIO
            file_size = data.get('file_size')  # File size in bytes
            file_name = data.get('file_name')  # Original filename
            
            if not conversation_id:
                await self.send(text_data=json.dumps(
                    self.error_response.validation_error("conversation_id is required", request_id)
                ))
                return
            
            # Rate limiting (synchronous function, no need for async wrapper)
            is_allowed, remaining = check_rate_limit(
                self.user_id, 'send_message'
            )
            if not is_allowed:
                await self.send(text_data=json.dumps(
                    self.error_response.rate_limit_exceeded(request_id)
                ))
                return
            
            # Send message
            response = await database_sync_to_async(
                self.send_message_interactor.send_message_interactor
            )(
                user_id=self.user_id,
                conversation_id=conversation_id,
                text=text,
                file_url=file_url,
                file_type=file_type,
                file_size=file_size,
                file_name=file_name,
                reply_to_id=reply_to_id,
                shared_post_id=shared_post_id,
                request_id=request_id
            )
            
            # Send acknowledgment
            await self.send(text_data=json.dumps(response))
            
            # If successful, broadcast to conversation group
            if response.get('ok'):
                message_id = response.get('data', {}).get('message_id')
                if message_id:
                    message = await database_sync_to_async(
                        self.storage.get_message_by_id
                    )(message_id)
                    if message:
                        broadcast_data = await database_sync_to_async(
                            self.send_message_interactor.get_message_for_broadcast
                        )(message)
                        
                        # Ensure we're in the conversation group
                        conv_group = f"conversation_{conversation_id}"
                        if conv_group not in self.user_groups:
                            await self.channel_layer.group_add(conv_group, self.channel_name)
                            self.user_groups.add(conv_group)
                        
                        # Broadcast to conversation group (excluding sender)
                        await self.channel_layer.group_send(
                            conv_group,
                            {
                                'type': 'message_sent',
                                'data': broadcast_data
                            }
                        )
        except Exception as e:
            import traceback
            print(f"Error in handle_send_message: {e}")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps(
                self.error_response.server_error(request_id)
            ))
    
    async def handle_edit_message(self, data: Dict[str, Any], request_id: str):
        """Handle edit_message action."""
        message_id = data.get('message_id')
        text = data.get('content', '')
        
        if not message_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("message_id is required", request_id)
            ))
            return
        
        # Edit message
        response = await database_sync_to_async(
            self.edit_message_interactor.edit_message_interactor
        )(
            user_id=self.user_id,
            message_id=message_id,
            text=text,
            request_id=request_id
        )
        
        # Send acknowledgment
        await self.send(text_data=json.dumps(response))
        
        # If successful, broadcast to conversation group
        if response.get('ok'):
            message = await database_sync_to_async(
                self.storage.get_message_by_id
            )(message_id)
            if message:
                broadcast_data = await database_sync_to_async(
                    self.edit_message_interactor.get_message_for_broadcast
                )(message)
                
                conv_group = f"conversation_{message.conversation_id}"
                await self.channel_layer.group_send(
                    conv_group,
                    {
                        'type': 'message_edited',
                        'data': broadcast_data
                    }
                )
    
    async def handle_delete_message(self, data: Dict[str, Any], request_id: str):
        """Handle delete_message action."""
        message_id = data.get('message_id')
        
        if not message_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("message_id is required", request_id)
            ))
            return
        
        # Get message before deletion to get conversation_id
        message = await database_sync_to_async(
            self.storage.get_message_by_id
        )(message_id)
        
        if not message:
            await self.send(text_data=json.dumps(
                self.error_response.message_not_found(request_id)
            ))
            return
        
        conversation_id = str(message.conversation_id)
        
        # Delete message
        response = await database_sync_to_async(
            self.delete_message_interactor.delete_message_interactor
        )(
            user_id=self.user_id,
            message_id=message_id,
            request_id=request_id
        )
        
        # Send acknowledgment
        await self.send(text_data=json.dumps(response))
        
        # If successful, broadcast to conversation group
        if response.get('ok'):
            broadcast_data = await database_sync_to_async(
                self.delete_message_interactor.get_delete_broadcast
            )(message_id, conversation_id)
            
            conv_group = f"conversation_{conversation_id}"
            await self.channel_layer.group_send(
                conv_group,
                {
                    'type': 'message_deleted',
                    'data': broadcast_data
                }
            )
    
    async def handle_mark_read(self, data: Dict[str, Any], request_id: str):
        """Handle mark_read action."""
        conversation_id = data.get('conversation_id')
        message_id = data.get('message_id')
        
        if not conversation_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("conversation_id is required", request_id)
            ))
            return
        
        # Mark as read
        response = await database_sync_to_async(
            self.mark_read_interactor.mark_read_interactor
        )(
            user_id=self.user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            request_id=request_id
        )
        
        # Send acknowledgment
        await self.send(text_data=json.dumps(response))
        
        # If successful, broadcast to conversation group
        if response.get('ok'):
            from datetime import datetime
            last_read_at = datetime.now().isoformat()
            broadcast_data = await database_sync_to_async(
                self.mark_read_interactor.get_read_receipt_broadcast
            )(self.user_id, conversation_id, last_read_at)
            
            conv_group = f"conversation_{conversation_id}"
            await self.channel_layer.group_send(
                conv_group,
                {
                    'type': 'read_receipt_updated',
                    'data': broadcast_data
                }
            )
    
    async def handle_join_conversation(self, data: Dict[str, Any], request_id: str):
        """Handle join_conversation action."""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("conversation_id is required", request_id)
            ))
            return
        
        # Check if user is a member
        is_member = await database_sync_to_async(
            self.storage.check_user_membership
        )(self.user_id, conversation_id)
        
        if not is_member:
            await self.send(text_data=json.dumps(
                self.error_response.not_member(request_id)
            ))
            return
        
        # Join conversation group
        conv_group = f"conversation_{conversation_id}"
        await self.channel_layer.group_add(conv_group, self.channel_name)
        self.user_groups.add(conv_group)
        
        # Get conversation for response
        conversation = await database_sync_to_async(
            self.storage.get_conversation_by_id
        )(conversation_id)
        
        if conversation:
            response = self.message_response.conversation_joined(conversation)
            response['request_id'] = request_id
            await self.send(text_data=json.dumps(response))
    
    async def handle_leave_conversation(self, data: Dict[str, Any], request_id: str):
        """Handle leave_conversation action."""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("conversation_id is required", request_id)
            ))
            return
        
        # Leave conversation group
        conv_group = f"conversation_{conversation_id}"
        await self.channel_layer.group_discard(conv_group, self.channel_name)
        self.user_groups.discard(conv_group)
        
        response = self.message_response.conversation_left(conversation_id)
        response['request_id'] = request_id
        await self.send(text_data=json.dumps(response))
    
    async def handle_typing(self, data: Dict[str, Any], request_id: str):
        """Handle typing indicator."""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', True)
        
        if not conversation_id:
            return
        
        # Check if user is a member
        is_member = await database_sync_to_async(
            self.storage.check_user_membership
        )(self.user_id, conversation_id)
        
        if not is_member:
            return
        
        # Broadcast typing indicator
        typing_data = self.message_response.typing_indicator(
            self.user_id,
            self.user.user_name,
            conversation_id,
            is_typing
        )
        
        conv_group = f"conversation_{conversation_id}"
        await self.channel_layer.group_send(
            conv_group,
            {
                'type': 'typing_indicator',
                'data': typing_data
            }
        )
    
    # Handler methods for group messages
    async def message_sent(self, event):
        """Handle message_sent event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def message_edited(self, event):
        """Handle message_edited event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def message_deleted(self, event):
        """Handle message_deleted event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def read_receipt_updated(self, event):
        """Handle read_receipt_updated event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def typing_indicator(self, event):
        """Handle typing_indicator event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def handle_get_presence(self, data: Dict[str, Any], request_id: str):
        """Handle get_presence action."""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("conversation_id is required", request_id)
            ))
            return
        
        # Check if user is a member
        is_member = await database_sync_to_async(
            self.storage.check_user_membership
        )(self.user_id, conversation_id)
        
        if not is_member:
            await self.send(text_data=json.dumps(
                self.error_response.not_member(request_id)
            ))
            return
        
        # Get conversation members
        members = await database_sync_to_async(
            self.storage.get_conversation_members
        )(conversation_id)
        
        # Build presence status for each member
        presence_data = []
        for member in members:
            member_id = str(member.user_id)
            is_online = member_id in _online_users
            presence_data.append({
                "user_id": member_id,
                "user_name": member.user_name,
                "is_online": is_online,
                "last_seen": _online_users[member_id].isoformat() if is_online else None
            })
        
        # Send presence status
        response = {
            "type": "presence.status",
            "request_id": request_id,
            "data": {
                "conversation_id": conversation_id,
                "users": presence_data
            }
        }
        await self.send(text_data=json.dumps(response))


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Legacy per-conversation WebSocket consumer.
    
    One connection per conversation. Simpler but less efficient.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.conversation_id = None
        self.storage = ChatDB()
        self.message_response = MessageResponse()
        self.error_response = ChatErrorResponse()
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4008)
            return
        
        self.user_id = str(self.user.user_id)
        
        # Check if user is a member
        is_member = await database_sync_to_async(
            self.storage.check_user_membership
        )(self.user_id, self.conversation_id)
        
        if not is_member:
            await self.close(code=4003)  # Forbidden
            return
        
        # Join conversation group
        self.conversation_group = f"conversation_{self.conversation_id}"
        await self.channel_layer.group_add(self.conversation_group, self.channel_name)
        
        # Accept connection
        await self.accept()
        
        # Send connection established message
        await self.send(text_data=json.dumps(
            self.message_response.connection_established(self.user_id)
        ))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'conversation_group'):
            await self.channel_layer.group_discard(self.conversation_group, self.channel_name)
    
    async def receive(self, text_data):
        """Handle messages received from WebSocket."""
        # Similar to UserChatConsumer but simpler since we know the conversation
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps(
                self.error_response.validation_error("Invalid JSON format")
            ))
            return
        
        # For simplicity, delegate to UserChatConsumer logic
        # In production, you might want to implement a shared handler
        await self.send(text_data=json.dumps({
            "type": "error",
            "error": "Use /ws/user/ endpoint for full functionality",
            "error_code": "USE_USER_ENDPOINT"
        }))
    
    async def message_sent(self, event):
        """Handle message_sent event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def message_edited(self, event):
        """Handle message_edited event from group."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def message_deleted(self, event):
        """Handle message_deleted event from group."""
        await self.send(text_data=json.dumps(event['data']))

