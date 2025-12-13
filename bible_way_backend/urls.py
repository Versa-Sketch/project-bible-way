from django.contrib import admin
from django.urls import path
from bible_way.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/signup", signup_view),
    path("user/login", login_view),
    path("user/google/signup", google_signup_view),
    path("user/google/login", google_login_view),
    path("user/profile/me", get_current_user_profile_view),
    path("user/profile/<str:user_name>", get_user_profile_view),
    path("user/follow", follow_user_view),
    path("user/unfollow", unfollow_user_view),
    path("post/create", create_post_view),
    path("post/update", update_post_view),
    path("post/delete", delete_post_view),
    path("comment/create", create_comment_view),
    path("comment/post", get_comments_view),
    path("comment/update", update_comment_view),
    path("comment/delete", delete_comment_view),
    path("reaction/post/like", like_post_view),
    path("reaction/post/unlike", unlike_post_view),
    path("reaction/comment/like", like_comment_view),
    path("reaction/comment/unlike", unlike_comment_view),
]
