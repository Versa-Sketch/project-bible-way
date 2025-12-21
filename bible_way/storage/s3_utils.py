import boto3
import re
from urllib.parse import urlparse
from django.conf import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
REGION = settings.AWS_S3_REGION_NAME


def extract_s3_key_from_url(url: str) -> str:
    """
    Extract S3 key from full S3 URL.
    
    Args:
        url: Full S3 URL like https://bucket.s3.region.amazonaws.com/key
        
    Returns:
        S3 key path
    """
    if not url:
        return ""
    
    # If it's already a key (no http/https), return as-is
    if not url.startswith(('http://', 'https://')):
        return url
    
    try:
        parsed = urlparse(url)
        # Remove leading slash from path
        key = parsed.path.lstrip('/')
        return key
    except Exception:
        # Fallback: try regex extraction
        match = re.search(r'\.s3\.[^/]+\.amazonaws\.com/(.+)$', url)
        if match:
            return match.group(1)
        return url


def generate_presigned_url(s3_key: str, expiration: int = None) -> str:
    """
    Generate presigned URL for S3 object.
    
    Args:
        s3_key: S3 key path or full S3 URL (will extract key if URL provided)
        expiration: Expiration time in seconds (defaults to AWS_S3_PRESIGNED_URL_EXPIRATION setting)
        
    Returns:
        Presigned URL string
    """
    if not s3_key:
        return ""
    
    # Extract key if full URL provided
    key = extract_s3_key_from_url(s3_key)
    
    if not key:
        return s3_key  # Return original if extraction fails
    
    # Use default expiration from settings if not provided
    if expiration is None:
        expiration = getattr(settings, 'AWS_S3_PRESIGNED_URL_EXPIRATION', 3600)
    
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration
        )
        return presigned_url
    except Exception as e:
        # If presigned URL generation fails, return original URL/key
        # This ensures backward compatibility
        return s3_key


def upload_file_to_s3(file_obj, key: str) -> str:
    """
    file_obj: Django UploadedFile (from request.FILES)
    key: path in S3, e.g. "posts/<post_id>/<filename>"
    
    Returns:
        Public S3 URL (for storage in database, will be converted to presigned URL when returned)
    """

    s3_client.upload_fileobj(
        Fileobj=file_obj,
        Bucket=BUCKET_NAME,
        Key=key,
        ExtraArgs={
            "ContentType": file_obj.content_type
        },
    )

    public_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"
    return public_url

