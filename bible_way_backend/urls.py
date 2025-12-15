from django.contrib import admin
from django.urls import path, include
from bible_way.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/signup", signup_view),
    path("user/login", login_view),
    path("user/google/authentication", google_authentication_view),
    path("user/profile/me", get_current_user_profile_view),
    path("user/profile/<str:user_name>", get_user_profile_view),
    path("user/search", search_users_view),
    path("user/follow", follow_user_view),
    path("user/unfollow", unfollow_user_view),
    path("post/create", create_post_view),
    path("post/all", get_all_posts_view),
    path("post/user/me", get_user_posts_view),
    path("post/update", update_post_view),
    path("post/delete", delete_post_view),
    path("comment/create", create_comment_view),
    path("comment/details/<str:post_id>/v1", get_comments_view),
    path("comment/user/me", get_user_comments_view),
    path("comment/update", update_comment_view),
    path("comment/delete", delete_comment_view),
    path("reaction/post/like", like_post_view),
    path("reaction/post/unlike", unlike_post_view),
    path("reaction/comment/like", like_comment_view),
    path("reaction/comment/unlike", unlike_comment_view),
    path("promotion/all", get_all_promotions_view),
    path("prayer-request/create", create_prayer_request_view),
    path("prayer-request/update", update_prayer_request_view),
    path("prayer-request/delete", delete_prayer_request_view),
    path("prayer-request/all", get_all_prayer_requests_view),
    path("prayer-request/user/me", get_user_prayer_requests_view),
    path("prayer-request/comment/create", create_prayer_request_comment_view),
    path("prayer-request/comment/details/<str:prayer_request_id>/v1", get_prayer_request_comments_view),
    path("prayer-request/reaction/like", like_prayer_request_view),
    path("prayer-request/reaction/unlike", unlike_prayer_request_view),
    path("verse/daily", get_verse_view),

    ################# admin side api's ################ 
    path("admin/verse/create", admin_create_verse_view),
    path("admin/promotion/create", admin_create_promotion_view),
    path("admin/category/create", admin_create_category_view),
    path("admin/age-group/create", admin_create_age_group_view),
    path("admin/book/create", admin_create_book_view),
    
    ################# books api's ################
    path("books/categories/", get_categories_view),
    path("books/age-groups/", get_age_groups_view),
    path("books/category/<str:category_id>/age-group/<str:age_group_id>/books/", get_books_by_category_view),
    path("books/<str:book_id>/", get_book_details_view),

    ####project chat api's ###############
    path('', include('project_chat.urls')),
    
    ####project notifications api's ###############
    path('api/notifications/', include('project_notifications.urls')),
]
