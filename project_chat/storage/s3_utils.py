"""
S3 utility functions for chat file uploads.

Handles uploading chat files (images, videos, audio) to AWS S3.
Supports both Django UploadedFile objects and bytes.
"""

import os
import boto3
import uuid
from io import BytesIO
from django.conf import settings
from typing import Optional

# Reuse S3 client configuration
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
REGION = settings.AWS_S3_REGION_NAME


def upload_chat_file_to_s3(
    file_obj,  # Django UploadedFile or bytes
    filename: str,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    message_id: Optional[str] = None,
    content_type: Optional[str] = None
) -> str:
    """
    Upload chat file to S3 and return public URL.
    
    Args:
        file_obj: Django UploadedFile object or bytes
        filename: Original filename (will be sanitized)
        user_id: Optional user ID for organizing files
        conversation_id: Optional conversation ID for organizing files
        message_id: Optional message ID for organizing files
        content_type: Optional MIME type (auto-detected from file_obj if not provided)
        
    Returns:
        Public S3 URL of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        # Determine content type
        if not content_type:
            if hasattr(file_obj, 'content_type') and file_obj.content_type:
                content_type = file_obj.content_type
            else:
                content_type = 'application/octet-stream'
        
        # Generate unique S3 key
        safe_filename = os.path.basename(filename)
        file_uuid = str(uuid.uuid4())
        
        # Generate unique path organized by conversation_id
        # Priority: conversation_id > user_id > generic
        if conversation_id:
            # Organize by conversation: chat/files/conversations/{conversation_id}/{uuid}/{filename}
            s3_key = f"chat/files/conversations/{conversation_id}/{file_uuid}/{safe_filename}"
        elif user_id:
            # Fallback to user-based: chat/files/users/{user_id}/{uuid}/{filename}
            s3_key = f"chat/files/users/{user_id}/{file_uuid}/{safe_filename}"
        else:
            # Generic fallback: chat/files/{uuid}/{filename}
            s3_key = f"chat/files/{file_uuid}/{safe_filename}"
        
        # Handle file object (Django UploadedFile) or bytes
        if hasattr(file_obj, 'read'):
            # Django UploadedFile - can be uploaded directly
            file_to_upload = file_obj
        else:
            # Bytes - create file-like object
            file_to_upload = BytesIO(file_obj)
        
        # Upload to S3 (without ACL to avoid Block Public Access issues)
        # Access will be controlled via bucket policy or presigned URLs
        extra_args = {
            "ContentType": content_type
        }
        
        # Only add ACL if explicitly allowed and not blocked
        # Check if we should use ACL (only if bucket allows it)
        use_acl = getattr(settings, 'AWS_S3_USE_ACL', False)
        if use_acl and hasattr(settings, 'AWS_DEFAULT_ACL'):
            extra_args["ACL"] = settings.AWS_DEFAULT_ACL
        
        s3_client.upload_fileobj(
            Fileobj=file_to_upload,
            Bucket=BUCKET_NAME,
            Key=s3_key,
            ExtraArgs=extra_args
        )
        
        # Generate public URL (no expiration)
        # Note: Requires bucket policy to allow public read access
        # If bucket has Block Public Access, you'll need to configure bucket policy
        if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN') and settings.AWS_S3_CUSTOM_DOMAIN:
            public_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        else:
            public_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{s3_key}"
        
        return public_url
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")

