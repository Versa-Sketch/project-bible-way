import os
import zipfile
import uuid
from io import BytesIO
from django.core.management.base import BaseCommand
from django.conf import settings
from bible_way.models import Sticker
from bible_way.storage.s3_utils import s3_client, BUCKET_NAME, REGION


class Command(BaseCommand):
    help = 'Extract images from stickers.zip and upload them to S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--zip-path',
            type=str,
            default='stickers.zip',
            help='Path to the zip file (default: stickers.zip in project root)'
        )

    def handle(self, *args, **options):
        zip_path = options['zip_path']
        
        # Get absolute path if relative
        if not os.path.isabs(zip_path):
            base_dir = settings.BASE_DIR
            zip_path = os.path.join(base_dir, zip_path)
        
        if not os.path.exists(zip_path):
            self.stdout.write(self.style.ERROR(f'Zip file not found: {zip_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Processing zip file: {zip_path}'))
        
        # Image file extensions to process
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        uploaded_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                self.stdout.write(f'Found {total_files} files in zip')
                
                for idx, filename in enumerate(file_list, 1):
                    # Skip directories
                    if filename.endswith('/'):
                        continue
                    
                    # Check if it's an image file
                    file_ext = os.path.splitext(filename.lower())[1]
                    if file_ext not in image_extensions:
                        skipped_count += 1
                        continue
                    
                    try:
                        # Extract file from zip
                        file_data = zip_ref.read(filename)
                        
                        # Generate unique S3 key
                        file_uuid = str(uuid.uuid4())
                        safe_filename = os.path.basename(filename)
                        # Sanitize filename
                        safe_filename = safe_filename.replace(' ', '_').replace('/', '_')
                        s3_key = f"stickers/{file_uuid}/{safe_filename}"
                        
                        # Determine content type
                        content_type_map = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.bmp': 'image/bmp',
                            '.webp': 'image/webp',
                        }
                        content_type = content_type_map.get(file_ext, 'image/jpeg')
                        
                        # Upload to S3
                        file_obj = BytesIO(file_data)
                        s3_client.upload_fileobj(
                            Fileobj=file_obj,
                            Bucket=BUCKET_NAME,
                            Key=s3_key,
                            ExtraArgs={
                                'ContentType': content_type
                            }
                        )
                        
                        # Generate public URL
                        public_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{s3_key}"
                        
                        # Create Sticker model instance
                        Sticker.objects.create(
                            image_url=public_url,
                            filename=safe_filename
                        )
                        
                        uploaded_count += 1
                        
                        if idx % 10 == 0:
                            self.stdout.write(f'Processed {idx}/{total_files} files...')
                        
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Error processing {filename}: {str(e)}')
                        )
                        continue
            
            self.stdout.write(self.style.SUCCESS(
                f'\nUpload complete!\n'
                f'  Uploaded: {uploaded_count}\n'
                f'  Skipped: {skipped_count}\n'
                f'  Errors: {error_count}'
            ))
            
        except zipfile.BadZipFile:
            self.stdout.write(self.style.ERROR('Invalid zip file'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing zip file: {str(e)}'))

