import boto3
from django.conf import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
REGION = settings.AWS_S3_REGION_NAME


def upload_file_to_s3(file_obj, key: str) -> str:
    """
    file_obj: Django UploadedFile (from request.FILES)
    key: path in S3, e.g. "posts/<post_id>/<filename>"
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

