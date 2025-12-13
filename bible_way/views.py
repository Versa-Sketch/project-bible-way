from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from bible_way.interactors.singup_interactor import SignupInteractor
from bible_way.presenters.singup_response import SignupResponse
from bible_way.interactors.login_interactor import LoginInteractor
from bible_way.presenters.login_response import LoginResponse
from bible_way.interactors.google_auth_interactor import GoogleAuthInteractor
from bible_way.interactors.google_login_interactor import GoogleLoginInteractor
from bible_way.presenters.google_auth_response import GoogleAuthResponse
from bible_way.interactors.user_profile_interactor import UserProfileInteractor
from bible_way.interactors.current_user_profile_interactor import CurrentUserProfileInteractor
from bible_way.interactors.follow_user_interactor import FollowUserInteractor
from bible_way.interactors.unfollow_user_interactor import UnfollowUserInteractor
from bible_way.interactors.create_post_interactor import CreatePostInteractor
from bible_way.interactors.update_post_interactor import UpdatePostInteractor
from bible_way.interactors.delete_post_interactor import DeletePostInteractor
from bible_way.interactors.create_comment_interactor import CreateCommentInteractor
from bible_way.interactors.get_comments_interactor import GetCommentsInteractor
from bible_way.interactors.update_comment_interactor import UpdateCommentInteractor
from bible_way.interactors.delete_comment_interactor import DeleteCommentInteractor
from bible_way.interactors.like_post_interactor import LikePostInteractor
from bible_way.interactors.unlike_post_interactor import UnlikePostInteractor
from bible_way.interactors.like_comment_interactor import LikeCommentInteractor
from bible_way.interactors.unlike_comment_interactor import UnlikeCommentInteractor
from bible_way.presenters.user_profile_response import UserProfileResponse
from bible_way.presenters.follow_user_response import FollowUserResponse
from bible_way.presenters.unfollow_user_response import UnfollowUserResponse
from bible_way.presenters.create_post_response import CreatePostResponse
from bible_way.presenters.update_post_response import UpdatePostResponse
from bible_way.presenters.delete_post_response import DeletePostResponse
from bible_way.presenters.create_comment_response import CreateCommentResponse
from bible_way.presenters.get_comments_response import GetCommentsResponse
from bible_way.presenters.update_comment_response import UpdateCommentResponse
from bible_way.presenters.delete_comment_response import DeleteCommentResponse
from bible_way.presenters.like_post_response import LikePostResponse
from bible_way.presenters.unlike_post_response import UnlikePostResponse
from bible_way.presenters.like_comment_response import LikeCommentResponse
from bible_way.presenters.unlike_comment_response import UnlikeCommentResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from bible_way.storage import UserDB

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup_view(request):
    user_name = request.data.get('user_name')
    email = request.data.get('email')
    password = request.data.get('password')
    country = request.data.get('country')
    age = request.data.get('age')
    preferred_language = request.data.get('preferred_language') or request.data.get('Preferred_language')
    confirm_password = request.data.get('confirm_password')
    profile_picture_url = request.data.get('profile_picture_url')
    response =SignupInteractor(storage=UserDB(), response=SignupResponse(), authentication=UserAuthentication()).\
        signup_interactor(user_name=user_name, email=email, password=password, country=country, age=age, preferred_language=preferred_language, confirm_password=confirm_password, profile_picture_url=profile_picture_url)
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    response = LoginInteractor(storage=UserDB(), response=LoginResponse(), authentication=UserAuthentication()).\
        login_interactor(email=email, password=password)
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def google_signup_view(request):
    token = request.data.get('token')
    country = request.data.get('country')
    age = request.data.get('age')
    preferred_language = request.data.get('preferred_language')
    response = GoogleAuthInteractor(storage=UserDB(), response=GoogleAuthResponse(), authentication=UserAuthentication()).\
        google_signup_interactor(
            token=token, 
            country=country, 
            age=age, 
            preferred_language=preferred_language
        )
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def google_login_view(request):
    token = request.data.get('token') 
    
    response = GoogleLoginInteractor(
        storage=UserDB(), 
        response=GoogleAuthResponse(), 
        authentication=UserAuthentication()
    ).google_login_interactor(token=token) # Pass token only
    return response

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_user_profile_view(request, user_name):
    response = UserProfileInteractor(storage=UserDB(), response=UserProfileResponse()).\
        get_user_profile_interactor(user_name=user_name)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user_profile_view(request):
    user_id = str(request.user.user_id)
    response = CurrentUserProfileInteractor(storage=UserDB(), response=UserProfileResponse()).\
        get_current_user_profile_interactor(user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def follow_user_view(request):
    follower_id = str(request.user.user_id)
    followed_id = request.data.get('followed_id')
    
    if not followed_id:
        return FollowUserResponse().user_not_found_response()
    
    response = FollowUserInteractor(storage=UserDB(), response=FollowUserResponse()).\
        follow_user_interactor(follower_id=follower_id, followed_id=followed_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def unfollow_user_view(request):
    follower_id = str(request.user.user_id)
    followed_id = request.data.get('followed_id')
    
    if not followed_id:
        return UnfollowUserResponse().user_not_found_response()
    
    response = UnfollowUserInteractor(storage=UserDB(), response=UnfollowUserResponse()).\
        unfollow_user_interactor(follower_id=follower_id, followed_id=followed_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_post_view(request):
    user_id = str(request.user.user_id)
    title = request.data.get('title', '')
    description = request.data.get('description', '')
    
    media_files = request.FILES.getlist('media')
    
    response = CreatePostInteractor(storage=UserDB(), response=CreatePostResponse()).\
        create_post_interactor(user_id=user_id, title=title, description=description, media_files=media_files)
    return response

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_post_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id')
    title = request.data.get('title')
    description = request.data.get('description')
    
    if not post_id:
        return UpdatePostResponse().validation_error_response("post_id is required in request body")
    
    response = UpdatePostInteractor(storage=UserDB(), response=UpdatePostResponse()).\
        update_post_interactor(post_id=post_id, user_id=user_id, title=title, description=description)
    return response

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_post_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id')
    
    if not post_id:
        return DeletePostResponse().error_response("post_id is required in request body")
    
    response = DeletePostInteractor(storage=UserDB(), response=DeletePostResponse()).\
        delete_post_interactor(post_id=post_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_comment_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id')
    description = request.data.get('description')
    
    response = CreateCommentInteractor(storage=UserDB(), response=CreateCommentResponse()).\
        create_comment_interactor(post_id=post_id, user_id=user_id, description=description)
    return response

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_comments_view(request):
    post_id = request.query_params.get('post_id')
    user_id = str(request.user.user_id)
    
    response = GetCommentsInteractor(storage=UserDB(), response=GetCommentsResponse()).\
        get_comments_interactor(post_id=post_id, user_id=user_id)
    return response

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_comment_view(request):
    user_id = str(request.user.user_id)
    comment_id = request.data.get('comment_id')
    description = request.data.get('description')
    
    response = UpdateCommentInteractor(storage=UserDB(), response=UpdateCommentResponse()).\
        update_comment_interactor(comment_id=comment_id, user_id=user_id, description=description)
    return response

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_comment_view(request):
    user_id = str(request.user.user_id)
    comment_id = request.data.get('comment_id')
    
    response = DeleteCommentInteractor(storage=UserDB(), response=DeleteCommentResponse()).\
        delete_comment_interactor(comment_id=comment_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_post_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id')
    
    response = LikePostInteractor(storage=UserDB(), response=LikePostResponse()).\
        like_post_interactor(post_id=post_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def unlike_post_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id')
    
    response = UnlikePostInteractor(storage=UserDB(), response=UnlikePostResponse()).\
        unlike_post_interactor(post_id=post_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_comment_view(request):
    user_id = str(request.user.user_id)
    comment_id = request.data.get('comment_id')
    
    response = LikeCommentInteractor(storage=UserDB(), response=LikeCommentResponse()).\
        like_comment_interactor(comment_id=comment_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def unlike_comment_view(request):
    user_id = str(request.user.user_id)
    comment_id = request.data.get('comment_id')
    
    response = UnlikeCommentInteractor(storage=UserDB(), response=UnlikeCommentResponse()).\
        unlike_comment_interactor(comment_id=comment_id, user_id=user_id)
    return response
