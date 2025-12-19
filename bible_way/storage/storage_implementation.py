from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Q, Case, When, Value, IntegerField, Exists, OuterRef
import uuid
import os
import secrets
from bible_way.models import User, UserFollowers, Post, Media, Comment, Reaction, Promotion, PromotionImage, PrayerRequest, Verse, Category, AgeGroup, Book, Language, Highlight, ShareLink, ShareLinkContentTypeChoices, Wallpaper
from bible_way.models.book_reading import ReadingNote, Chapters
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file


class UserDB:
    
    def get_user_by_email(self, email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    def get_user_by_user_name(self, user_name: str) -> User | None:
        """Map API user_name parameter to username for lookup"""
        try:
            return User.objects.get(username=user_name)
        except User.DoesNotExist:
            return None
    
    def get_user_by_username(self, username: str) -> User | None:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    def create_user(self, username: str, email: str, password: str, 
                    country: str, age: int, preferred_language: str, 
                    profile_picture_url: str = None) -> User:
        hashed_password = make_password(password)
        
        user = User.objects.create(
            username=username,
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
    
    def create_google_user(self, username: str, email: str, google_id: str,
                          country: str, age: int, preferred_language: str, 
                          profile_picture_url: str = None) -> User:
        user = User(
            username=username,
            email=email,
            google_id=google_id,
            country=country,
            age=age,
            preferred_language=preferred_language,
            profile_picture_url=profile_picture_url,
            auth_provider='GOOGLE',
            is_email_verified=True  # Google already verifies emails
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
    
    def search_users(self, query: str, limit: int = 20, current_user_id: str = None) -> dict:
        """
        Search users by username using Elasticsearch.
        """
        if not query or len(query.strip()) < 2:
            return {
                'users': [],
                'total_count': 0,
                'query': query
            }
        
        query = query.strip()
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        # Search with priority: exact match > starts with > contains
        from django.db.models import Case, When, IntegerField, Count
        
        # Build base query
        base_query = Q(username__iexact=query) | Q(username__istartswith=query) | Q(username__icontains=query)
        
        # Exclude current user from results
        if current_user_uuid:
            base_query = base_query & ~Q(user_id=current_user_uuid)
        
        # Build query with priority ordering
        users = User.objects.filter(base_query).annotate(
            priority=Case(
                When(username__iexact=query, then=1),
                When(username__istartswith=query, then=2),
                When(username__icontains=query, then=3),
                output_field=IntegerField()
            )
        ).annotate(
            followers_count=Count('followed', distinct=True)
        ).order_by('priority', 'username')[:limit]
        
        # Get total count (without limit, excluding current user)
        total_count = User.objects.filter(base_query).count()
        
        users_data = []
        for user in users:
            user_data = {
                'user_id': str(user.user_id),
                'user_name': user.username,  # Map username to user_name for API response
                'profile_picture_url': user.profile_picture_url or '',
                'followers_count': user.followers_count,
                'is_admin': user.is_staff
            }
            
            # Add follow status and conversation_id if current_user_id provided
            if current_user_uuid:
                is_following = UserFollowers.objects.filter(
                    follower_id__user_id=current_user_uuid,
                    followed_id__user_id=user.user_id
                ).exists()
                user_data['is_following'] = is_following
                
                # Check if conversation exists between current user and searched user
                try:
                    from project_chat.storage import ChatDB
                    chat_db = ChatDB()
                    conversation = chat_db.find_conversation_between_users(
                        current_user_id,
                        str(user.user_id)
                    )
                    user_data['conversation_id'] = str(conversation.id) if conversation else None
                except Exception as e:
                    # If conversation table doesn't exist or other error, set to None
                    user_data['conversation_id'] = None
            else:
                user_data['is_following'] = False
                user_data['conversation_id'] = None
            
            users_data.append(user_data)
        
        return {
            'users': users_data,
            'total_count': total_count,
            'query': query
        }
    
    def get_recommended_users(self, user_id: str, limit: int = 20) -> dict:
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise Exception("Invalid user_id format")
        
        limit = min(max(1, int(limit)), 20)
        
        following_user_ids = UserFollowers.objects.filter(
            follower_id__user_id=user_uuid
        ).values_list('followed_id__user_id', flat=True)
        
        queryset = User.objects.exclude(user_id=user_uuid).exclude(
            user_id__in=following_user_ids
        ).exclude(
            is_staff=True
        ).exclude(
            is_superuser=True
        )
        
        users = queryset.annotate(
            followers_count=Count('followed', distinct=True)
        ).order_by('-followers_count', 'username')[:limit]
        
        total_count = queryset.count()
        
        users_data = []
        for user in users:
            users_data.append({
                'user_id': str(user.user_id),
                'user_name': user.username,  # Map username to user_name for API response
                'profile_image': user.profile_picture_url or ''
            })
        
        return {
            'users': users_data,
            'total_count': total_count
        }
    
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
    
    def get_complete_user_profile(self, user_id: str, current_user_id: str | None = None):
        from bible_way.storage.dtos import CompleteUserProfileResponseDTO
        
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return None
        
        # Get user with follower and following counts
        user = User.objects.filter(user_id=user_uuid).annotate(
            followers_count=Count('followed', distinct=True),
            following_count=Count('follower', distinct=True)
        ).first()
        
        if not user:
            return None
        
        # Check if current_user is following this user
        is_following = False
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
                is_following = UserFollowers.objects.filter(
                    follower_id__user_id=current_user_uuid,
                    followed_id__user_id=user_uuid
                ).exists()
            except (ValueError, TypeError):
                is_following = False
        
        return CompleteUserProfileResponseDTO(
            user_id=str(user.user_id),
            user_name=user.username,  # Map username to user_name for API response
            email=user.email,
            country=user.country,
            age=user.age,
            preferred_language=user.preferred_language,
            profile_picture_url=user.profile_picture_url,
            is_admin=user.is_staff,
            followers_count=user.followers_count,
            following_count=user.following_count,
            is_following=is_following
        )
    
    def create_post(self, user_id: str, title: str = '', description: str = '') -> Post:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user = User.objects.get(user_id=user_uuid)
        
        post = Post.objects.create(
            user=user,
            title=title,
            description=description
        )
        return post
    
    def get_media_type_from_file(self, file_obj) -> str:
        if not file_obj or not hasattr(file_obj, 'name'):
            return Media.IMAGE
        
        return self._determine_media_type_from_filename(file_obj.name)
    
    def _determine_media_type_from_filename(self, filename_or_url: str) -> str:
        path_lower = filename_or_url.lower()
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        audio_extensions = ['.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac']
        
        path = path_lower.split('?')[0]
        file_ext = os.path.splitext(path)[1]
        
        if file_ext in image_extensions:
            return Media.IMAGE
        elif file_ext in video_extensions:
            return Media.VIDEO
        elif file_ext in audio_extensions:
            return Media.AUDIO
        else:
            return Media.IMAGE
    
    def _generate_s3_key(self, user_id: str, post_id: str, filename: str) -> str:
        safe_filename = os.path.basename(filename)
        return f"bible_way/user/post/{user_id}/{post_id}/{safe_filename}"
    
    def upload_file_to_s3(self, post: Post, media_file, user_id: str) -> str:
        try:
            s3_key = self._generate_s3_key(str(user_id), str(post.post_id), media_file.name)
            
            s3_url = s3_upload_file(media_file, s3_key)
            
            return s3_url
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    def create_media(self, post: Post, s3_url: str, media_type: str) -> Media:
        media = Media.objects.create(
            post=post,
            media_type=media_type,
            url=s3_url
        )
        return media
    
    def get_post_by_id(self, post_id: str) -> Post | None:
        try:
            post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
            return Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def update_post(self, post_id: str, user_id: str, title: str = None, description: str = None) -> Post:
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
    
    def get_comments_by_post(self, post_id: str, current_user_id: str = None) -> list:
        post_uuid = uuid.UUID(post_id) if isinstance(post_id, str) else post_id
        
        try:
            Post.objects.get(post_id=post_uuid)
        except Post.DoesNotExist:
            raise Exception("Post not found")
        
        comments = Comment.objects.select_related('user').filter(post_id=post_uuid).annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
        ).order_by('-created_at')
        
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        comments_data = []
        for comment in comments:
            is_liked = False
            
            if current_user_uuid:
                is_liked = Reaction.objects.filter(
                    comment=comment,
                    user__user_id=current_user_uuid,
                    reaction_type=Reaction.LIKE
                ).exists()
            
            comments_data.append({
                'comment_id': str(comment.comment_id),
                'user': {
                    'user_id': str(comment.user.user_id),
                    'user_name': comment.user.username,
                    'profile_picture_url': comment.user.profile_picture_url or ''
                },
                'description': comment.description,
                'likes_count': comment.likes_count,
                'is_liked': is_liked,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat()
            })
        
        return comments_data
    
    def get_comment_by_id(self, comment_id: str) -> Comment | None:
        try:
            comment_uuid = uuid.UUID(comment_id) if isinstance(comment_id, str) else comment_id
            return Comment.objects.get(comment_id=comment_uuid)
        except Comment.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def update_comment(self, comment_id: str, user_id: str, description: str) -> Comment:
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
    
    def get_all_posts_with_counts(self, limit: int = 10, offset: int = 0, current_user_id: str = None) -> dict:
        total_count = Post.objects.count()
        
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        # Build queryset with annotations
        queryset = Post.objects.select_related('user').prefetch_related('media').annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like')),
            comments_count=Count('comments')
        )
        
        # Add following status annotation and ordering if user is authenticated
        if current_user_uuid:
            queryset = queryset.annotate(
                is_following_author=Case(
                    When(
                        Exists(
                            UserFollowers.objects.filter(
                                follower_id__user_id=current_user_uuid,
                                followed_id=OuterRef('user')
                            )
                        ),
                        then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-is_following_author', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        posts = queryset[offset:offset + limit]
        
        posts_data = []
        for post in posts:
            media_list = []
            for media in post.media.all():
                media_list.append({
                    'media_id': str(media.media_id),
                    'media_type': media.media_type,
                    'url': media.url
                })
            
            is_liked = False
            is_commented = False
            
            if current_user_uuid:
                is_liked = Reaction.objects.filter(
                    post=post,
                    user__user_id=current_user_uuid,
                    reaction_type=Reaction.LIKE
                ).exists()
                
                is_commented = Comment.objects.filter(
                    post=post,
                    user__user_id=current_user_uuid
                ).exists()
            
            posts_data.append({
                'post_id': str(post.post_id),
                'user': {
                    'user_id': str(post.user.user_id),
                    'user_name': post.user.username,  # Map username to user_name for API response
                    'profile_picture_url': post.user.profile_picture_url or ''
                },
                'title': post.title,
                'description': post.description,
                'media': media_list,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'is_liked': is_liked,
                'is_commented': is_commented,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            })
        
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        
        return {
            'posts': posts_data,
            'limit': limit,
            'offset': offset,
            'total_count': total_count,
            'has_next': has_next,
            'has_previous': has_previous
        }
    
    def get_user_posts_with_counts(self, user_id: str, limit: int = 10, offset: int = 0, current_user_id: str = None) -> dict:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        total_count = Post.objects.filter(user__user_id=user_uuid).count()
        
        posts = Post.objects.prefetch_related('media').filter(user__user_id=user_uuid).annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like')),
            comments_count=Count('comments')
        ).order_by('-created_at')[offset:offset + limit]
        
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        posts_data = []
        for post in posts:
            media_list = []
            for media in post.media.all():
                media_list.append({
                    'media_id': str(media.media_id),
                    'media_type': media.media_type,
                    'url': media.url
                })
            
            is_liked = False
            is_commented = False
            
            if current_user_uuid:
                is_liked = Reaction.objects.filter(
                    post=post,
                    user__user_id=current_user_uuid,
                    reaction_type=Reaction.LIKE
                ).exists()
                
                is_commented = Comment.objects.filter(
                    post=post,
                    user__user_id=current_user_uuid
                ).exists()
            
            posts_data.append({
                'post_id': str(post.post_id),
                'title': post.title,
                'description': post.description,
                'media': media_list,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'is_liked': is_liked,
                'is_commented': is_commented,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            })
        
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        
        return {
            'posts': posts_data,
            'limit': limit,
            'offset': offset,
            'total_count': total_count,
            'has_next': has_next,
            'has_previous': has_previous
        }
    
    def get_user_comments(self, user_id: str) -> list:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        comments = Comment.objects.filter(user__user_id=user_uuid).annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
        ).order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'comment_id': str(comment.comment_id),
                'description': comment.description,
                'likes_count': comment.likes_count,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat()
            })
        
        return comments_data
    
    def get_all_promotions(self) -> list:
        promotions = Promotion.objects.prefetch_related('promotion_images').order_by('-created_at')
        
        promotions_data = []
        for promotion in promotions:
            images_data = []
            for image in promotion.promotion_images.all().order_by('order', 'created_at'):
                images_data.append({
                    'promotion_image_id': str(image.promotion_image_id),
                    'image_url': image.image_url,
                    'image_type': image.image_type,
                    'order': image.order,
                    'created_at': image.created_at.isoformat(),
                    'updated_at': image.updated_at.isoformat()
                })
            
            promotions_data.append({
                'promotion_id': str(promotion.promotion_id),
                'title': promotion.title,
                'description': promotion.description,
                'price': str(promotion.price),
                'redirect_link': promotion.redirect_link,
                'meta_data': promotion.meta_data or {},
                'images': images_data,
                'created_at': promotion.created_at.isoformat(),
                'updated_at': promotion.updated_at.isoformat()
            })
        
        return promotions_data
    
    def get_all_wallpapers(self) -> list:
        wallpapers = Wallpaper.objects.all().order_by('-created_at')
        
        wallpapers_data = []
        for wallpaper in wallpapers:
            wallpapers_data.append({
                'wallpaper_id': str(wallpaper.wallpaper_id),
                'image_url': wallpaper.image_url,
                'filename': wallpaper.filename,
                'created_at': wallpaper.created_at.isoformat()
            })
        
        return wallpapers_data
    
    def create_prayer_request(self, user_id: str, name: str, email: str, description: str, phone_number: str = None) -> PrayerRequest:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        user = User.objects.get(user_id=user_uuid)
        prayer_request = PrayerRequest.objects.create(
            user=user,
            name=name.strip(),
            email=email.strip(),
            phone_number=phone_number.strip() if phone_number else None,
            description=description.strip()
        )
        return prayer_request
    
    def update_prayer_request(self, prayer_request_id: str, user_id: str, name: str = None, email: str = None, phone_number: str = None, description: str = None) -> PrayerRequest:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            prayer_request = PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        if prayer_request.user.user_id != user_uuid:
            raise Exception("You are not authorized to update this prayer request")
        
        if name is not None:
            prayer_request.name = name.strip()
        if email is not None:
            prayer_request.email = email.strip()
        if phone_number is not None:
            prayer_request.phone_number = phone_number.strip()
        if description is not None:
            prayer_request.description = description.strip()
        
        prayer_request.save()
        return prayer_request
    
    def delete_prayer_request(self, prayer_request_id: str, user_id: str) -> bool:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            prayer_request = PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        if prayer_request.user.user_id != user_uuid:
            raise Exception("You are not authorized to delete this prayer request")
        
        prayer_request.delete()
        return True
    
    def get_all_prayer_requests(self, limit: int = 10, offset: int = 0, current_user_id: str = None) -> dict:
        total_count = PrayerRequest.objects.count()
        
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        prayer_requests = PrayerRequest.objects.select_related('user').annotate(
            comments_count=Count('comments'),
            reactions_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
        ).order_by('-created_at')[offset:offset + limit]
        
        prayer_requests_data = []
        for prayer_request in prayer_requests:
            is_liked = False
            
            if current_user_uuid:
                is_liked = Reaction.objects.filter(
                    prayer_request=prayer_request,
                    user__user_id=current_user_uuid,
                    reaction_type=Reaction.LIKE
                ).exists()
            
            prayer_requests_data.append({
                'prayer_request_id': str(prayer_request.prayer_request_id),
                'user': {
                    'user_id': str(prayer_request.user.user_id),
                    'user_name': prayer_request.user.username,  # Map username to user_name for API response
                    'profile_picture_url': prayer_request.user.profile_picture_url or ''
                },
                'name': prayer_request.name,
                'email': prayer_request.email,
                'phone_number': prayer_request.phone_number,
                'description': prayer_request.description,
                'comments_count': prayer_request.comments_count,
                'reactions_count': prayer_request.reactions_count,
                'is_liked': is_liked,
                'created_at': prayer_request.created_at.isoformat(),
                'updated_at': prayer_request.updated_at.isoformat()
            })
        
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        
        return {
            'prayer_requests': prayer_requests_data,
            'limit': limit,
            'offset': offset,
            'total_count': total_count,
            'has_next': has_next,
            'has_previous': has_previous
        }
    
    def get_user_prayer_requests(self, user_id: str, limit: int = 10, offset: int = 0, current_user_id: str = None) -> dict:
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        total_count = PrayerRequest.objects.filter(user__user_id=user_uuid).count()
        
        prayer_requests = PrayerRequest.objects.filter(user__user_id=user_uuid).select_related('user').annotate(
            comments_count=Count('comments'),
            reactions_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
        ).order_by('-created_at')[offset:offset + limit]
        
        current_user_uuid = None
        if current_user_id:
            try:
                current_user_uuid = uuid.UUID(current_user_id) if isinstance(current_user_id, str) else current_user_id
            except (ValueError, TypeError):
                current_user_uuid = None
        
        prayer_requests_data = []
        for prayer_request in prayer_requests:
            is_liked = False
            
            if current_user_uuid:
                is_liked = Reaction.objects.filter(
                    prayer_request=prayer_request,
                    user__user_id=current_user_uuid,
                    reaction_type=Reaction.LIKE
                ).exists()
            
            prayer_requests_data.append({
                'prayer_request_id': str(prayer_request.prayer_request_id),
                'user': {
                    'user_id': str(prayer_request.user.user_id),
                    'user_name': prayer_request.user.username,  # Map username to user_name for API response
                    'profile_picture_url': prayer_request.user.profile_picture_url or ''
                },
                'name': prayer_request.name,
                'email': prayer_request.email,
                'phone_number': prayer_request.phone_number,
                'description': prayer_request.description,
                'comments_count': prayer_request.comments_count,
                'reactions_count': prayer_request.reactions_count,
                'is_liked': is_liked,
                'created_at': prayer_request.created_at.isoformat(),
                'updated_at': prayer_request.updated_at.isoformat()
            })
        
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        
        return {
            'prayer_requests': prayer_requests_data,
            'limit': limit,
            'offset': offset,
            'total_count': total_count,
            'has_next': has_next,
            'has_previous': has_previous
        }
    
    def create_prayer_request_comment(self, prayer_request_id: str, user_id: str, description: str) -> Comment:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            prayer_request = PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        user = User.objects.get(user_id=user_uuid)
        
        comment = Comment.objects.create(
            prayer_request=prayer_request,
            user=user,
            description=description.strip()
        )
        return comment
    
    def get_prayer_request_comments(self, prayer_request_id: str) -> list:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        
        try:
            PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        comments = Comment.objects.select_related('user').filter(prayer_request_id=prayer_request_uuid).annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
        ).order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'comment_id': str(comment.comment_id),
                'user': {
                    'user_id': str(comment.user.user_id),
                    'user_name': comment.user.username,  # Map username to user_name for API response
                    'profile_picture_url': comment.user.profile_picture_url or ''
                },
                'description': comment.description,
                'likes_count': comment.likes_count,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat()
            })
        
        return comments_data
    
    def check_prayer_request_reaction_exists(self, user_id: str, prayer_request_id: str):
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        
        try:
            return Reaction.objects.get(user__user_id=user_uuid, prayer_request__prayer_request_id=prayer_request_uuid)
        except Reaction.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def like_prayer_request(self, prayer_request_id: str, user_id: str) -> Reaction:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            prayer_request = PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        existing_reaction = self.check_prayer_request_reaction_exists(user_id, prayer_request_id)
        if existing_reaction:
            raise Exception("You have already liked this prayer request")
        
        user = User.objects.get(user_id=user_uuid)
        reaction = Reaction.objects.create(
            user=user,
            prayer_request=prayer_request,
            reaction_type=Reaction.LIKE
        )
        return reaction
    
    def unlike_prayer_request(self, prayer_request_id: str, user_id: str) -> bool:
        prayer_request_uuid = uuid.UUID(prayer_request_id) if isinstance(prayer_request_id, str) else prayer_request_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            prayer_request = PrayerRequest.objects.get(prayer_request_id=prayer_request_uuid)
        except PrayerRequest.DoesNotExist:
            raise Exception("Prayer request not found")
        
        try:
            reaction = Reaction.objects.get(user__user_id=user_uuid, prayer_request__prayer_request_id=prayer_request_uuid)
        except Reaction.DoesNotExist:
            raise Exception("You have not liked this prayer request")
        
        reaction.delete()
        return True
    
    def check_verse_reaction_exists(self, user_id: str, verse_id: str) -> Reaction | None:
        try:
            return Reaction.objects.get(user__user_id=user_id, verse__verse_id=verse_id)
        except Reaction.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def like_verse(self, verse_id: str, user_id: str) -> Reaction:    
        try:
            verse = Verse.objects.get(verse_id=verse_id)
        except Verse.DoesNotExist:
            raise Exception("Verse not found")
        
        existing_reaction = self.check_verse_reaction_exists(user_id, verse_id)
        if existing_reaction:
            raise Exception("You have already liked this verse")
        
        user = User.objects.get(user_id=user_id)
        reaction = Reaction.objects.create(
            user=user,
            verse=verse,
            reaction_type=Reaction.LIKE
        )
        return reaction
    
    def get_verse(self, user_id: str):
        try:
            verse = Verse.objects.annotate(
                likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
            ).order_by('-created_at').first()
            
            if not verse:
                return None
            
            # Check if user has liked this verse
            is_liked = False
            if user_id:
                existing_reaction = self.check_verse_reaction_exists(user_id, str(verse.verse_id))
                if existing_reaction:
                    is_liked = True
            
            return {
                'verse_id': str(verse.verse_id),
                'title': verse.title or 'Quote of the day',
                'description': verse.description or '',
                'likes_count': verse.likes_count or 0,
                'is_liked': is_liked,
                'created_at': verse.created_at.isoformat(),
                'updated_at': verse.updated_at.isoformat()
            }
        except Exception:
            return None
    
    def get_all_verses_with_like_count(self, user_id: str = None):
        try:
            # Build queryset with like count annotation
            verses_query = Verse.objects.annotate(
                likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'))
            )
            
            # Add is_liked annotation if user_id provided
            if user_id:
                verses_query = verses_query.annotate(
                    is_liked=Exists(
                        Reaction.objects.filter(
                            verse=OuterRef('verse_id'),
                            user__user_id=user_id,
                            reaction_type='like'
                        )
                    )
                )
            
            verses = verses_query.order_by('-created_at')
            
            verses_data = []
            for verse in verses:
                verses_data.append({
                    'verse_id': str(verse.verse_id),
                    'title': verse.title or 'Quote of the day',
                    'description': verse.description or '',
                    'likes_count': verse.likes_count or 0,
                    'is_liked': getattr(verse, 'is_liked', False),
                    'created_at': verse.created_at.isoformat() if verse.created_at else None,
                    'updated_at': verse.updated_at.isoformat() if verse.updated_at else None
                })
            
            return verses_data
        except Exception as e:
            raise Exception(f"Failed to retrieve verses: {str(e)}")
    
    
    def create_verse(self, title: str, description: str) -> Verse:
        verse = Verse.objects.create(
            title=title.strip() if title else 'Quote of the day',
            description=description.strip()
        )
        return verse
    
    def create_promotion(self, title: str, description: str, price, redirect_link: str, meta_data: dict = None) -> Promotion:
        promotion = Promotion.objects.create(
            title=title.strip(),
            description=description.strip() if description else '',
            price=price,
            redirect_link=redirect_link.strip(),
            meta_data=meta_data
        )
        return promotion
    
    def create_promotion_images(self, promotion: Promotion, image_urls: list) -> list:
        promotion_images = []
        for index, image_url in enumerate(image_urls):
            promotion_image = PromotionImage.objects.create(
                promotion=promotion,
                image_url=image_url,
                image_type='image',
                order=index
            )
            promotion_images.append(promotion_image)
        return promotion_images
    
    def create_category(self, category_name: str, cover_image_url: str = None, description: str = None, display_order: int = 0) -> Category:
        category = Category.objects.create(
            category_name=category_name,
            cover_image_url=cover_image_url,
            description=description or '',
            display_order=display_order
        )
        return category
    
    def get_all_categories(self):
        return Category.objects.all().order_by('display_order', 'category_name')
    
    def create_age_group(self, age_group_name: str, cover_image_url: str = None, description: str = None, display_order: int = 0) -> AgeGroup:
        age_group = AgeGroup.objects.create(
            age_group_name=age_group_name,
            cover_image_url=cover_image_url,
            description=description or '',
            display_order=display_order
        )
        return age_group
    
    def get_all_age_groups(self):
        return AgeGroup.objects.all().order_by('display_order', 'age_group_name')
    
    def get_all_languages(self):
        return Language.objects.all().order_by('language_name')
    
    def get_category_by_id(self, category_id: str):
        try:
            return Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return None
    
    def get_age_group_by_id(self, age_group_id: str):
        try:
            return AgeGroup.objects.get(age_group_id=age_group_id)
        except AgeGroup.DoesNotExist:
            return None
    
    def get_language_by_id(self, language_id: str):
        try:
            return Language.objects.get(language_id=language_id)
        except Language.DoesNotExist:
            return None
    
    def create_book(self, title: str, category_id: str, age_group_id: str, language_id: str, 
                    cover_image_url: str = None, description: str = None, book_order: int = 0) -> Book:
        category = Category.objects.get(category_id=category_id)
        age_group = AgeGroup.objects.get(age_group_id=age_group_id)
        language = Language.objects.get(language_id=language_id)
        
        book = Book.objects.create(
            title=title,
            description=description or '',
            category=category,
            age_group=age_group,
            language=language,
            cover_image_url=cover_image_url,
            book_order=book_order
        )
        return book
    
    def get_books_by_category_and_age_group(self, category_id: str, age_group_id: str):
        return Book.objects.filter(
            category__category_id=category_id,
            age_group__age_group_id=age_group_id,
            is_active=True
        ).select_related('category', 'age_group', 'language').order_by('book_order', 'title')
    
    def get_book_by_id(self, book_id: str):
        return Book.objects.select_related('category', 'age_group', 'language').get(book_id=book_id)
    
    def get_book_chapters(self, book_id: str):
        return Chapters.objects.filter(book_id=book_id).order_by('chapter_number')
    
    def get_max_chapter_number(self, book_id: str):
        from django.db.models import Max
        result = Chapters.objects.filter(book_id=book_id).aggregate(max_number=Max('chapter_number'))
        return result['max_number'] if result['max_number'] is not None else 0
    
    def get_chapters_count(self, book_id: str):
        return Chapters.objects.filter(book_id=book_id).count()
    
    def create_chapter(self, book_id: str, title: str, description: str, chapter_url: str, 
                      chapter_number: int, metadata: dict = None) -> Chapters:
        book = Book.objects.get(book_id=book_id)
        chapter = Chapters.objects.create(
            book=book,
            title=title,
            description=description or '',
            chapter_url=chapter_url,
            chapter_number=chapter_number,
            metadata=metadata or {}
        )
        return chapter
    
    def update_book_parsed_status(self, book_id: str, total_chapters: int, parsed_at=None) -> Book:
        from django.utils import timezone
        book = Book.objects.get(book_id=book_id)
        book.is_parsed = True
        book.total_chapters = total_chapters
        if parsed_at:
            book.parsed_at = parsed_at
        else:
            book.parsed_at = timezone.now()
        book.save()
        return book
    
    def create_highlight(self, user_id: str, book_id: str, block_id: str = None, 
                        start_offset: str = None, end_offset: str = None, color: str = 'yellow') -> Highlight:
        user = User.objects.get(user_id=user_id)
        book = Book.objects.get(book_id=book_id)
        
        highlight = Highlight.objects.create(
            user=user,
            book=book,
            block_id=block_id,
            start_offset=start_offset,
            end_offset=end_offset,
            color=color
        )
        return highlight
    
    def get_highlights_by_user_and_book(self, user_id: str, book_id: str):
        return Highlight.objects.filter(
            user__user_id=user_id,
            book__book_id=book_id
        ).select_related('user', 'book').order_by('-created_at')
    
    def get_highlight_by_id(self, highlight_id: str):
        try:
            return Highlight.objects.select_related('user', 'book').get(highlight_id=highlight_id)
        except Highlight.DoesNotExist:
            return None
    
    def delete_highlight(self, highlight_id: str, user_id: str):
        highlight = Highlight.objects.get(highlight_id=highlight_id, user__user_id=user_id)
        highlight.delete()
        return True
    
    def create_reading_note(self, user_id: str, book_id: str, content: str,
                           chapter_id: str = None, block_id: str = None) -> ReadingNote:
        user = User.objects.get(user_id=user_id)
        book = Book.objects.get(book_id=book_id)
        
        reading_note = ReadingNote.objects.create(
            user=user,
            book=book,
            content=content,
            chapter_id=chapter_id,
            block_id=block_id
        )
        return reading_note
    
    def get_reading_notes_by_user_and_book(self, user_id: str, book_id: str):
        return ReadingNote.objects.filter(
            user__user_id=user_id,
            book__book_id=book_id
        ).select_related('user', 'book').order_by('-created_at')
    
    def get_reading_note_by_id(self, note_id: str):
        try:
            return ReadingNote.objects.select_related('user', 'book').get(note_id=note_id)
        except ReadingNote.DoesNotExist:
            return None
    
    def update_reading_note(self, note_id: str, user_id: str, content: str) -> ReadingNote:
        note_uuid = uuid.UUID(note_id) if isinstance(note_id, str) else note_id
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        try:
            reading_note = ReadingNote.objects.get(note_id=note_uuid)
        except ReadingNote.DoesNotExist:
            raise Exception("Reading note not found")
        
        if reading_note.user.user_id != user_uuid:
            raise Exception("You are not authorized to update this reading note")
        
        reading_note.content = content.strip()
        reading_note.save()
        return reading_note
    
    def _generate_unique_share_token(self) -> str:
        """Generate a unique URL-safe token for share links."""
        max_attempts = 10
        for _ in range(max_attempts):
            token = secrets.token_urlsafe(8)[:12]  # Generate 12-character URL-safe token
            if not ShareLink.objects.filter(share_token=token).exists():
                return token
        raise Exception("Failed to generate unique share token after multiple attempts")
    
    def create_share_link(self, content_type: str, content_id: str, user_id: str) -> ShareLink:
        """Create a share link for a post or profile."""
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        content_uuid = uuid.UUID(content_id) if isinstance(content_id, str) else content_id
        
        # Validate content_type
        if content_type not in [ShareLinkContentTypeChoices.POST, ShareLinkContentTypeChoices.PROFILE]:
            raise Exception("Invalid content_type. Must be 'POST' or 'PROFILE'")
        
        # Check if share link already exists for this content and user
        existing_link = ShareLink.objects.filter(
            content_type=content_type,
            content_id=content_uuid,
            created_by__user_id=user_uuid,
            is_active=True
        ).first()
        
        if existing_link:
            return existing_link
        
        # Generate unique token
        share_token = self._generate_unique_share_token()
        
        user = User.objects.get(user_id=user_uuid)
        share_link = ShareLink.objects.create(
            share_token=share_token,
            content_type=content_type,
            content_id=content_uuid,
            created_by=user
        )
        return share_link
    
    def get_share_link_by_token(self, token: str) -> ShareLink | None:
        """Get ShareLink by token. Returns None if not found or inactive."""
        try:
            share_link = ShareLink.objects.get(share_token=token, is_active=True)
            return share_link
        except ShareLink.DoesNotExist:
            return None
        except (ValueError, TypeError):
            return None
    
    def get_post_by_share_token(self, token: str) -> Post | None:
        """Get Post by share token. Returns None if token invalid or not for a POST."""
        share_link = self.get_share_link_by_token(token)
        if not share_link:
            return None
        
        if share_link.content_type != ShareLinkContentTypeChoices.POST:
            return None
        
        try:
            post = Post.objects.select_related('user').prefetch_related('media').get(
                post_id=share_link.content_id
            )
            return post
        except Post.DoesNotExist:
            return None
    
    def get_profile_by_share_token(self, token: str) -> User | None:
        """Get User profile by share token. Returns None if token invalid or not for a PROFILE."""
        share_link = self.get_share_link_by_token(token)
        if not share_link:
            return None
        
        if share_link.content_type != ShareLinkContentTypeChoices.PROFILE:
            return None
        
        try:
            user = User.objects.get(user_id=share_link.content_id)
            return user
        except User.DoesNotExist:
            return None