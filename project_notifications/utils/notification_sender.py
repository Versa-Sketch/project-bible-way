from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from project_notifications.models import Notification
from project_notifications.presenters import NotificationResponse


def _normalize_user_id(user_id) -> str:
    """
    Normalize user_id to a consistent string format for dictionary lookups.
    
    Args:
        user_id: User ID in any format (UUID, string, etc.)
    
    Returns:
        Lowercase, stripped string representation of the user_id
    """
    return str(user_id).lower().strip()


def send_notification_via_websocket(notification: Notification):
    """
    Send notification to user via WebSocket using channel layer.
    
    Args:
        notification: Notification instance to send
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    
    recipient_id = _normalize_user_id(notification.recipient.user_id)
    group_name = f"user_{recipient_id}_notifications"
    
    # Format notification
    presenter = NotificationResponse()
    metadata = notification.metadata or {}
    
    # Check if aggregated
    if metadata.get('actors_count', 1) > 1:
        notification_data = presenter.format_aggregated_notification(notification)
    else:
        notification_data = presenter.format_notification(notification)
    
    # Send to user's notification group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_sent',
            'data': notification_data
        }
    )

