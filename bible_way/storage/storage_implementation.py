from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Q
import uuid
import os
from bible_way.models import User, UserFollowers, Post, Media, Comment, Reaction, Promotion, PromotionImage, PrayerRequest, Verse
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
    
    def search_users(self, query: str, limit: int = 20, current_user_id: str = None) -> dict:
        """
        Search users by username (partial match, case-insensitive).
        
        Args:
            query: Search term (e.g., "ven")
            limit: Maximum number of results
            current_user_id: Optional - to include follow status and followers count
            
        Returns:
            Dictionary with:
            - users: List of user dictionaries
            - total_count: Total matching users
            - query: Original search query
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
        
        # Build query with priority ordering
        users = User.objects.filter(
            Q(user_name__iexact=query) |
            Q(user_name__istartswith=query) |
            Q(user_name__icontains=query)
        ).annotate(
            priority=Case(
                When(user_name__iexact=query, then=1),
                When(user_name__istartswith=query, then=2),
                When(user_name__icontains=query, then=3),
                output_field=IntegerField()
            )
        ).annotate(
            followers_count=Count('followed', distinct=True)
        ).order_by('priority', 'user_name')[:limit]
        
        # Get total count (without limit)
        total_count = User.objects.filter(
            Q(user_name__iexact=query) |
            Q(user_name__istartswith=query) |
            Q(user_name__icontains=query)
        ).count()
        
        users_data = []
        for user in users:
            user_data = {
                'user_id': str(user.user_id),
                'user_name': user.user_name,
                'profile_picture_url': user.profile_picture_url or '',
                'followers_count': user.followers_count
            }
            
            # Add follow status if current_user_id provided
            if current_user_uuid:
                is_following = UserFollowers.objects.filter(
                    follower_id__user_id=current_user_uuid,
                    followed_id__user_id=user.user_id
                ).exists()
                user_data['is_following'] = is_following
            else:
                user_data['is_following'] = False
            
            users_data.append(user_data)
        
        return {
            'users': users_data,
            'total_count': total_count,
            'query': query
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
            likes_count=Count('reactions')
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
                    'user_name': comment.user.user_name,
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
        
        posts = Post.objects.select_related('user').prefetch_related('media').annotate(
            likes_count=Count('reactions', filter=Q(reactions__post__isnull=False)),
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
                'user': {
                    'user_id': str(post.user.user_id),
                    'user_name': post.user.user_name,
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
            likes_count=Count('reactions', filter=Q(reactions__post__isnull=False)),
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
            likes_count=Count('reactions')
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
        promotions = Promotion.objects.select_related('media').prefetch_related('promotion_images').order_by('-created_at')
        
        promotions_data = []
        for promotion in promotions:
            media_data = None
            if promotion.media:
                media_data = {
                    'media_id': str(promotion.media.media_id),
                    'media_type': promotion.media.media_type,
                    'url': promotion.media.url
                }
            
            images_data = []
            for image in promotion.promotion_images.all():
                images_data.append({
                    'promotion_image_id': str(image.promotion_image_id),
                    'image_url': image.image_url,
                    'image_type': image.image_type,
                    'order': image.order
                })
            
            promotions_data.append({
                'promotion_id': str(promotion.promotion_id),
                'title': promotion.title,
                'description': promotion.description,
                'price': str(promotion.price),
                'redirect_link': promotion.redirect_link,
                'meta_data': promotion.meta_data or {},
                'media': media_data,
                'images': images_data,
                'created_at': promotion.created_at.isoformat(),
                'updated_at': promotion.updated_at.isoformat()
            })
        
        return promotions_data
    
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
    
    def get_all_prayer_requests(self, limit: int = 10, offset: int = 0) -> dict:
        total_count = PrayerRequest.objects.count()
        
        prayer_requests = PrayerRequest.objects.select_related('user').annotate(
            comments_count=Count('comments'),
            reactions_count=Count('reactions')
        ).order_by('-created_at')[offset:offset + limit]
        
        prayer_requests_data = []
        for prayer_request in prayer_requests:
            prayer_requests_data.append({
                'prayer_request_id': str(prayer_request.prayer_request_id),
                'user': {
                    'user_id': str(prayer_request.user.user_id),
                    'user_name': prayer_request.user.user_name,
                    'profile_picture_url': prayer_request.user.profile_picture_url or ''
                },
                'name': prayer_request.name,
                'email': prayer_request.email,
                'phone_number': prayer_request.phone_number,
                'description': prayer_request.description,
                'comments_count': prayer_request.comments_count,
                'reactions_count': prayer_request.reactions_count,
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
            likes_count=Count('reactions')
        ).order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'comment_id': str(comment.comment_id),
                'user': {
                    'user_id': str(comment.user.user_id),
                    'user_name': comment.user.user_name,
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
    
    def get_verse(self):
        try:
            verse = Verse.objects.order_by('-created_at').first()
            
            if not verse:
                return None
            
            return {
                'verse_id': str(verse.verse_id),
                'title': verse.title or 'Quote of the day',
                'description': verse.description or '',
                'created_at': verse.created_at.isoformat(),
                'updated_at': verse.updated_at.isoformat()
            }
        except Exception:
            return None
    
    def clear_all_verses(self) -> int:
        count = Verse.objects.count()
        Verse.objects.all().delete()
        return count
    
    def create_verse(self, title: str, description: str) -> Verse:
        verse = Verse.objects.create(
            title=title.strip() if title else 'Quote of the day',
            description=description.strip()
        )
        return verse
    
    def create_promotion(self, title: str, description: str, price, redirect_link: str, meta_data: dict = None, media_id: str = None) -> Promotion:
        media = None
        if media_id:
            try:
                media_uuid = uuid.UUID(media_id) if isinstance(media_id, str) else media_id
                media = Media.objects.get(media_id=media_uuid)
            except Media.DoesNotExist:
                raise Exception("Media not found")
        
        promotion = Promotion.objects.create(
            title=title.strip(),
            description=description.strip() if description else '',
            price=price,
            redirect_link=redirect_link.strip(),
            meta_data=meta_data,
            media=media
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