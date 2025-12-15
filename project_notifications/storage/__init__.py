"""
Storage layer for notification-related database operations.

Follows the existing storage pattern for database interactions.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from django.db.models import Q
from project_notifications.models import Notification, NotificationFetchTracker, NotificationTypeChoices
from bible_way.models import User
from project_chat.models import ConversationMember
from django.utils import timezone


class NotificationDB:
    """Database operations for notification functionality."""
    
    def create_notification(
        self,
        recipient_id: str,
        notification_type: str,
        actor_id: str,
        target_id: str,
        target_type: str,
        conversation_id: Optional[int] = None,
        message_id: Optional[int] = None
    ) -> Optional[Notification]:
        """Create a new notification."""
        try:
            recipient_uuid = uuid.UUID(recipient_id) if isinstance(recipient_id, str) else recipient_id
            actor_uuid = uuid.UUID(actor_id) if isinstance(actor_id, str) else actor_id
            
            recipient = User.objects.get(user_id=recipient_uuid)
            actor = User.objects.get(user_id=actor_uuid)
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type=notification_type,
                actor=actor,
                target_id=target_id,
                target_type=target_type,
                conversation_id=conversation_id,
                message_id=message_id,
                metadata={
                    'actors_count': 1,
                    'actors': [actor_id],
                    'last_actor_id': actor_id
                }
            )
            return notification
        except (User.DoesNotExist, ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating notification: {e}")
            return None
    
    def get_user_notifications(
        self,
        user_id: str,
        last_fetch_time: Optional[datetime] = None
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user based on last fetch time."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            query = Notification.objects.filter(recipient__user_id=user_uuid)
            
            # If last_fetch_time is provided, return only notifications created after it
            if last_fetch_time:
                query = query.filter(created_at__gt=last_fetch_time)
            # If None, return all notifications (first call)
            
            notifications = query.select_related('recipient', 'actor').order_by('-created_at')
            total_count = notifications.count()
            
            return list(notifications), total_count
        except (ValueError, TypeError):
            return [], 0
    
    def get_or_create_fetch_tracker(self, user_id: str) -> Optional[NotificationFetchTracker]:
        """Get or create NotificationFetchTracker for a user."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            user = User.objects.get(user_id=user_uuid)
            
            tracker, created = NotificationFetchTracker.objects.get_or_create(
                user=user,
                defaults={'last_fetch_at': None}
            )
            return tracker
        except (User.DoesNotExist, ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting/creating fetch tracker: {e}")
            return None
    
    def update_fetch_tracker(self, user_id: str, fetch_time: datetime) -> bool:
        """Update the last_fetch_at timestamp for a user."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            user = User.objects.get(user_id=user_uuid)
            
            tracker = NotificationFetchTracker.objects.get(user=user)
            tracker.last_fetch_at = fetch_time
            tracker.save()
            return True
        except (User.DoesNotExist, NotificationFetchTracker.DoesNotExist, ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating fetch tracker: {e}")
            return False
    
    def get_or_create_aggregated_notification(
        self,
        recipient_id: str,
        notification_type: str,
        target_id: str,
        target_type: str
    ) -> Optional[Notification]:
        """Get existing notification for aggregation, or return None if not exists."""
        try:
            user_uuid = uuid.UUID(recipient_id) if isinstance(recipient_id, str) else recipient_id
            
            # Only aggregate like notifications
            if notification_type not in ['POST_LIKE', 'COMMENT_LIKE', 'PRAYER_REQUEST_LIKE']:
                return None
            
            notification = Notification.objects.filter(
                recipient__user_id=user_uuid,
                notification_type=notification_type,
                target_id=target_id,
                target_type=target_type
            ).first()
            
            return notification
        except (ValueError, TypeError):
            return None
    
    def update_aggregated_notification(
        self,
        notification: Notification,
        actor_id: str
    ) -> Optional[Notification]:
        """Update an aggregated notification with a new actor."""
        try:
            actor_uuid = uuid.UUID(actor_id) if isinstance(actor_id, str) else actor_id
            actor = User.objects.get(user_id=actor_uuid)
            
            metadata = notification.metadata or {}
            actors = metadata.get('actors', [])
            
            # Add actor if not already in list
            if actor_id not in actors:
                actors.append(actor_id)
            
            # Update metadata
            metadata['actors_count'] = len(actors)
            metadata['actors'] = actors
            metadata['last_actor_id'] = actor_id
            
            notification.metadata = metadata
            notification.actor = actor  # Update to latest actor
            notification.save()
            
            return notification
        except (User.DoesNotExist, ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating aggregated notification: {e}")
            return None
    
    def get_conversation_members(self, conversation_id: str) -> List[ConversationMember]:
        """Get all active members of a conversation (helper for message notifications)."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            return list(ConversationMember.objects.filter(
                conversation_id=conv_id,
                left_at__isnull=True
            ).select_related('user'))
        except (ValueError, TypeError):
            return []
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification (for cleanup)."""
        try:
            notif_uuid = uuid.UUID(notification_id) if isinstance(notification_id, str) else notification_id
            Notification.objects.filter(notification_id=notif_uuid).delete()
            return True
        except (ValueError, TypeError):
            return False
