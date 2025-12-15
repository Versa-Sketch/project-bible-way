"""
Utility function for broadcasting notifications via WebSocket.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from project_notifications.models import Notification
from typing import Dict, Any


def broadcast_notification(notification: Notification) -> None:
    """
    Broadcast a notification to the recipient via WebSocket.
    
    Args:
        notification: The Notification instance to broadcast
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        
        recipient_id = str(notification.recipient.user_id).lower()
        group_name = f"notification_{recipient_id}"
        
        # Format notification data
        metadata = notification.metadata or {}
        actors_count = metadata.get('actors_count', 1)
        actors = metadata.get('actors', [])
        last_actor_id = metadata.get('last_actor_id', str(notification.actor.user_id) if notification.actor else None)
        
        # Get actor info
        actor_data = None
        if notification.actor:
            actor_data = {
                'user_id': str(notification.actor.user_id),
                'user_name': notification.actor.user_name,
                'profile_picture_url': notification.actor.profile_picture_url or ''
            }
        
        notification_data = {
            'notification_id': str(notification.notification_id),
            'type': notification.notification_type,
            'actor': actor_data,
            'actors_count': actors_count,
            'actors': actors,
            'target_id': notification.target_id,
            'target_type': notification.target_type,
            'conversation_id': notification.conversation_id,
            'message_id': notification.message_id,
            'created_at': notification.created_at.isoformat() if notification.created_at else None,
            'metadata': metadata
        }
        
        # Send to channel layer group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_new',
                'data': {
                    'notification': notification_data
                }
            }
        )
    except Exception as e:
        # Log error but don't break notification creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error broadcasting notification: {e}")
