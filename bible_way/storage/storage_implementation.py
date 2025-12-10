from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import uuid
import os
import requests
from urllib.parse import urlparse
from bible_way.models import User, UserFollowers, Post, Media


class UserDB:
    
    def get_user_by_email(self, email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    def get_user_by_user_name(self, user_name: str) -> User | None:
        try:
            return User.objects.get(user_name=user_name)
        except User.DoesNotExist:
            return None
    
    def create_user(self, username: str, user_name: str, email: str, password: str, 
                    country: str, age: int, preferred_language: str, 
                    profile_picture_url: str = None) -> User:
        hashed_password = make_password(password)
        
        user = User.objects.create(
            username=username,      # Required by Django's AbstractUser (inherited field)
            user_name=user_name,    # Our custom field defined in User model
            email=email,
            country=country,
            age=age,
            preferred_language=preferred_language,
            password=hashed_password,
            profile_picture_url=profile_picture_url
        )
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.get_user_by_email(email)
        if user and check_password(password, user.password):
            return user
        return None
    
    def get_user_by_google_id(self, google_id: str) -> User | None:
        try:
            return User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            return None
    
    def create_google_user(self, username: str, user_name: str, email: str, google_id: str,
                          country: str, age: int, preferred_language: str, 
                          profile_picture_url: str = None) -> User:
        user = User(
            username=username,
            user_name=user_name,
            email=email,
            google_id=google_id,
            country=country,
            age=age,
            preferred_language=preferred_language,
            profile_picture_url=profile_picture_url,
            auth_provider='GOOGLE'
        )
        user.set_unusable_password()
        user.save()
        return user
    
    def update_user_auth_provider(self, user: User, provider: str) -> User:
        user.auth_provider = provider
        user.save()
        return user
    
    def check_user_exists_by_email(self, email: str) -> tuple[bool, User | None]:
        try:
            user = User.objects.get(email=email)
            return True, user
        except User.DoesNotExist:
            return False, None
    
    def get_user_by_user_id(self, user_id: str) -> User | None:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    
    def check_follow_exists(self, follower_id: str, followed_id: str) -> bool:
        try:
            import uuid
            follower_uuid = uuid.UUID(follower_id) if isinstance(follower_id, str) else follower_id
            followed_uuid = uuid.UUID(followed_id) if isinstance(followed_id, str) else followed_id
            UserFollowers.objects.get(follower_id__user_id=follower_uuid, followed_id__user_id=followed_uuid)
            return True
        except UserFollowers.DoesNotExist:
            return False
    
    def follow_user(self, follower_id: str, followed_id: str) -> UserFollowers:
        import uuid
        follower_uuid = uuid.UUID(follower_id) if isinstance(follower_id, str) else follower_id
        followed_uuid = uuid.UUID(followed_id) if isinstance(followed_id, str) else followed_id
        
        follower = User.objects.get(user_id=follower_uuid)
        followed = User.objects.get(user_id=followed_uuid)
        
        follow_relationship = UserFollowers.objects.create(
            follower_id=follower,
            followed_id=followed
        )
        return follow_relationship
    
    def unfollow_user(self, follower_id: str, followed_id: str) -> bool:
        import uuid
        follower_uuid = uuid.UUID(follower_id) if isinstance(follower_id, str) else follower_id
        followed_uuid = uuid.UUID(followed_id) if isinstance(followed_id, str) else followed_id
        
        try:
            follow_relationship = UserFollowers.objects.get(
                follower_id__user_id=follower_uuid,
                followed_id__user_id=followed_uuid
            )
            follow_relationship.delete()
            return True
        except UserFollowers.DoesNotExist:
            return False
    
    def create_post(self, user_id: str, title: str = '', description: str = '') -> Post:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user = User.objects.get(user_id=user_uuid)
        
        post = Post.objects.create(
            user=user,
            title=title,
            description=description
        )
        return post
    
    def _determine_media_type(self, file) -> str:
        """Determine if file is image or video based on extension"""
        filename = file.name.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        
        file_ext = os.path.splitext(filename)[1]
        
        if file_ext in image_extensions:
            return Media.IMAGE
        elif file_ext in video_extensions:
            return Media.VIDEO
        else:
            # Default to image if unknown
            return Media.IMAGE
    
    def _determine_media_type_from_url(self, url: str) -> str:
        """Determine if URL is image or video based on extension"""
        url_lower = url.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        
        # Extract extension from URL (before query parameters)
        url_path = url_lower.split('?')[0]
        file_ext = os.path.splitext(url_path)[1]
        
        if file_ext in image_extensions:
            return Media.IMAGE
        elif file_ext in video_extensions:
            return Media.VIDEO
        else:
            # Default to image if unknown
            return Media.IMAGE
    
    def _generate_s3_key(self, user_id: str, post_id: str, filename: str) -> str:
        """Generate S3 key path: bible_way/user/post/{user_id}/{post_id}/{filename}"""
        # Clean filename to avoid issues
        safe_filename = os.path.basename(filename)
        return f"bible_way/user/post/{user_id}/{post_id}/{safe_filename}"
    
    def upload_media_to_s3(self, post: Post, media_file, user_id: str) -> str:
        """Upload media file to S3 and return the URL"""
        try:
            # Generate S3 key
            s3_key = self._generate_s3_key(str(user_id), str(post.post_id), media_file.name)
            
            # Upload to S3 using default storage (configured in settings)
            file_name = default_storage.save(s3_key, media_file)
            
            # Get the URL from storage
            file_url = default_storage.url(file_name)
            
            return file_url
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def download_and_upload_to_s3(self, post: Post, media_url: str, user_id: str) -> str:
        """Download file from URL and upload to S3, return S3 URL"""
        try:
            # Download file from URL
            response = requests.get(media_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Get filename from URL or generate one
            parsed_url = urlparse(media_url)
            filename = os.path.basename(parsed_url.path)
            
            # If no filename in URL, generate one based on content type
            if not filename or '.' not in filename:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    filename = f"image_{uuid.uuid4().hex[:8]}.jpg"
                elif 'video' in content_type:
                    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
                else:
                    filename = f"file_{uuid.uuid4().hex[:8]}"
            
            # Generate S3 key
            s3_key = self._generate_s3_key(str(user_id), str(post.post_id), filename)
            
            # Create ContentFile from downloaded content
            file_content = ContentFile(response.content)
            file_content.name = filename
            
            # Upload to S3
            file_name = default_storage.save(s3_key, file_content)
            
            # Get the S3 URL
            s3_url = default_storage.url(file_name)
            
            return s3_url
        except requests.RequestException as e:
            raise Exception(f"Failed to download file from URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def create_media(self, post: Post, s3_url: str, media_type: str) -> Media:
        """Create Media record with S3 URL"""
        media = Media.objects.create(
            post=post,
            media_type=media_type,
            url=s3_url
        )
        return media