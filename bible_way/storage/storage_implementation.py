from django.contrib.auth.hashers import make_password, check_password
import uuid
import os
from bible_way.models import User, UserFollowers, Post, Media, Comment, Reaction
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file


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
            username=username,
            user_name=user_name,
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
    
    def _determine_media_type_from_filename(self, filename_or_url: str) -> str:
        """Determine if filename/URL is image or video based on extension"""
        path_lower = filename_or_url.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        
        path = path_lower.split('?')[0]
        file_ext = os.path.splitext(path)[1]
        
        if file_ext in image_extensions:
            return Media.IMAGE
        elif file_ext in video_extensions:
            return Media.VIDEO
        else:
            return Media.IMAGE
    
    def _generate_s3_key(self, user_id: str, post_id: str, filename: str) -> str:
        """Generate S3 key path: bible_way/user/post/{user_id}/{post_id}/{filename}"""
        safe_filename = os.path.basename(filename)
        return f"bible_way/user/post/{user_id}/{post_id}/{safe_filename}"
    
    def upload_file_to_s3(self, post: Post, media_file, user_id: str) -> str:
        """Upload media file to S3 and return the URL"""
        try:
            s3_key = self._generate_s3_key(str(user_id), str(post.post_id), media_file.name)
            
            s3_url = s3_upload_file(media_file, s3_key)
            
            return s3_url
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
    
    def get_post_by_id(self, post_id: str) -> Post | None:
        """Get post by post_id"""
        try:
            post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
            return Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def update_post(self, post_id: str, user_id: str, title: str = None, description: str = None) -> Post:
        """Update post - only owner can update"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            post = Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        if post.user.user_id != user_uuid:
            raise Exception("You are not authorized to update this post")
        
        if title is not None:
            post.title = title.strip() if title else ''
        if description is not None:
            post.description = description.strip() if description else ''
        
        post.save()
        return post
    
    def delete_post(self, post_id: str, user_id: str) -> bool:
        """Delete post - only owner can delete"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            post = Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        if post.user.user_id != user_uuid:
            raise Exception("You are not authorized to delete this post")
        
        post.delete()
        return True
    
    def create_comment(self, post_id: str, user_id: str, description: str) -> Comment:
        """Create a comment on a post"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        post = Post.objects.get(post_id=post_uuid)
        user = User.objects.get(user_id=user_uuid)
        
        comment = Comment.objects.create(
            post=post,
            user=user,
            description=description.strip()
        )
        return comment
    
    def get_comments_by_post(self, post_id: str) -> list:
        """Get all comments for a post"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        
        try:
            Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        comments = Comment.objects.filter(post_id=post_uuid).order_by('-created_at')
        return list(comments)
    
    def get_comment_by_id(self, comment_id: str) -> Comment | None:
        """Get comment by comment_id"""
        try:
            comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
            return Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def update_comment(self, comment_id: str, user_id: str, description: str) -> Comment:
        """Update comment - only owner can update"""
        comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            comment = Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            raise Exception("Comment not found")
        
        if comment.user.user_id != user_uuid:
            raise Exception("You are not authorized to update this comment")
        
        comment.description = description.strip()
        comment.save()
        return comment
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete comment - only owner can delete"""
        comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            comment = Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            raise Exception("Comment not found")
        
        if comment.user.user_id != user_uuid:
            raise Exception("You are not authorized to delete this comment")
        
        comment.delete()
        return True
    
    def check_reaction_exists(self, user_id: str, post_id: str = None, comment_id: str = None) -> Reaction | None:
        """Check if a reaction already exists for user on post or comment"""
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            if post_id:
                post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
                return Reaction.objects.get(user__user_id=user_uuid, post__post_id=post_uuid)
            elif comment_id:
                comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
                return Reaction.objects.get(user__user_id=user_uuid, comment__comment_id=comment_uuid)
        except Reaction.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def like_post(self, post_id: str, user_id: str) -> Reaction:
        """Like a post - create reaction"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            post = Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        existing_reaction = self.check_reaction_exists(user_id, post_id=post_id)
        if existing_reaction:
            raise Exception("You have already liked this post")
        
        user = User.objects.get(user_id=user_uuid)
        reaction = Reaction.objects.create(
            user=user,
            post=post,
            reaction_type=Reaction.LIKE
        )
        return reaction
    
    def unlike_post(self, post_id: str, user_id: str) -> bool:
        """Unlike a post - delete reaction"""
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            post = Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        try:
            reaction = Reaction.objects.get(user__user_id=user_uuid, post__post_id=post_uuid)
        except Reaction.DoesNotExist:
            raise Exception("You have not liked this post")
        
        reaction.delete()
        return True
    
    def like_comment(self, comment_id: str, user_id: str) -> Reaction:
        """Like a comment - create reaction"""
        comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            comment = Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            raise Exception("Comment not found")
        
        existing_reaction = self.check_reaction_exists(user_id, comment_id=comment_id)
        if existing_reaction:
            raise Exception("You have already liked this comment")
        
        user = User.objects.get(user_id=user_uuid)
        reaction = Reaction.objects.create(
            user=user,
            comment=comment,
            reaction_type=Reaction.LIKE
        )
        return reaction
    
    def unlike_comment(self, comment_id: str, user_id: str) -> bool:
        """Unlike a comment - delete reaction"""
        comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            comment = Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            raise Exception("Comment not found")
        
        try:
            reaction = Reaction.objects.get(user__user_id=user_uuid, comment__comment_id=comment_uuid)
        except Reaction.DoesNotExist:
            raise Exception("You have not liked this comment")
        
        reaction.delete()
        return True