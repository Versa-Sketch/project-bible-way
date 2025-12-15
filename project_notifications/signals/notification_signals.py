"""
Signal handlers for creating notifications automatically.

Notifications are created when:
- User follows another user
- User likes a post/comment/prayer request/verse
- User sends a message
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from bible_way.models import UserFollowers, Reaction
from project_chat.models import Message
from project_notifications.storage import NotificationDB
from project_notifications.utils.broadcast import broadcast_notification


@receiver(post_save, sender=UserFollowers)
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when user follows another user."""
    if not created:  # Only on new follow
        return
    
    # Skip if user follows themselves
    follower_id = str(instance.follower_id.user_id)
    followed_id = str(instance.followed_id.user_id)
    
    if follower_id == followed_id:
        return
    
    try:
        notification = NotificationDB().create_notification(
            recipient_id=followed_id,
            notification_type='FOLLOW',
            actor_id=follower_id,
            target_id=followed_id,
            target_type='user'
        )
        if notification:
            broadcast_notification(notification)
    except Exception as e:
        # Log error but don't break the follow operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating follow notification: {e}")


@receiver(post_save, sender=Reaction)
def create_like_notification(sender, instance, created, **kwargs):
    """Create or update notification when user likes content."""
    if not created:  # Only on new reaction
        return
    
    actor_id = str(instance.user.user_id)
    notification_type = None
    recipient_id = None
    target_id = None
    target_type = None
    
    # Determine notification type and recipient based on what was liked
    if instance.post:
        # Someone liked a post
        recipient_id = str(instance.post.user.user_id)
        target_id = str(instance.post.post_id)
        target_type = 'post'
        notification_type = 'POST_LIKE'
    elif instance.comment:
        # Someone liked a comment
        recipient_id = str(instance.comment.user.user_id)
        target_id = str(instance.comment.comment_id)
        target_type = 'comment'
        notification_type = 'COMMENT_LIKE'
    elif instance.prayer_request:
        # Someone liked a prayer request
        recipient_id = str(instance.prayer_request.user.user_id)
        target_id = str(instance.prayer_request.prayer_request_id)
        target_type = 'prayer_request'
        notification_type = 'PRAYER_REQUEST_LIKE'
    elif instance.verse:
        # Someone liked a verse (verse doesn't have an owner, skip)
        # Verse likes don't create notifications as verses are not user-owned
        return
    
    # Skip if user likes their own content
    if recipient_id and actor_id == recipient_id:
        return
    
    if not notification_type or not recipient_id:
        return
    
    try:
        # Check if notification exists for aggregation
        notification = NotificationDB().get_or_create_aggregated_notification(
            recipient_id=recipient_id,
            notification_type=notification_type,
            target_id=target_id,
            target_type=target_type
        )
        
        if notification:
            # Update existing notification with new actor
            updated_notification = NotificationDB().update_aggregated_notification(
                notification=notification,
                actor_id=actor_id
            )
            if updated_notification:
                broadcast_notification(updated_notification)
        else:
            # Create new notification
            new_notification = NotificationDB().create_notification(
                recipient_id=recipient_id,
                notification_type=notification_type,
                actor_id=actor_id,
                target_id=target_id,
                target_type=target_type
            )
            if new_notification:
                broadcast_notification(new_notification)
    except Exception as e:
        # Log error but don't break the like operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating like notification: {e}")


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create notification when user sends a message."""
    if not created:  # Only on new message
        return
    
    # Skip if message is deleted or sender is sending to themselves
    if instance.is_deleted_for_everyone:
        return
    
    sender_id = str(instance.sender.user_id)
    conversation_id = str(instance.conversation_id)
    
    try:
        notification_db = NotificationDB()
        
        # Get conversation members
        members = notification_db.get_conversation_members(conversation_id)
        
        for member in members:
            member_id = str(member.user.user_id)
            
            # Skip sender
            if member_id == sender_id:
                continue
            
            # Skip if user has left the conversation
            if member.left_at:
                continue
            
            # Create notification for each member
            notification = notification_db.create_notification(
                recipient_id=member_id,
                notification_type='NEW_MESSAGE',
                actor_id=sender_id,
                target_id=conversation_id,
                target_type='conversation',
                conversation_id=instance.conversation_id,
                message_id=instance.id
            )
            
            if notification:
                broadcast_notification(notification)
    except Exception as e:
        # Log error but don't break the message operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating message notification: {e}")
