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
    
    def _safe_convert_conversation_id(self, conversation_id: str):
        """Safely convert conversation_id to int, handling OverflowError for SQLite INTEGER limit."""
        if isinstance(conversation_id, str):
            # Check if it looks like a UUID (has dashes or is 32+ hex chars)
            if '-' in conversation_id or len(conversation_id) > 20:
                raise ValueError(f"conversation_id appears to be a UUID or invalid format: {conversation_id}")
            
            try:
                conv_id = int(conversation_id)
                # SQLite INTEGER max value is 2^63 - 1 (9,223,372,036,854,775,807)
                if conv_id > 9223372036854775807:
                    raise OverflowError(f"conversation_id {conversation_id} exceeds SQLite INTEGER limit")
                if conv_id < 0:
                    raise ValueError(f"conversation_id cannot be negative: {conversation_id}")
                return conv_id
            except ValueError as e:
                # Re-raise with more context
                raise ValueError(f"Invalid conversation_id format (expected integer): {conversation_id}") from e
            except OverflowError:
                # Re-raise with context
                raise OverflowError(f"conversation_id {conversation_id} exceeds SQLite INTEGER limit")
        return conversation_id
    
    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        try:
            conv_id = self._safe_convert_conversation_id(conversation_id)
            return Conversation.objects.get(id=conv_id, is_active=True)
        except (Conversation.DoesNotExist, ValueError, TypeError, OverflowError, Exception) as e:
            # Handle case where table doesn't exist
            error_msg = str(e).lower()
            if "no such table" in error_msg or "does not exist" in error_msg:
                return None
            # Re-raise other exceptions
            raise
    
    def get_conversation_members(self, conversation_id: str) -> List[ConversationMember]:
        """Get all active members of a conversation."""
        try:
            conv_id = self._safe_convert_conversation_id(conversation_id)
            return list(ConversationMember.objects.filter(
                conversation_id=conv_id,
                left_at__isnull=True
            ).select_related('user'))
        except (ValueError, TypeError, OverflowError):
            return []
    
    def check_user_membership(self, user_id: str, conversation_id: str) -> bool:
        """Check if user is a member of the conversation."""
        try:
            conv_id = self._safe_convert_conversation_id(conversation_id)
            sender_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            return ConversationMember.objects.filter(
                conversation_id=conv_id,
                user__user_id=sender_uuid,  # Use user__user_id to access UUIDField through ForeignKey
                left_at__isnull=True
            ).exists()
        except (ValueError, TypeError, OverflowError):
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
    
    def check_message_ownership(self, message_id: str, user_id: str) -> bool:
        """Check if a user owns a message (i.e., is the sender)."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            # Check if message exists and sender matches user_id
            message = Message.objects.filter(
                id=msg_id,
                sender__user_id=user_uuid  # Use sender__user_id to access UUIDField through ForeignKey
            ).first()
            
            return message is not None
        except (ValueError, TypeError, Exception):
            return False
    
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
            conv_id = self._safe_convert_conversation_id(conversation_id)
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
        except (ValueError, TypeError, OverflowError) as e:
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
    
    def delete_message(self, message_id: str) -> Optional[Message]:
        """Soft delete a message (mark as deleted for everyone)."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            message = Message.objects.get(id=msg_id)
            message.is_deleted_for_everyone = True
            message.text = ""  # Clear text
            message.save()
            return message
        except (Message.DoesNotExist, ValueError, TypeError):
            return None
    
    def mark_message_as_read(self, user_id: str, message_id: str, conversation_id: str) -> bool:
        """Mark a message as read for a user."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            conv_id = self._safe_convert_conversation_id(conversation_id)
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
                user__user_id=user_uuid,  # Use user__user_id
                left_at__isnull=True
            ).first()
            if member:
                member.last_read_at = datetime.now()
                member.save()
            
            return True
        except (Message.DoesNotExist, User.DoesNotExist, ValueError, TypeError, OverflowError):
            return False
    
    def create_message_read_receipt(self, user_id: str, message_id: str, conversation_id: str = None) -> Optional[MessageReadReceipt]:
        """Create a read receipt for a specific message."""
        try:
            msg_id = int(message_id) if isinstance(message_id, str) else message_id
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            # Get message, optionally filtered by conversation
            if conversation_id:
                conv_id = self._safe_convert_conversation_id(conversation_id)
                message = Message.objects.get(id=msg_id, conversation_id=conv_id)
            else:
                message = Message.objects.get(id=msg_id)
            
            user = User.objects.get(user_id=user_uuid)
            
            # Create or get read receipt
            receipt, created = MessageReadReceipt.objects.get_or_create(
                message=message,
                user=user,
                defaults={'read_at': datetime.now()}
            )
            if not created:
                receipt.read_at = datetime.now()
                receipt.save()
            
            # Update conversation member's last_read_at if conversation_id provided
            if conversation_id:
                conv_id = self._safe_convert_conversation_id(conversation_id)
                member = ConversationMember.objects.filter(
                    conversation_id=conv_id,
                    user__user_id=user_uuid,
                    left_at__isnull=True
                ).first()
                if member:
                    member.last_read_at = datetime.now()
                    member.save()
            
            return receipt
        except (Message.DoesNotExist, User.DoesNotExist, ValueError, TypeError, OverflowError):
            return None
    
    def update_read_receipt(self, user_id: str, conversation_id: str) -> bool:
        """Update last_read_at for all messages in a conversation."""
        try:
            conv_id = self._safe_convert_conversation_id(conversation_id)
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            # Update conversation member's last_read_at
            member = ConversationMember.objects.filter(
                conversation_id=conv_id,
                user__user_id=user_uuid,  # Use user__user_id
                left_at__isnull=True
            ).first()
            
            if not member:
                return False
            
            # Update last_read_at to now
            member.last_read_at = datetime.now()
            member.save()
            
            # Optionally create read receipts for all unread messages
            unread_messages = Message.objects.filter(
                conversation_id=conv_id,
                is_deleted_for_everyone=False
            ).exclude(sender__user_id=user_uuid).exclude(
                read_receipts__user__user_id=user_uuid
            )
            
            user = User.objects.get(user_id=user_uuid)
            for message in unread_messages:
                MessageReadReceipt.objects.get_or_create(
                    message=message,
                    user=user,
                    defaults={'read_at': datetime.now()}
                )
            
            return True
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
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
        except Exception as e:
            # Handle case where tables don't exist
            error_msg = str(e).lower()
            if "no such table" in error_msg or "does not exist" in error_msg:
                import traceback
                print(f"Error in get_or_create_direct_conversation: Tables don't exist. Run migrations: {e}")
                print(traceback.format_exc())
                return None
            # Re-raise other exceptions
            import traceback
            print(f"Error in get_or_create_direct_conversation: {e}")
            print(traceback.format_exc())
            raise
    
    def find_conversation_between_users(self, user1_id: str, user2_id: str) -> Optional[Conversation]:
        """Find a direct conversation between two users."""
        try:
            user1_uuid = uuid.UUID(user1_id) if isinstance(user1_id, str) else user1_id
            user2_uuid = uuid.UUID(user2_id) if isinstance(user2_id, str) else user2_id
            
            # Find conversations where both users are members
            # Use user__user_id to access the user_id field through the ForeignKey
            conversations = Conversation.objects.filter(
                type=ConversationTypeChoices.DIRECT,
                memberships__user__user_id=user1_uuid,
                memberships__left_at__isnull=True
            ).filter(
                memberships__user__user_id=user2_uuid,
                memberships__left_at__isnull=True
            ).distinct()
            
            return conversations.first()
        except (ValueError, TypeError, Exception) as e:
            # Handle case where table doesn't exist or other database errors
            error_msg = str(e).lower()
            if "no such table" in error_msg or "does not exist" in error_msg:
                return None
            # Re-raise other exceptions
            raise
    
    def deactivate_conversation(self, conversation_id: int) -> bool:
        """Deactivate a conversation (used when user unfollows)."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.is_active = False
            conversation.save()
            return True
        except Conversation.DoesNotExist:
            return False
    
    def ensure_user_membership(self, user_id: str, conversation_id: str) -> bool:
        """Ensure user is a member of the conversation. Adds if not already a member."""
        try:
            # Log the inputs for debugging
            print(f"DEBUG ensure_user_membership: user_id={user_id}, conversation_id={conversation_id} (type: {type(conversation_id)})")
            
            conv_id = self._safe_convert_conversation_id(conversation_id)
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            # Check if already a member
            membership = ConversationMember.objects.filter(
                conversation_id=conv_id,
                user_id=user_uuid,
                left_at__isnull=True
            ).first()
            
            if membership:
                return True  # Already a member
            
            # Add user as member
            conversation = Conversation.objects.get(id=conv_id)
            user = User.objects.get(user_id=user_uuid)
            ConversationMember.objects.create(
                conversation=conversation,
                user=user
            )
            return True
        except (Conversation.DoesNotExist, User.DoesNotExist) as e:
            print(f"Error in ensure_user_membership (object not found): {type(e).__name__}: {e}, conversation_id={conversation_id}, user_id={user_id}")
            return False
        except (ValueError, TypeError, OverflowError) as e:
            print(f"Error in ensure_user_membership (validation error): {type(e).__name__}: {e}, conversation_id={conversation_id}, user_id={user_id}")
            return False
        except Exception as e:
            # Catch any other exceptions including database-level OverflowError
            print(f"Error in ensure_user_membership (unexpected): {type(e).__name__}: {e}, conversation_id={conversation_id}, user_id={user_id}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_conversation_messages(self, conversation_id: str, user_id: str = None) -> list:
        """Get all messages for a conversation (no pagination), including deleted messages."""
        try:
            conv_id = self._safe_convert_conversation_id(conversation_id)
            user_uuid = uuid.UUID(user_id) if user_id and isinstance(user_id, str) else user_id
            
            # Get all messages (newest first), including deleted ones
            messages = Message.objects.filter(
                conversation_id=conv_id
            ).select_related('sender', 'reply_to', 'shared_post').order_by('-created_at')
            
            messages_data = []
            for message in messages:
                # Determine if sent by current user
                is_sent_by_me = False
                if user_uuid:
                    is_sent_by_me = (str(message.sender.user_id) == str(user_uuid))
                
                # Format shared post if exists
                shared_post_data = None
                if message.shared_post:
                    shared_post_data = {
                        'post_id': str(message.shared_post.post_id),
                        'title': message.shared_post.title or '',
                        'description': message.shared_post.description or '',
                        'created_at': message.shared_post.created_at.isoformat() if message.shared_post.created_at else None,
                        'media': [
                            {
                                'media_id': str(media.media_id),
                                'media_type': media.media_type,
                                'url': media.url
                            }
                            for media in message.shared_post.media.all()[:3]  # Limit to 3 for preview
                        ]
                    }
                
                message_data = {
                    'message_id': str(message.id),
                    'sender': {
                        'user_id': str(message.sender.user_id),
                        'user_name': message.sender.username,
                        'profile_picture_url': message.sender.profile_picture_url or ''
                    },
                    'text': message.text,
                    'file': {
                        'url': message.file,
                        'type': message.file_type,
                        'size': message.file_size,
                        'name': message.file_name
                    } if message.file else None,
                    'reply_to_id': str(message.reply_to.id) if message.reply_to else None,
                    'shared_post': shared_post_data,
                    'created_at': message.created_at.isoformat() if message.created_at else None,
                    'edited_at': message.edited_at.isoformat() if message.edited_at else None,
                    'is_deleted_for_everyone': message.is_deleted_for_everyone,
                    'is_sent_by_me': is_sent_by_me
                }
                messages_data.append(message_data)
            
            return messages_data
        except (ValueError, TypeError, OverflowError):
            return []
    
    def get_user_conversations(self, user_id: str) -> list:
        """Get all conversations for a user with last message preview."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            
            # Get all active conversations where user is a member
            memberships = ConversationMember.objects.filter(
                user__user_id=user_uuid,  # Use user__user_id to access UUIDField through ForeignKey
                left_at__isnull=True
            ).select_related('conversation').filter(
                conversation__is_active=True
            )
            
            conversations_data = []
            
            for membership in memberships:
                conversation = membership.conversation
                
                # Get last message
                last_message = Message.objects.filter(
                    conversation_id=conversation.id,
                    is_deleted_for_everyone=False
                ).select_related('sender').order_by('-created_at').first()
                
                # Format last message if exists
                last_message_data = None
                if last_message:
                    is_sent_by_me = (str(last_message.sender.user_id) == str(user_uuid))
                    
                    # Determine if user has seen the last message
                    is_seen = False
                    if is_sent_by_me:
                        # User sent the message, so they've seen it
                        is_seen = True
                    else:
                        # Check if user has read this message
                        if membership.last_read_at and last_message.created_at:
                            # User has read messages up to last_read_at
                            # If last_read_at is after or equal to message created_at, they've seen it
                            is_seen = (membership.last_read_at >= last_message.created_at)
                        else:
                            # User has never read any messages in this conversation
                            is_seen = False
                    
                    last_message_data = {
                        'message_id': str(last_message.id),
                        'text': last_message.text,
                        'sender': {
                            'user_id': str(last_message.sender.user_id),
                            'user_name': last_message.sender.username,
                            'profile_picture_url': last_message.sender.profile_picture_url or ''
                        },
                        'file': {
                            'url': last_message.file,
                            'type': last_message.file_type,
                            'name': last_message.file_name
                        } if last_message.file else None,
                        'created_at': last_message.created_at.isoformat() if last_message.created_at else None,
                        'is_sent_by_me': is_sent_by_me,
                        'is_seen': is_seen
                    }
                
                # Get other member(s) based on conversation type
                other_member = None
                members_data = []
                
                if conversation.type == ConversationTypeChoices.DIRECT:
                    # Get the other member (not current user)
                    other_membership = ConversationMember.objects.filter(
                        conversation_id=conversation.id,
                        left_at__isnull=True
                    ).exclude(user__user_id=user_uuid).select_related('user').first()  # Use user__user_id
                    
                    if other_membership:
                        other_member = {
                            'user_id': str(other_membership.user.user_id),
                            'user_name': other_membership.user.username,
                            'profile_picture_url': other_membership.user.profile_picture_url or ''
                        }
                else:
                    # GROUP conversation - get all members
                    all_members = ConversationMember.objects.filter(
                        conversation_id=conversation.id,
                        left_at__isnull=True
                    ).select_related('user')
                    
                    for mem in all_members:
                        members_data.append({
                            'user_id': str(mem.user.user_id),
                            'user_name': mem.user.username,
                            'profile_picture_url': mem.user.profile_picture_url or ''
                        })
                
                # Calculate unread count (messages after last_read_at)
                unread_count = 0
                if membership.last_read_at:
                    unread_count = Message.objects.filter(
                        conversation_id=conversation.id,
                        is_deleted_for_everyone=False,
                        created_at__gt=membership.last_read_at
                    ).exclude(sender__user_id=user_uuid).count()  # Use sender__user_id
                else:
                    # If never read, count all messages not sent by user
                    unread_count = Message.objects.filter(
                        conversation_id=conversation.id,
                        is_deleted_for_everyone=False
                    ).exclude(sender__user_id=user_uuid).count()  # Use sender__user_id
                
                # Determine last activity timestamp
                if last_message:
                    last_activity_at = last_message.created_at
                else:
                    last_activity_at = conversation.updated_at
                
                conversation_data = {
                    'conversation_id': conversation.id,
                    'type': conversation.type,
                    'name': conversation.name or '',
                    'description': conversation.description or '',
                    'image': conversation.image.url if conversation.image else '',
                    'is_active': conversation.is_active,
                    'last_message': last_message_data,
                    'other_member': other_member,  # For DIRECT
                    'members': members_data,  # For GROUP
                    'members_count': len(members_data) if members_data else 0,  # For GROUP
                    'unread_count': unread_count,
                    'last_activity_at': last_activity_at.isoformat() if last_activity_at else None
                }
                
                conversations_data.append(conversation_data)
            
            # Sort by last_activity_at (most recent first)
            conversations_data.sort(
                key=lambda x: x['last_activity_at'] or '', 
                reverse=True
            )
            
            return conversations_data
        except (ValueError, TypeError) as e:
            import traceback
            print(f"Error in get_user_conversations: {e}")
            print(traceback.format_exc())
            return []
