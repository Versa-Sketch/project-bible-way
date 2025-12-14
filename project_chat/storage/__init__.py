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
        """Get a conversation by ID."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            return Conversation.objects.get(id=conv_id, is_active=True)
        except (Conversation.DoesNotExist, ValueError, TypeError):
            return None
    
    def get_conversation_members(self, conversation_id: str) -> List[ConversationMember]:
        """Get all active members of a conversation."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            return list(ConversationMember.objects.filter(
                conversation_id=conv_id,
                left_at__isnull=True
            ).select_related('user'))
        except (ValueError, TypeError):
            return []
    
    def check_user_membership(self, user_id: str, conversation_id: str) -> bool:
        """Check if user is a member of the conversation."""
        try:
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            sender_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            return ConversationMember.objects.filter(
                conversation_id=conv_id,
                user_id=sender_uuid,
                left_at__isnull=True
            ).exists()
        except (ValueError, TypeError):
            return False
    
    def get_message_by_id(self, message_id: str, conversation_id: str = None) -> Optional[Message]:
        """Get a message by ID, optionally filtered by conversation."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            query = Message.objects.filter(id=msg_id)
            if conversation_id:
                conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
                query = query.filter(conversation_id=conv_id)
            return query.first()
        except (ValueError, TypeError, Message.DoesNotExist):
            return None
    
    def create_message(
        self,
        conversation_id: str,
        sender_id: str,
        text: str = "",
        file_url: Optional[str] = None,  # S3 URL
        file_type: Optional[str] = None,
        file_size: Optional[int] = None,
        file_name: Optional[str] = None,
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
                file=file_url,
                file_type=file_type,
                file_size=file_size,
                file_name=file_name
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
            print(f"Unexpected error in create_message: {e}")
            print(traceback.format_exc())
            return None
    
    def update_message_text(self, message_id: str, new_text: str) -> Optional[Message]:
        """Update message text."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            message = Message.objects.get(id=msg_id)
            message.text = new_text
            message.edited_at = datetime.now()
            message.save()
            return message
        except (Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def delete_message(self, message_id: str) -> bool:
        """Soft delete a message (mark as deleted for everyone)."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            message = Message.objects.get(id=msg_id)
            message.is_deleted_for_everyone = True
            message.text = ""  # Clear text
            message.save()
            return True
        except (Message.DoesNotExist, ValueError, TypeError):
            return False
    
    def mark_message_as_read(self, user_id: str, message_id: str, conversation_id: str) -> bool:
        """Mark a message as read for a user."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            conv_id = int(conversation_id) if isinstance(conversation_id, str) else conversation_id
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            message = Message.objects.get(id=msg_id, conversation_id=conv_id)
            user = User.objects.get(user_id=user_uuid)
            
            # Create or update read receipt
            receipt, created = MessageReadReceipt.objects.get_or_create(
                message=message,
                user=user,
                defaults={'read_at': datetime.now()}
            )
            if not created:
                receipt.read_at = datetime.now()
                receipt.save()
            
            # Update conversation member's last_read_at
            member = ConversationMember.objects.filter(
                conversation_id=conv_id,
                user_id=user_uuid,
                left_at__isnull=True
            ).first()
            if member:
                member.last_read_at = datetime.now()
                member.save()
            
            return True
        except (Message.DoesNotExist, User.DoesNotExist, ValueError, TypeError):
            return False
    
    def get_or_create_direct_conversation(self, user1_id: str, user2_id: str) -> Optional[Conversation]:
        """Get or create a direct conversation between two users."""
        try:
            user1_uuid = uuid.UUID(user1_id) if isinstance(user1_id, str) else user1_id
            user2_uuid = uuid.UUID(user2_id) if isinstance(user2_id, str) else user2_id
            
            # Find existing direct conversation
            conversation = self.find_conversation_between_users(user1_id, user2_id)
            
            if conversation:
                # Reactivate if inactive
                if not conversation.is_active:
                    conversation.is_active = True
                    conversation.save()
                return conversation
            
            # Create new conversation
            user1 = User.objects.get(user_id=user1_uuid)
            conversation = Conversation.objects.create(
                type=ConversationTypeChoices.DIRECT,
                created_by=user1,
                is_active=True
            )
            
            # Add both users as members
            ConversationMember.objects.create(
                conversation=conversation,
                user=user1
            )
            ConversationMember.objects.create(
                conversation=conversation,
                user=User.objects.get(user_id=user2_uuid)
            )
            
            return conversation
        except (User.DoesNotExist, ValueError, TypeError) as e:
            import traceback
            print(f"Error in get_or_create_direct_conversation: {e}")
            print(traceback.format_exc())
            return None
    
    def find_conversation_between_users(self, user1_id: str, user2_id: str) -> Optional[Conversation]:
        """Find a direct conversation between two users."""
        try:
            user1_uuid = uuid.UUID(user1_id) if isinstance(user1_id, str) else user1_id
            user2_uuid = uuid.UUID(user2_id) if isinstance(user2_id, str) else user2_id
            
            # Find conversations where both users are members
            conversations = Conversation.objects.filter(
                type=ConversationTypeChoices.DIRECT,
                memberships__user_id=user1_uuid,
                memberships__left_at__isnull=True
            ).filter(
                memberships__user_id=user2_uuid,
                memberships__left_at__isnull=True
            ).distinct()
            
            return conversations.first()
        except (ValueError, TypeError):
            return None
    
    def deactivate_conversation(self, conversation_id: int) -> bool:
        """Deactivate a conversation (used when user unfollows)."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.is_active = False
            conversation.save()
            return True
        except Conversation.DoesNotExist:
            return False
    
    def check_follow_relationship(self, sender_id: str, receiver_id: str) -> bool:
        """Check if sender follows receiver (one-way follow check)."""
        try:
            from bible_way.models import Follow
            sender_uuid = uuid.UUID(sender_id) if isinstance(sender_id, str) else sender_id
            receiver_uuid = uuid.UUID(receiver_id) if isinstance(receiver_id, str) else receiver_id
            
            return Follow.objects.filter(
                follower_id=sender_uuid,
                following_id=receiver_uuid,
                is_active=True
            ).exists()
        except (ValueError, TypeError):
            return False
