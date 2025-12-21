from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from bible_way.views import *

urlpatterns = [
    # ==================== Authentication APIs ====================
    path("user/signup", signup_view),
    path("user/login", login_view),
    path("user/logout", logout_view),
    path("user/google/authentication", google_authentication_view),
    path("user/verify-email", verify_email_view),
    path("user/resend-verification-email", resend_verification_email_view),
    path("user/forgot-password", forgot_password_view),
    path("user/otp-verify-reset-password", reset_password_view),
    
    # ==================== User Profile APIs ====================
    path("user/profile/me", get_current_user_profile_view),
    path("user/profile/complete", get_complete_user_profile_view),
    path("user/profile/update", update_profile_view),
    path("user/profile/<str:user_name>", get_user_profile_view),
    
    # ==================== User Search & Discovery APIs ====================
    path("user/search", search_users_view),
    path("user/recommended", get_recommended_users_view),
    
    # ==================== User Follow APIs ====================
    path("user/follow", follow_user_view),
    path("user/unfollow", unfollow_user_view),
    path("user/following", get_user_following_view),
    path("user/followers", get_user_followers_view),
    
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
    
    # ==================== Wallpaper APIs ====================
    path("wallpapers/all", get_all_wallpapers_view),
    
    # ==================== Sticker APIs ====================
    path("stickers/all", get_all_stickers_view),
    
    # ==================== Testimonial APIs ====================
    path("testimonial/create", create_testimonial_view),
    path("testimonials/all", get_testimonials_view),
    path("testimonial/user/me", get_user_testimonials_view),
    
    # ==================== Verse APIs ====================
    path("verse/daily", get_verse_view),
    path("verse/all", get_all_verses_view),
    path("verse/like", like_verse_view),
    path("verse/unlike", unlike_verse_view),
    
    # ==================== Books APIs ====================
    path("books/categories/", get_categories_view),
    path("books/age-groups/", get_age_groups_view),
    path("books/get", get_books_by_category_and_age_group_view),
    path("books/", get_books_by_category_and_age_group_get_view),
    path("books/all", get_all_books_view),
    path("books/chapters/get", get_book_chapters_view),
    path("books/details", get_book_details_view),
    path("books/search", search_chapters_view),
    path("books/segregate-bibles/latest-chapters-by-age-group", get_latest_segregate_bibles_chapters_by_age_group_view),
    
    # ==================== Language APIs ====================
    path("languages/all", get_all_languages_view),
    
    # ==================== Audio/TTS APIs ====================
    path("audio/text-to-speech", generate_text_to_speech_view),
    
    # ==================== Highlight APIs ====================
    path("highlight/create", create_highlight_view),
    path("highlight/book/<str:book_id>", get_highlights_view),
    path("highlight/delete", delete_highlight_view),
    
    # ==================== Reading Note APIs ====================
    path("reading-note/create", create_reading_note_view),
    path("reading-note/book/<str:book_id>", get_reading_notes_view),
    path("reading-note/update", update_reading_note_view),
    path("reading-note/delete", delete_reading_note_view),
    
    # ==================== Bookmark APIs ====================
    path("bookmark/toggle", toggle_bookmark_view),
    path("bookmark/all", get_bookmarks_view),
    
    # ==================== Reading Progress APIs ====================
    path("reading-progress/create", create_reading_progress_view),
    path("reading-progress/get", get_reading_progress_view),
    path("reading-progress/top-books", get_top_books_reading_progress_view),
    
    # ==================== Share Link APIs ====================
    path("share/post/create", create_post_share_link_view),
    path("share/profile/create", create_profile_share_link_view),
    
    # ==================== Short Share URLs ====================
    path("s/p/<str:token>", get_shared_post_view),  
    path("s/u/<str:token>", get_shared_profile_view),  
    
    # ==================== Admin APIs ====================
    # IMPORTANT: These must come BEFORE Django admin to avoid conflicts
    path("admin/verse/create", admin_create_verse_view),
    path("admin/verse/update", admin_update_verse_view),
    path("admin/verse/delete", admin_delete_verse_view),
    path("admin/promotion/create", admin_create_promotion_view),
    path("admin/category/create", admin_create_category_view),
    path("admin/category/update", admin_update_category_view),
    path("admin/categories", admin_get_categories_view),
    path("admin/age-group/create", admin_create_age_group_view),
    path("admin/age-group/update", admin_update_age_group_view),
    path("admin/age-groups", admin_get_age_groups_view),
    path("admin/languages", admin_get_languages_view),
    path("admin/book/create", admin_create_book_view),
    path("admin/book/update", admin_update_book_view),
    path("admin/book/chapters/create", admin_create_chapters_view),
    path("admin/book/chapter/delete", delete_chapter_view),
    path("admin/testimonials", admin_get_testimonials_view),
    path("admin/testimonial/approve", admin_approve_testimonial_view),
    path("admin/testimonial/reject", admin_reject_testimonial_view),
    
    # ==================== Django Admin (must be after custom admin APIs) ====================
    path("admin/", admin.site.urls),
    
    # ==================== Chat APIs ====================
    path('api/chat/', include('project_chat.urls')),
    
    # ==================== Notification APIs ====================
    path('api/notifications/', include('project_notifications.urls')),
]
