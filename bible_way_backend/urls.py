"""
URL configuration for bible_way_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
