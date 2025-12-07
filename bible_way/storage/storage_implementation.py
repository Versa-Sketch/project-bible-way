from django.contrib.auth.hashers import make_password, check_password
from bible_way.models import User, UserFollowers


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
