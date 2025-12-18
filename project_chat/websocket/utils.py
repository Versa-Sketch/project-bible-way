"""
Utility functions for WebSocket chat functionality.

Includes rate limiting, message validation, error codes, and serialization helpers.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import uuid
import base64
import os
import mimetypes

# Error codes
class ErrorCodes:
    """Error code constants for WebSocket responses."""
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    NOT_MEMBER = "NOT_MEMBER"
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    EDIT_TIME_EXPIRED = "EDIT_TIME_EXPIRED"
    DELETE_TIME_EXPIRED = "DELETE_TIME_EXPIRED"
    INVALID_ACTION = "INVALID_ACTION"
    SERVER_ERROR = "SERVER_ERROR"
    NO_FOLLOW_RELATIONSHIP = "NO_FOLLOW_RELATIONSHIP"
    POST_NOT_FOUND = "POST_NOT_FOUND"
    POST_SHARING_NOT_ALLOWED = "POST_SHARING_NOT_ALLOWED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"

# File validation constants
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.wma']

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# Rate limiting storage (in-memory, per user)
_rate_limit_storage: Dict[str, Dict] = {}


def check_rate_limit(user_id: str, action: str, max_requests: int = 30, window_seconds: int = 30) -> tuple[bool, Optional[int]]:
    """
    Check if user has exceeded rate limit for an action.
    
    Args:
        user_id: User ID
        action: Action name (e.g., 'send_message')
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        
    Returns:
        Tuple of (is_allowed, remaining_requests)
    """
    key = f"{user_id}:{action}"
    now = datetime.now()
    
    if key not in _rate_limit_storage:
        _rate_limit_storage[key] = {
            'requests': [],
            'window_start': now
        }
    
    storage = _rate_limit_storage[key]
    
    # Remove requests outside the time window
    cutoff_time = now - timedelta(seconds=window_seconds)
    storage['requests'] = [
        req_time for req_time in storage['requests']
        if req_time > cutoff_time
    ]
    
    # Check if limit exceeded
    if len(storage['requests']) >= max_requests:
        remaining = 0
        return False, remaining
    
    # Add current request
    storage['requests'].append(now)
    remaining = max_requests - len(storage['requests'])
    
    return True, remaining


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def validate_message_data(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate message data structure.
    
    Args:
        data: Message data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    # Check required fields for send_message
    if 'conversation_id' in data:
        if not data.get('conversation_id'):
            return False, "conversation_id is required"
        # conversation_id is integer, not UUID
        try:
            int(data['conversation_id'])
        except (ValueError, TypeError):
            return False, "conversation_id must be a valid integer"
    
    if 'content' in data:
        content = data.get('content', '')
        if not isinstance(content, str):
            return False, "content must be a string"
        # Allow empty content if file_url or shared_post is provided
        if len(content.strip()) == 0 and not data.get('file_url') and not data.get('shared_post_id'):
            return False, "content cannot be empty unless file_url or shared_post_id is provided"
    
    # Validate file_url if provided
    if 'file_url' in data and data.get('file_url'):
        file_url = data.get('file_url')
        if not isinstance(file_url, str):
            return False, "file_url must be a string"
        if not file_url.startswith(('http://', 'https://')):
            return False, "file_url must be a valid HTTP/HTTPS URL"
    
    # Validate shared_post_id if provided
    if 'shared_post_id' in data and data.get('shared_post_id'):
        shared_post_id = data.get('shared_post_id')
        if not validate_uuid(shared_post_id):
            return False, "shared_post_id must be a valid UUID"
    
    return True, None


def can_edit_message(message_created_at: datetime, hours_limit: int = 24) -> bool:
    """
    Check if a message can still be edited.
    
    Args:
        message_created_at: When the message was created
        hours_limit: Hours limit for editing (default 24)
        
    Returns:
        True if message can be edited, False otherwise
    """
    if not message_created_at:
        return False
    
    time_diff = datetime.now(message_created_at.tzinfo) - message_created_at
    return time_diff <= timedelta(hours=hours_limit)


def can_delete_message(message_created_at: datetime, days_limit: int = 7) -> bool:
    """
    Check if a message can still be deleted.
    
    Args:
        message_created_at: When the message was created
        days_limit: Days limit for deletion (default 7)
        
    Returns:
        True if message can be deleted, False otherwise
    """
    if not message_created_at:
        return False
    
    time_diff = datetime.now(message_created_at.tzinfo) - message_created_at
    return time_diff <= timedelta(days=days_limit)


def serialize_message(message, include_sender_info: bool = True) -> dict:
    """
    Serialize a Message model instance to dictionary.
    
    Args:
        message: Message model instance
        include_sender_info: Whether to include sender details
        
    Returns:
        Dictionary representation of the message
    """
    data = {
        'message_id': str(message.id),
        'conversation_id': str(message.conversation_id),
        'text': message.text,
        'file': message.file.url if message.file else None,
        'reply_to_id': str(message.reply_to_id) if message.reply_to else None,
        'created_at': message.created_at.isoformat() if message.created_at else None,
        'edited_at': message.edited_at.isoformat() if message.edited_at else None,
        'is_deleted_for_everyone': message.is_deleted_for_everyone,
    }
    
    if include_sender_info:
        data['sender_id'] = str(message.sender.user_id)
        data['sender_name'] = message.sender.username
        data['sender_email'] = message.sender.email
    
    return data


def serialize_conversation(conversation, user_id: str = None) -> dict:
    """
    Serialize a Conversation model instance to dictionary.
    
    Args:
        conversation: Conversation model instance
        user_id: Optional user ID for membership info
        
    Returns:
        Dictionary representation of the conversation
    """
    data = {
        'conversation_id': str(conversation.id),
        'type': conversation.type,
        'name': conversation.name,
        'description': conversation.description,
        'image': conversation.image.url if conversation.image else None,
        'created_by_id': str(conversation.created_by.user_id) if conversation.created_by else None,
        'created_at': conversation.created_at.isoformat() if conversation.created_at else None,
        'updated_at': conversation.updated_at.isoformat() if conversation.updated_at else None,
        'is_active': conversation.is_active,
    }
    
    return data


def determine_file_type_from_filename(filename: str) -> Optional[str]:
    """
    Determine file type (IMAGE, VIDEO, AUDIO) from filename extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        File type string or None if unknown
    """
    from project_chat.models import FileTypeChoices
    
    if not filename:
        return None
    
    # Get file extension
    path_lower = filename.lower()
    path = path_lower.split('?')[0]  # Remove query params if any
    file_ext = os.path.splitext(path)[1]
    
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        return FileTypeChoices.IMAGE
    elif file_ext in ALLOWED_VIDEO_EXTENSIONS:
        return FileTypeChoices.VIDEO
    elif file_ext in ALLOWED_AUDIO_EXTENSIONS:
        return FileTypeChoices.AUDIO
    
    return None


def decode_base64_file(file_data_base64: str) -> Tuple[bytes, str]:
    """
    Decode base64 file data.
    
    Args:
        file_data_base64: Base64 encoded file string (with or without data URL prefix)
        
    Returns:
        Tuple of (file_bytes, content_type)
        
    Raises:
        ValueError: If base64 string is invalid
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in file_data_base64:
            header, data = file_data_base64.split(',', 1)
            # Extract content type from header
            if 'data:' in header and ';base64' in header:
                content_type = header.split('data:')[1].split(';base64')[0]
            else:
                content_type = 'application/octet-stream'
        else:
            data = file_data_base64
            content_type = 'application/octet-stream'
        
        # Decode base64
        file_bytes = base64.b64decode(data)
        
        return file_bytes, content_type
    except Exception as e:
        raise ValueError(f"Invalid base64 file data: {str(e)}")


def validate_file_data(file_data_base64: str, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate file data and determine file type.
    
    Args:
        file_data_base64: Base64 encoded file string
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, error_message, file_type)
        - is_valid: True if file is valid
        - error_message: Error message if invalid, None if valid
        - file_type: File type (IMAGE, VIDEO, AUDIO) or None
    """
    from project_chat.models import FileTypeChoices
    
    # Check filename is provided
    if not filename:
        return False, "Filename is required when file_data is provided", None
    
    # Determine file type from filename
    file_type = determine_file_type_from_filename(filename)
    if not file_type:
        allowed = ', '.join(ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS + ALLOWED_AUDIO_EXTENSIONS)
        return False, f"Invalid file type. Allowed extensions: {allowed}", None
    
    # Decode and check file size
    try:
        file_bytes, _ = decode_base64_file(file_data_base64)
        file_size = len(file_bytes)
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds {max_mb} MB limit", None
        
        if file_size == 0:
            return False, "File is empty", None
        
        return True, None, file_type
    except ValueError as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Error validating file: {str(e)}", None


def validate_uploaded_file(file_obj, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate uploaded file object (Django UploadedFile).
    
    Args:
        file_obj: Django UploadedFile object from request.FILES
        max_size: Maximum file size in bytes (default: 10 MB)
        
    Returns:
        Tuple of (is_valid, error_message, file_type)
        - is_valid: True if file is valid
        - error_message: Error message if invalid, None if valid
        - file_type: File type (IMAGE, VIDEO, AUDIO) or None
    """
    from project_chat.models import FileTypeChoices
    
    # Check if file object is valid
    if not file_obj or not hasattr(file_obj, 'name'):
        return False, "Invalid file object", None
    
    # Check file name
    if not file_obj.name:
        return False, "Filename is required", None
    
    # Determine file type from filename
    file_type = determine_file_type_from_filename(file_obj.name)
    if not file_type:
        allowed = ', '.join(ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS + ALLOWED_AUDIO_EXTENSIONS)
        return False, f"Invalid file type. Allowed extensions: {allowed}", None
    
    # Check file size
    if not hasattr(file_obj, 'size'):
        return False, "Unable to determine file size", None
    
    if file_obj.size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds {max_mb} MB limit", None
    
    if file_obj.size == 0:
        return False, "File is empty", None
    
    return True, None, file_type

