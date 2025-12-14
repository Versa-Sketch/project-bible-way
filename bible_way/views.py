from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from bible_way.interactors.singup_interactor import SignupInteractor
from bible_way.presenters.singup_response import SignupResponse
from bible_way.interactors.login_interactor import LoginInteractor
from bible_way.presenters.login_response import LoginResponse
from bible_way.interactors.google_authentication_interactor import GoogleAuthenticationInteractor
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
from bible_way.interactors.get_all_posts_interactor import GetAllPostsInteractor
from bible_way.interactors.get_user_posts_interactor import GetUserPostsInteractor
from bible_way.interactors.get_user_comments_interactor import GetUserCommentsInteractor
from bible_way.interactors.get_promotions_interactor import GetPromotionsInteractor
from bible_way.interactors.create_prayer_request_interactor import CreatePrayerRequestInteractor
from bible_way.interactors.update_prayer_request_interactor import UpdatePrayerRequestInteractor
from bible_way.interactors.delete_prayer_request_interactor import DeletePrayerRequestInteractor
from bible_way.interactors.get_all_prayer_requests_interactor import GetAllPrayerRequestsInteractor
from bible_way.interactors.create_prayer_request_comment_interactor import CreatePrayerRequestCommentInteractor
from bible_way.interactors.get_prayer_request_comments_interactor import GetPrayerRequestCommentsInteractor
from bible_way.interactors.like_prayer_request_interactor import LikePrayerRequestInteractor
from bible_way.interactors.unlike_prayer_request_interactor import UnlikePrayerRequestInteractor
from bible_way.interactors.get_verse_interactor import GetVerseInteractor
from bible_way.interactors.admin.create_verse_interactor import CreateVerseInteractor
from bible_way.interactors.admin.create_promotion_interactor import CreatePromotionInteractor
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
from bible_way.presenters.get_all_posts_response import GetAllPostsResponse
from bible_way.presenters.get_user_posts_response import GetUserPostsResponse
from bible_way.presenters.get_user_comments_response import GetUserCommentsResponse
from bible_way.presenters.get_promotions_response import GetPromotionsResponse
from bible_way.presenters.create_prayer_request_response import CreatePrayerRequestResponse
from bible_way.presenters.update_prayer_request_response import UpdatePrayerRequestResponse
from bible_way.presenters.delete_prayer_request_response import DeletePrayerRequestResponse
from bible_way.presenters.get_all_prayer_requests_response import GetAllPrayerRequestsResponse
from bible_way.presenters.create_prayer_request_comment_response import CreatePrayerRequestCommentResponse
from bible_way.presenters.get_prayer_request_comments_response import GetPrayerRequestCommentsResponse
from bible_way.presenters.like_prayer_request_response import LikePrayerRequestResponse
from bible_way.presenters.unlike_prayer_request_response import UnlikePrayerRequestResponse
from bible_way.presenters.get_verse_response import GetVerseResponse
from bible_way.presenters.admin.create_verse_response import CreateVerseResponse
from bible_way.presenters.admin.create_promotion_response import CreatePromotionResponse
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
def google_authentication_view(request):
    token = request.data.get('token')
    age = request.data.get('age')
    preferred_language = request.data.get('preferred_language')
    country = request.data.get('country')
    
    try:
        if age is not None:
            age = int(age)
    except (ValueError, TypeError):
        age = None
    
    response = GoogleAuthenticationInteractor(
        storage=UserDB(), 
        response=GoogleAuthResponse(), 
        authentication=UserAuthentication()
    ).google_authentication_interactor(
        token=token,
        age=age,
        preferred_language=preferred_language,
        country=country
    )
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

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_posts_view(request):
    current_user_id = str(request.user.user_id)
    limit = request.query_params.get('limit', '10')
    offset = request.query_params.get('offset', '0')
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
    
    try:
        offset = int(offset)
    except (ValueError, TypeError):
        offset = 0
    
    response = GetAllPostsInteractor(storage=UserDB(), response=GetAllPostsResponse()).\
        get_all_posts_interactor(limit=limit, offset=offset, current_user_id=current_user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_posts_view(request):
    user_id = str(request.user.user_id)
    current_user_id = str(request.user.user_id)
    limit = request.query_params.get('limit', '10')
    offset = request.query_params.get('offset', '0')
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
    
    try:
        offset = int(offset)
    except (ValueError, TypeError):
        offset = 0
    
    response = GetUserPostsInteractor(storage=UserDB(), response=GetUserPostsResponse()).\
        get_user_posts_interactor(user_id=user_id, limit=limit, offset=offset, current_user_id=current_user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_comments_view(request):
    user_id = str(request.user.user_id)
    
    response = GetUserCommentsInteractor(storage=UserDB(), response=GetUserCommentsResponse()).\
        get_user_comments_interactor(user_id=user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_promotions_view(request):
    response = GetPromotionsInteractor(storage=UserDB(), response=GetPromotionsResponse()).\
        get_all_promotions_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_prayer_request_view(request):
    user_id = str(request.user.user_id)
    name = request.data.get('name')
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    description = request.data.get('description')
    
    response = CreatePrayerRequestInteractor(storage=UserDB(), response=CreatePrayerRequestResponse()).\
        create_prayer_request_interactor(user_id=user_id, name=name, email=email, description=description, phone_number=phone_number)
    return response

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_prayer_request_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    name = request.data.get('name')
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')
    description = request.data.get('description')
    
    response = UpdatePrayerRequestInteractor(storage=UserDB(), response=UpdatePrayerRequestResponse()).\
        update_prayer_request_interactor(
            prayer_request_id=prayer_request_id,
            user_id=user_id,
            name=name,
            email=email,
            phone_number=phone_number,
            description=description
        )
    return response

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_prayer_request_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    
    response = DeletePrayerRequestInteractor(storage=UserDB(), response=DeletePrayerRequestResponse()).\
        delete_prayer_request_interactor(prayer_request_id=prayer_request_id, user_id=user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_prayer_requests_view(request):
    limit = request.query_params.get('limit', 10)
    offset = request.query_params.get('offset', 0)
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
    
    try:
        offset = int(offset)
    except (ValueError, TypeError):
        offset = 0
    
    response = GetAllPrayerRequestsInteractor(storage=UserDB(), response=GetAllPrayerRequestsResponse()).\
        get_all_prayer_requests_interactor(limit=limit, offset=offset)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_prayer_request_comment_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    description = request.data.get('description')
    
    response = CreatePrayerRequestCommentInteractor(storage=UserDB(), response=CreatePrayerRequestCommentResponse()).\
        create_prayer_request_comment_interactor(
            prayer_request_id=prayer_request_id,
            user_id=user_id,
            description=description
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_prayer_request_comments_view(request, prayer_request_id):
    response = GetPrayerRequestCommentsInteractor(storage=UserDB(), response=GetPrayerRequestCommentsResponse()).\
        get_prayer_request_comments_interactor(prayer_request_id=prayer_request_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_prayer_request_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    
    response = LikePrayerRequestInteractor(storage=UserDB(), response=LikePrayerRequestResponse()).\
        like_prayer_request_interactor(prayer_request_id=prayer_request_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def unlike_prayer_request_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    
    response = UnlikePrayerRequestInteractor(storage=UserDB(), response=UnlikePrayerRequestResponse()).\
        unlike_prayer_request_interactor(prayer_request_id=prayer_request_id, user_id=user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_verse_view(request):
    response = GetVerseInteractor(storage=UserDB(), response=GetVerseResponse()).\
        get_verse_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_verse_view(request):
    title = request.data.get('title')
    description = request.data.get('description')
    
    response = CreateVerseInteractor(storage=UserDB(), response=CreateVerseResponse()).\
        create_verse_interactor(title=title, description=description)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_promotion_view(request):
    title = request.data.get('title')
    description = request.data.get('description')
    price = request.data.get('price')
    redirect_link = request.data.get('redirect_link')
    meta_data = request.data.get('meta_data')
    media_file = request.FILES.get('media')
    image_files = request.FILES.getlist('images')
    
    response = CreatePromotionInteractor(storage=UserDB(), response=CreatePromotionResponse()).\
        create_promotion_interactor(
            title=title,
            description=description,
            price=price,
            redirect_link=redirect_link,
            meta_data_str=meta_data,
            media_file=media_file,
            image_files=image_files
        )
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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_comments_view(request, post_id):
    current_user_id = str(request.user.user_id)
    response = GetCommentsInteractor(storage=UserDB(), response=GetCommentsResponse()).\
        get_comments_interactor(post_id=post_id, current_user_id=current_user_id)
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
