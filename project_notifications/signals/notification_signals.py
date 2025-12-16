import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from bible_way.models import UserFollowers, Reaction, Comment, PrayerRequest
from project_notifications.storage import NotificationDB
from project_notifications.models import NotificationTypeChoices
from project_notifications.utils import send_notification_via_websocket

logger = logging.getLogger(__name__)
storage = NotificationDB()


@receiver(post_save, sender=UserFollowers)
def handle_follow_signal(sender, instance, created, **kwargs):
    """Handle follow notification."""
    if not created:
        return
    
    try:
        follower_id = str(instance.follower_id.user_id)
        followed_id = str(instance.followed_id.user_id)
        
        # Don't notify self
        if follower_id == followed_id:
            return
        
        # Create notification (follows are not aggregated)
        notification = storage.create_notification(
            notification_type=NotificationTypeChoices.FOLLOW,
            target_id=followed_id,
            target_type='user',
            actor_id=follower_id,
            recipient_id=followed_id
        )
        
        # Send via WebSocket
        send_notification_via_websocket(notification)
        logger.info(
            f"Follow notification sent: follower={follower_id}, followed={followed_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to send follow notification: follower={getattr(instance.follower_id, 'user_id', 'unknown')}, "
            f"followed={getattr(instance.followed_id, 'user_id', 'unknown')}, error={str(e)}",
            exc_info=True
        )
        # Don't raise - let the follow action succeed even if notification fails


@receiver(post_save, sender=Reaction)
def handle_reaction_signal(sender, instance, created, **kwargs):
    """Handle like notifications for posts, comments, and prayer requests."""
    if not created:
        return
    
    try:
        actor_id = str(instance.user.user_id)
        
        # Handle post like
        if instance.post:
            post = instance.post
            recipient_id = str(post.user.user_id)
            
            # Don't notify self
            if actor_id == recipient_id:
                return
            
            # Get or create aggregated notification
            notification, _ = storage.get_or_create_aggregated_notification(
                notification_type=NotificationTypeChoices.POST_LIKE,
                target_id=str(post.post_id),
                target_type='post',
                actor_id=actor_id,
                recipient_id=recipient_id
            )
            
            # Initialize or update metadata (works for both new and existing)
            storage.update_notification_metadata(
                notification,
                actor_id,
                instance.user.user_name
            )
            
            # Send via WebSocket
            send_notification_via_websocket(notification)
            logger.info(
                f"Post like notification sent: actor={actor_id}, post={post.post_id}, recipient={recipient_id}"
            )
        
        # Handle comment like
        elif instance.comment:
            comment = instance.comment
            recipient_id = str(comment.user.user_id)
            
            # Don't notify self
            if actor_id == recipient_id:
                return
            
            # Get or create aggregated notification
            notification, _ = storage.get_or_create_aggregated_notification(
                notification_type=NotificationTypeChoices.COMMENT_LIKE,
                target_id=str(comment.comment_id),
                target_type='comment',
                actor_id=actor_id,
                recipient_id=recipient_id
            )
            
            # Initialize or update metadata (works for both new and existing)
            storage.update_notification_metadata(
                notification,
                actor_id,
                instance.user.user_name
            )
            
            # Send via WebSocket
            send_notification_via_websocket(notification)
            logger.info(
                f"Comment like notification sent: actor={actor_id}, comment={comment.comment_id}, recipient={recipient_id}"
            )
        
        # Handle prayer request like
        elif instance.prayer_request:
            prayer_request = instance.prayer_request
            recipient_id = str(prayer_request.user.user_id)
            
            # Don't notify self
            if actor_id == recipient_id:
                return
            
            # Get or create aggregated notification
            notification, _ = storage.get_or_create_aggregated_notification(
                notification_type=NotificationTypeChoices.PRAYER_REQUEST_LIKE,
                target_id=str(prayer_request.prayer_request_id),
                target_type='prayer_request',
                actor_id=actor_id,
                recipient_id=recipient_id
            )
            
            # Initialize or update metadata (works for both new and existing)
            storage.update_notification_metadata(
                notification,
                actor_id,
                instance.user.user_name
            )
            
            # Send via WebSocket
            send_notification_via_websocket(notification)
            logger.info(
                f"Prayer request like notification sent: actor={actor_id}, "
                f"prayer_request={prayer_request.prayer_request_id}, recipient={recipient_id}"
            )
    except Exception as e:
        logger.error(
            f"Failed to send reaction notification: actor={getattr(instance.user, 'user_id', 'unknown')}, "
            f"reaction_id={getattr(instance, 'reaction_id', 'unknown')}, error={str(e)}",
            exc_info=True
        )
        # Don't raise - let the reaction action succeed even if notification fails


@receiver(post_save, sender=Comment)
def handle_comment_signal(sender, instance, created, **kwargs):
    """Handle comment notifications for posts and prayer requests."""
    if not created:
        return
    
    try:
        actor_id = str(instance.user.user_id)
        
        # Handle comment on post
        if instance.post:
            post = instance.post
            recipient_id = str(post.user.user_id)
            
            # Don't notify self
            if actor_id == recipient_id:
                return
            
            # Get or create aggregated notification
            notification, _ = storage.get_or_create_aggregated_notification(
                notification_type=NotificationTypeChoices.COMMENT_ON_POST,
                target_id=str(post.post_id),
                target_type='post',
                actor_id=actor_id,
                recipient_id=recipient_id
            )
            
            # Initialize or update metadata (works for both new and existing)
            storage.update_notification_metadata(
                notification,
                actor_id,
                instance.user.user_name
            )
            
            # Send via WebSocket
            send_notification_via_websocket(notification)
            logger.info(
                f"Comment on post notification sent: actor={actor_id}, post={post.post_id}, recipient={recipient_id}"
            )
        
        # Handle comment on prayer request
        elif instance.prayer_request:
            prayer_request = instance.prayer_request
            recipient_id = str(prayer_request.user.user_id)
            
            # Don't notify self
            if actor_id == recipient_id:
                return
            
            # Get or create aggregated notification
            notification, _ = storage.get_or_create_aggregated_notification(
                notification_type=NotificationTypeChoices.COMMENT_ON_PRAYER_REQUEST,
                target_id=str(prayer_request.prayer_request_id),
                target_type='prayer_request',
                actor_id=actor_id,
                recipient_id=recipient_id
            )
            
            # Initialize or update metadata (works for both new and existing)
            storage.update_notification_metadata(
                notification,
                actor_id,
                instance.user.user_name
            )
            
            # Send via WebSocket
            send_notification_via_websocket(notification)
            logger.info(
                f"Comment on prayer request notification sent: actor={actor_id}, "
                f"prayer_request={prayer_request.prayer_request_id}, recipient={recipient_id}"
            )
    except Exception as e:
        logger.error(
            f"Failed to send comment notification: actor={getattr(instance.user, 'user_id', 'unknown')}, "
            f"comment_id={getattr(instance, 'comment_id', 'unknown')}, error={str(e)}",
            exc_info=True
        )
        # Don't raise - let the comment action succeed even if notification fails


@receiver(post_save, sender=PrayerRequest)
def handle_prayer_request_created_signal(sender, instance, created, **kwargs):
    """Handle prayer request created notification (notify followers)."""
    if not created:
        return
    
    try:
        actor_id = str(instance.user.user_id)
        
        # Get all followers
        followers = UserFollowers.objects.filter(followed_id__user_id=actor_id).select_related('follower_id')
        
        # Notify each follower
        notified_count = 0
        for follow in followers:
            try:
                follower_id = str(follow.follower_id.user_id)
                
                # Create notification for each follower (not aggregated)
                notification = storage.create_notification(
                    notification_type=NotificationTypeChoices.PRAYER_REQUEST_CREATED,
                    target_id=str(instance.prayer_request_id),
                    target_type='prayer_request',
                    actor_id=actor_id,
                    recipient_id=follower_id
                )
                
                # Send via WebSocket
                send_notification_via_websocket(notification)
                notified_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to notify follower {getattr(follow.follower_id, 'user_id', 'unknown')} "
                    f"about prayer request {getattr(instance, 'prayer_request_id', 'unknown')}: {str(e)}",
                    exc_info=True
                )
                # Continue with next follower even if one fails
        
        logger.info(
            f"Prayer request created notifications sent: actor={actor_id}, "
            f"prayer_request={instance.prayer_request_id}, notified={notified_count}/{followers.count()}"
        )
    except Exception as e:
        logger.error(
            f"Failed to send prayer request created notifications: "
            f"actor={getattr(instance.user, 'user_id', 'unknown')}, "
            f"prayer_request={getattr(instance, 'prayer_request_id', 'unknown')}, error={str(e)}",
            exc_info=True
        )
        # Don't raise - let the prayer request creation succeed even if notification fails

