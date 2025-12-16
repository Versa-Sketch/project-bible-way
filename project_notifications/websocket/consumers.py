"""
WebSocket consumer for real-time notifications.

Handles WebSocket connections for notifications and delivers notifications
to connected clients in real-time.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


def _normalize_user_id(user_id) -> str:
    """
    Normalize user_id to a consistent string format for dictionary lookups.
    
    Args:
        user_id: User ID in any format (UUID, string, etc.)
    
    Returns:
        Lowercase, stripped string representation of the user_id
    """
    return str(user_id).lower().strip()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user notifications.
    
    Each user connects to receive their notifications in real-time.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.notification_group = None
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope.get('user')
        
        # Check if user exists and is not None (middleware validates token)
        if not self.user:
            logger.warning("Notification WebSocket connection rejected: User not authenticated")
            await self.close(code=4008)  # Policy violation - authentication required
            return
        
        self.user_id = _normalize_user_id(self.user.user_id)
        
        # Join user's personal notification group
        self.notification_group = f"user_{self.user_id}_notifications"
        await self.channel_layer.group_add(self.notification_group, self.channel_name)
        
        # Accept connection
        await self.accept()
        
        # Send connection established message
        await self.send(text_data=json.dumps({
            'type': 'connection.established',
            'message': 'Notification connection established',
            'user_id': str(self.user.user_id)
        }))
        
        logger.info(f"User {self.user_id} connected to notifications WebSocket")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.notification_group:
            await self.channel_layer.group_discard(self.notification_group, self.channel_name)
        
        if self.user_id:
            logger.info(f"User {self.user_id} disconnected from notifications WebSocket")
    
    async def receive(self, text_data):
        """Handle messages received from WebSocket."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': 'Invalid JSON format',
                'error_code': 'VALIDATION_ERROR'
            }))
            return
        
        action = data.get('action')
        request_id = data.get('request_id', '')
        
        if action == 'ping':
            # Heartbeat response
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'request_id': request_id
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': f'Unknown action: {action}',
                'error_code': 'INVALID_ACTION',
                'request_id': request_id
            }))
    
    async def notification_sent(self, event):
        """Handle notification_sent event from group."""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps(event['data']))

