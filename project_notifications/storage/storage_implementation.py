import logging
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
import uuid
from project_notifications.models import Notification, NotificationFetchTracker

logger = logging.getLogger(__name__)


class NotificationDB:
    
    def create_notification(
        self,
        notification_type: str,
        target_id: str,
        target_type: str,
        actor_id: str,
        recipient_id: str,
        metadata: dict = None,
        conversation_id: int = None,
        message_id: int = None
    ) -> Notification:
        """Create a new notification."""
        try:
            actor_uuid = uuid.UUID(actor_id) if isinstance(actor_id, str) else actor_id
            recipient_uuid = uuid.UUID(recipient_id) if isinstance(recipient_id, str) else recipient_id
            
            from bible_way.models import User
            try:
                actor = User.objects.get(user_id=actor_uuid)
            except User.DoesNotExist:
                logger.error(f"Failed to create notification: Actor user not found: {actor_id}")
                raise ValueError(f"Actor user not found: {actor_id}")
            
            try:
                recipient = User.objects.get(user_id=recipient_uuid)
            except User.DoesNotExist:
                logger.error(f"Failed to create notification: Recipient user not found: {recipient_id}")
                raise ValueError(f"Recipient user not found: {recipient_id}")
            
            notification = Notification.objects.create(
                notification_type=notification_type,
                target_id=target_id,
                target_type=target_type,
                actor=actor,
                recipient=recipient,
                metadata=metadata or {},
                conversation_id=conversation_id,
                message_id=message_id
            )
            logger.debug(
                f"Notification created: type={notification_type}, target={target_id}, "
                f"actor={actor_id}, recipient={recipient_id}"
            )
            return notification
        except (ValueError, Exception) as e:
            logger.error(
                f"Failed to create notification: type={notification_type}, target={target_id}, "
                f"actor={actor_id}, recipient={recipient_id}, error={str(e)}",
                exc_info=True
            )
            raise
    
    def get_or_create_aggregated_notification(
        self,
        notification_type: str,
        target_id: str,
        target_type: str,
        actor_id: str,
        recipient_id: str,
        aggregation_window_hours: int = 24
    ) -> tuple[Notification, bool]:
        """
        Get existing notification for aggregation or create new one.
        
        Returns:
            tuple: (notification, created) - created is True if new notification was created
        """
        recipient_uuid = uuid.UUID(recipient_id) if isinstance(recipient_id, str) else recipient_id
        
        # Check for existing notification within aggregation window
        cutoff_time = timezone.now() - timedelta(hours=aggregation_window_hours)
        
        existing = Notification.objects.filter(
            notification_type=notification_type,
            target_id=target_id,
            target_type=target_type,
            recipient__user_id=recipient_uuid,
            created_at__gte=cutoff_time
        ).order_by('-created_at').first()
        
        if existing:
            return existing, False
        
        # Create new notification
        notification = self.create_notification(
            notification_type=notification_type,
            target_id=target_id,
            target_type=target_type,
            actor_id=actor_id,
            recipient_id=recipient_id,
            metadata={}
        )
        return notification, True
    
    def update_notification_metadata(
        self,
        notification: Notification,
        actor_id: str,
        actor_name: str
    ) -> Notification:
        """Update notification metadata with aggregation data."""
        try:
            metadata = notification.metadata or {}
            
            # Initialize if needed
            if 'actors' not in metadata:
                metadata['actors'] = []
            if 'actors_count' not in metadata:
                metadata['actors_count'] = 0
            
            # Add actor if not already in list
            actor_uuid = str(uuid.UUID(actor_id) if isinstance(actor_id, str) else actor_id)
            if actor_uuid not in metadata['actors']:
                metadata['actors'].append(actor_uuid)
                metadata['actors_count'] = len(metadata['actors'])
            
            # Update last actor info
            metadata['last_actor_id'] = actor_uuid
            metadata['last_actor_name'] = actor_name
            
            notification.metadata = metadata
            notification.save()
            logger.debug(
                f"Notification metadata updated: notification_id={notification.notification_id}, "
                f"actors_count={metadata['actors_count']}"
            )
            return notification
        except Exception as e:
            logger.error(
                f"Failed to update notification metadata: notification_id={getattr(notification, 'notification_id', 'unknown')}, "
                f"actor_id={actor_id}, error={str(e)}",
                exc_info=True
            )
            raise
    
    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """Get notifications for a user (for future use)."""
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        notifications = Notification.objects.filter(
            recipient__user_id=user_uuid
        ).select_related('actor').order_by('-created_at')[offset:offset + limit]
        
        return list(notifications)
    
    def mark_notification_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Mark notification as read (for future use)."""
        notification_uuid = uuid.UUID(notification_id) if isinstance(notification_id, str) else notification_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            notification = Notification.objects.get(
                notification_id=notification_uuid,
                recipient__user_id=user_uuid
            )
            # Note: is_read field was removed in migration 0002
            # This method is kept for future use if read tracking is re-added
            return True
        except Notification.DoesNotExist:
            return False

