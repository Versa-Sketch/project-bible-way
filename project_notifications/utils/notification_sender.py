import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from project_notifications.models import Notification
from project_notifications.presenters import NotificationResponse

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


def send_notification_via_websocket(notification: Notification):
    """
    Send notification to user via WebSocket using channel layer.
    
    Args:
        notification: Notification instance to send
    """
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning(
                f"Channel layer not available, notification not sent: "
                f"notification_id={notification.notification_id}, recipient={notification.recipient.user_id}"
            )
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
        ws_msg = (
            f"📤 WebSocket message sent to group '{group_name}': notification_id={notification.notification_id}, "
            f"type={notification.notification_type}, recipient={recipient_id[:8]}..."
        )
        print(ws_msg)
        logger.info(ws_msg)
    except Exception as e:
        logger.error(
            f"Failed to send notification via WebSocket: notification_id={getattr(notification, 'notification_id', 'unknown')}, "
            f"recipient={getattr(notification.recipient, 'user_id', 'unknown')}, error={str(e)}",
            exc_info=True
        )
        # Don't raise - notification sending failure shouldn't break the main action

