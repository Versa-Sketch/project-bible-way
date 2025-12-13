"""
Storage layer for chat-related database operations.

Follows the existing storage pattern for database interactions.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from django.db.models import Q, Max
from project_chat.models import Conversation, ConversationMember, Message, MessageReadReceipt, ConversationTypeChoices
from bible_way.models import User


class ChatDB:
    """Database operations for chat functionality."""
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by its ID."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            return Conversation.objects.get(id=conv_id, is_active=True)
        except (Conversation.DoesNotExist, ValueError, TypeError):
            return None
    
    def check_user_membership(self, user_id: str, conversation_id: str) -> bool:
        """Check if a user is a member of a conversation."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            
            membership = ConversationMember.objects.get(
                user__user_id=user_uuid,
                conversation_id=conv_id,
                left_at__isnull=True  # User hasn't left
            )
            return True
        except (ConversationMember.DoesNotExist, ValueError, TypeError):
            return False
    
    def get_conversation_members(self, conversation_id: str) -> List[User]:
        """Get all active members of a conversation."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            memberships = ConversationMember.objects.filter(
                conversation_id=conv_id,
                left_at__isnull=True
            ).select_related('user')
            return [membership.user for membership in memberships]
        except (ValueError, TypeError, Exception):
            return []
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            memberships = ConversationMember.objects.filter(
                user__user_id=user_uuid,
                left_at__isnull=True
            ).select_related('conversation').filter(conversation__is_active=True)
            return [membership.conversation for membership in memberships]
        except (ValueError, Exception):
            return []
    
    def create_message(
        self,
        conversation_id: str,
        sender_id: str,
        text: str = "",
        file=None,
        reply_to_id: Optional[str] = None,
        shared_post_id: Optional[str] = None
    ) -> Optional[Message]:
        """Create a new message in a conversation."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            sender_uuid = uuid.UUID(sender_id) if isinstance(sender_id, str) else sender_id
            
            conversation = Conversation.objects.get(id=conv_id)
            sender = User.objects.get(user_id=sender_uuid)
            
            message = Message(
                conversation=conversation,
                sender=sender,
                text=text,
                file=file
            )
            
            if shared_post_id:
                from bible_way.models import Post
                post_uuid = uuid.UUID(shared_post_id) if isinstance(shared_post_id, str) else shared_post_id
                try:
                    post = Post.objects.get(post_id=post_uuid)
                    message.shared_post = post
                except Post.DoesNotExist:
                    pass  # Invalid post, ignore
            
            if reply_to_id:
                reply_id = int(reply_to_id) if isinstance(reply_to_id, str) else reply_to_id
                try:
                    reply_message = Message.objects.get(id=reply_id, conversation=conversation)
                    message.reply_to = reply_message
                except Message.DoesNotExist:
                    pass  # Invalid reply_to, ignore
            
            message.save()
            return message
        except (Conversation.DoesNotExist, User.DoesNotExist) as e:
            import traceback
            print(f"Error creating message - object not found: {e}")
            print(traceback.format_exc())
            return None
        except (ValueError, TypeError) as e:
            import traceback
            print(f"Error creating message - invalid type/value: {e}")
            print(traceback.format_exc())
            return None
        except Exception as e:
            import traceback
            print(f"Unexpected error creating message: {e}")
            print(traceback.format_exc())
            return None
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Get a message by its ID."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            return Message.objects.get(id=msg_id)
        except (Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def update_message(self, message_id: str, text: str = None) -> Optional[Message]:
        """Update a message (edit)."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            message = Message.objects.get(id=msg_id)
            
            if text is not None:
                message.text = text
                message.edited_at = datetime.now()
                message.save()
            
            return message
        except (Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def delete_message(self, message_id: str) -> Optional[Message]:
        """Soft delete a message."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            message = Message.objects.get(id=msg_id)
            message.is_deleted_for_everyone = True
            message.save()
            return message
        except (Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation with pagination."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            messages = Message.objects.filter(
                conversation_id=conv_id,
                is_deleted_for_everyone=False
            ).select_related('sender', 'reply_to').order_by('-created_at')[offset:offset + limit]
            return list(messages)
        except (ValueError, TypeError, Exception):
            return []
    
    def update_read_receipt(self, user_id: str, conversation_id: str) -> bool:
        """Update the last_read_at timestamp for a user in a conversation."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            
            membership = ConversationMember.objects.get(
                user__user_id=user_uuid,
                conversation_id=conv_id,
                left_at__isnull=True
            )
            membership.last_read_at = datetime.now()
            membership.save()
            return True
        except (ConversationMember.DoesNotExist, ValueError, TypeError):
            return False
    
    def create_message_read_receipt(self, user_id: str, message_id: str) -> Optional[MessageReadReceipt]:
        """Create a read receipt for a specific message."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            
            user = User.objects.get(user_id=user_uuid)
            message = Message.objects.get(id=msg_id)
            
            # Get or create read receipt
            receipt, created = MessageReadReceipt.objects.get_or_create(
                user=user,
                message=message,
                defaults={'read_at': datetime.now()}
            )
            
            if not created:
                receipt.read_at = datetime.now()
                receipt.save()
            
            return receipt
        except (User.DoesNotExist, Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def get_unread_count(self, user_id: str, conversation_id: str) -> int:
        """Get the count of unread messages for a user in a conversation."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            
            membership = ConversationMember.objects.get(
                user__user_id=user_uuid,
                conversation_id=conv_id,
                left_at__isnull=True
            )
            
            if not membership.last_read_at:
                # If never read, count all messages
                return Message.objects.filter(
                    conversation_id=conv_id,
                    is_deleted_for_everyone=False
                ).exclude(sender__user_id=user_uuid).count()
            
            # Count messages after last_read_at
            return Message.objects.filter(
                conversation_id=conv_id,
                created_at__gt=membership.last_read_at,
                is_deleted_for_everyone=False
            ).exclude(sender__user_id=user_uuid).count()
        except (ConversationMember.DoesNotExist, ValueError, TypeError):
            return 0
    
    def check_message_ownership(self, message_id: str, user_id: str) -> bool:
        """Check if a user owns a message."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            message = Message.objects.get(id=msg_id)
            return str(message.sender.user_id) == str(user_uuid)
        except (Message.DoesNotExist, ValueError, TypeError):
            return False
    
    def get_or_create_direct_conversation(self, user1_id: str, user2_id: str) -> Optional[Conversation]:
        """
        Get or create a direct conversation between two users.
        If conversation exists but is inactive, reactivates it.
        """
        try:
            user1_uuid = uuid.UUID(user1_id) if isinstance(user1_id, str) else user1_id
            user2_uuid = uuid.UUID(user2_id) if isinstance(user2_id, str) else user2_id
            
            user1 = User.objects.get(user_id=user1_uuid)
            user2 = User.objects.get(user_id=user2_uuid)
            
            # Check if conversation already exists between these two users
            existing_memberships = ConversationMember.objects.filter(
                user__user_id__in=[user1_uuid, user2_uuid]
            ).values_list('conversation_id', flat=True).distinct()
            
            # Find conversation that has both users as members
            for conv_id in existing_memberships:
                members = ConversationMember.objects.filter(
                    conversation_id=conv_id,
                    user__user_id__in=[user1_uuid, user2_uuid]
                )
                if members.count() == 2:
                    # Found existing conversation
                    conversation = Conversation.objects.get(id=conv_id)
                    if not conversation.is_active:
                        # Reactivate conversation
                        conversation.is_active = True
                        conversation.save()
                        # Reactivate memberships
                        ConversationMember.objects.filter(conversation=conversation).update(left_at=None)
                    return conversation
            
            # No existing conversation found, create new one
            conversation = Conversation.objects.create(
                type=ConversationTypeChoices.DIRECT,
                created_by=user1,
                is_active=True
            )
            
            # Create memberships for both users
            ConversationMember.objects.create(
                conversation=conversation,
                user=user1,
                joined_at=datetime.now()
            )
            ConversationMember.objects.create(
                conversation=conversation,
                user=user2,
                joined_at=datetime.now()
            )
            
            return conversation
        except (User.DoesNotExist, ValueError, TypeError, Exception):
            return None
    
    def find_conversation_between_users(self, user1_id: str, user2_id: str) -> Optional[Conversation]:
        """Find DIRECT conversation between two specific users."""
        try:
            user1_uuid = uuid.UUID(user1_id) if isinstance(user1_id, str) else user1_id
            user2_uuid = uuid.UUID(user2_id) if isinstance(user2_id, str) else user2_id
            
            # Find conversations where both users are members
            memberships = ConversationMember.objects.filter(
                user__user_id__in=[user1_uuid, user2_uuid]
            ).values_list('conversation_id', flat=True).distinct()
            
            for conv_id in memberships:
                conversation = Conversation.objects.get(id=conv_id, type=ConversationTypeChoices.DIRECT)
                member_count = ConversationMember.objects.filter(
                    conversation=conversation,
                    user__user_id__in=[user1_uuid, user2_uuid]
                ).count()
                
                if member_count == 2:
                    return conversation
            
            return None
        except (Conversation.DoesNotExist, ValueError, TypeError, Exception):
            return None
    
    def deactivate_conversation(self, conversation_id: int) -> bool:
        """Deactivate a conversation and mark all members as left."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.is_active = False
            conversation.save()
            
            # Mark all members as left
            ConversationMember.objects.filter(conversation=conversation).update(
                left_at=datetime.now()
            )
            
            return True
        except (Conversation.DoesNotExist, ValueError, TypeError):
            return False
    
    def check_follow_relationship(self, sender_id: str, receiver_id: str) -> bool:
        """
        Check if sender follows receiver (one-way follow check).
        Returns True if sender follows receiver, False otherwise.
        """
        try:
            from bible_way.storage import UserDB
            user_db = UserDB()
            return user_db.check_follow_exists(sender_id, receiver_id)
        except Exception:
            return False

