from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from bible_way.views import *

urlpatterns = [
    # ==================== Authentication APIs ====================
    path("user/signup", signup_view),
    path("user/login", login_view),
    path("user/google/authentication", google_authentication_view),
    
    # ==================== User Profile APIs ====================
    path("user/profile/me", get_current_user_profile_view),
    path("user/profile/complete", get_complete_user_profile_view),
    path("user/profile/<str:user_name>", get_user_profile_view),
    
    # ==================== User Search & Discovery APIs ====================
    path("user/search", search_users_view),
    path("user/recommended", get_recommended_users_view),
    
    # ==================== User Follow APIs ====================
    path("user/follow", follow_user_view),
    path("user/unfollow", unfollow_user_view),
    
    # ==================== Post APIs ====================
    path("post/create", create_post_view),
    path("post/all", get_all_posts_view),
    path("post/user/me", get_user_posts_view),
    path("post/user", get_specific_user_posts_view),
    path("post/update", update_post_view),
    path("post/delete", delete_post_view),
    
    # ==================== Comment APIs ====================
    path("comment/create", create_comment_view),
    path("comment/details/<str:post_id>/v1", get_comments_view),
    path("comment/user/me", get_user_comments_view),
    path("comment/update", update_comment_view),
    path("comment/delete", delete_comment_view),
    
    # ==================== Reaction APIs ====================
    path("reaction/post/like", like_post_view),
    path("reaction/post/unlike", unlike_post_view),
    path("reaction/comment/like", like_comment_view),
    path("reaction/comment/unlike", unlike_comment_view),
    
    # ==================== Prayer Request APIs ====================
    path("prayer-request/create", create_prayer_request_view),
    path("prayer-request/update", update_prayer_request_view),
    path("prayer-request/delete", delete_prayer_request_view),
    path("prayer-request/all", get_all_prayer_requests_view),
    path("prayer-request/user/me", get_user_prayer_requests_view),
    path("prayer-request/user", get_specific_user_prayer_requests_view),
    path("prayer-request/comment/create", create_prayer_request_comment_view),
    path("prayer-request/comment/details/<str:prayer_request_id>/v1", get_prayer_request_comments_view),
    path("prayer-request/reaction/like", like_prayer_request_view),
    path("prayer-request/reaction/unlike", unlike_prayer_request_view),
    
    # ==================== Promotion APIs ====================
    path("promotion/all", get_all_promotions_view),
    
    # ==================== Verse APIs ====================
    path("verse/daily", get_verse_view),
    path("verse/all", get_all_verses_view),
    
    # ==================== Books APIs ====================
    path("books/categories/", get_categories_view),
    path("books/age-groups/", get_age_groups_view),
    path("books/category/<str:category_id>/age-group/<str:age_group_id>/books/", get_books_by_category_view),
    
    # ==================== Highlight APIs ====================
    path("highlight/create", create_highlight_view),
    path("highlight/book/<str:book_id>", get_highlights_view),
    path("highlight/delete", delete_highlight_view),
    
    # ==================== Admin APIs ====================
    path("admin/verse/create", admin_create_verse_view),
    path("admin/promotion/create", admin_create_promotion_view),
    path("admin/category/create", admin_create_category_view),
    path("admin/categories", admin_get_categories_view),
    path("admin/age-group/create", admin_create_age_group_view),
    path("admin/age-groups", admin_get_age_groups_view),
    path("admin/languages", admin_get_languages_view),
    path("admin/book/create", admin_create_book_view),
    path("admin/book/update-metadata", admin_update_book_metadata_view),
    path("admin/books", admin_get_all_books_view),
    
    # ==================== Chat APIs ====================
    path('', include('project_chat.urls')),
    
    # ==================== Notification APIs ====================
    path('', include('project_notifications.urls')),
]
