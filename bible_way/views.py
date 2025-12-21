from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from bible_way.interactors.singup_interactor import SignupInteractor
from bible_way.presenters.singup_response import SignupResponse
from bible_way.interactors.login_interactor import LoginInteractor
from bible_way.presenters.login_response import LoginResponse
from bible_way.interactors.logout_interactor import LogoutInteractor
from bible_way.presenters.logout_response import LogoutResponse
from bible_way.interactors.verify_email_interactor import VerifyEmailInteractor
from bible_way.presenters.verify_email_response import VerifyEmailResponse
from bible_way.interactors.resend_verification_email_interactor import ResendVerificationEmailInteractor
from bible_way.presenters.resend_verification_email_response import ResendVerificationEmailResponse
from bible_way.interactors.google_authentication_interactor import GoogleAuthenticationInteractor
from bible_way.presenters.google_auth_response import GoogleAuthResponse
from bible_way.interactors.user_profile_interactor import UserProfileInteractor
from bible_way.interactors.current_user_profile_interactor import CurrentUserProfileInteractor
from bible_way.interactors.search_users_interactor import SearchUsersInteractor
from bible_way.interactors.get_recommended_users_interactor import GetRecommendedUsersInteractor
from bible_way.interactors.get_complete_user_profile_interactor import GetCompleteUserProfileInteractor
from bible_way.interactors.update_profile_interactor import UpdateProfileInteractor
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
from bible_way.interactors.get_specific_user_posts_interactor import GetSpecificUserPostsInteractor
from bible_way.interactors.get_user_comments_interactor import GetUserCommentsInteractor
from bible_way.interactors.get_promotions_interactor import GetPromotionsInteractor
from bible_way.interactors.get_wallpapers_interactor import GetWallpapersInteractor
from bible_way.interactors.get_stickers_interactor import GetStickersInteractor
from bible_way.interactors.create_testimonial_interactor import CreateTestimonialInteractor
from bible_way.interactors.get_testimonials_interactor import GetTestimonialsInteractor
from bible_way.interactors.get_user_testimonials_interactor import GetUserTestimonialsInteractor
from bible_way.interactors.admin.get_testimonials_interactor import AdminGetTestimonialsInteractor
from bible_way.interactors.admin.approve_testimonial_interactor import AdminApproveTestimonialInteractor
from bible_way.interactors.admin.reject_testimonial_interactor import AdminRejectTestimonialInteractor
from bible_way.interactors.create_prayer_request_interactor import CreatePrayerRequestInteractor
from bible_way.interactors.update_prayer_request_interactor import UpdatePrayerRequestInteractor
from bible_way.interactors.delete_prayer_request_interactor import DeletePrayerRequestInteractor
from bible_way.interactors.get_all_prayer_requests_interactor import GetAllPrayerRequestsInteractor
from bible_way.interactors.get_user_prayer_requests_interactor import GetUserPrayerRequestsInteractor
from bible_way.interactors.get_specific_user_prayer_requests_interactor import GetSpecificUserPrayerRequestsInteractor
from bible_way.interactors.create_prayer_request_comment_interactor import CreatePrayerRequestCommentInteractor
from bible_way.interactors.get_prayer_request_comments_interactor import GetPrayerRequestCommentsInteractor
from bible_way.interactors.like_prayer_request_interactor import LikePrayerRequestInteractor
from bible_way.interactors.unlike_prayer_request_interactor import UnlikePrayerRequestInteractor
from bible_way.interactors.like_verse_interactor import LikeVerseInteractor
from bible_way.interactors.unlike_verse_interactor import UnlikeVerseInteractor
from bible_way.interactors.get_verse_interactor import GetVerseInteractor
from bible_way.interactors.get_all_verses_interactor import GetAllVersesInteractor
from bible_way.interactors.admin.create_verse_interactor import CreateVerseInteractor
from bible_way.interactors.admin.create_promotion_interactor import CreatePromotionInteractor
from bible_way.interactors.admin.create_category_interactor import CreateCategoryInteractor
from bible_way.interactors.get_categories_interactor import GetCategoriesInteractor
from bible_way.interactors.admin.get_categories_interactor import GetCategoriesInteractor as AdminGetCategoriesInteractor
from bible_way.interactors.admin.create_age_group_interactor import CreateAgeGroupInteractor
from bible_way.interactors.get_age_groups_interactor import GetAgeGroupsInteractor
from bible_way.interactors.admin.get_age_groups_interactor import GetAgeGroupsInteractor as AdminGetAgeGroupsInteractor
from bible_way.interactors.admin.get_languages_interactor import GetLanguagesInteractor
from bible_way.interactors.admin.create_book_interactor import CreateBookInteractor
from bible_way.interactors.admin.create_chapters_interactor import CreateChaptersInteractor
from bible_way.interactors.get_all_books_interactor import GetAllBooksInteractor
from bible_way.interactors.get_books_by_category_and_age_group_interactor import GetBooksByCategoryAndAgeGroupInteractor
from bible_way.interactors.get_book_chapters_interactor import GetBookChaptersInteractor
from bible_way.interactors.search_chapters_interactor import SearchChaptersInteractor
from bible_way.presenters.user_profile_response import UserProfileResponse
from bible_way.presenters.search_users_response import SearchUsersResponse
from bible_way.presenters.get_recommended_users_response import GetRecommendedUsersResponse
from bible_way.presenters.get_complete_user_profile_response import GetCompleteUserProfileResponse
from bible_way.presenters.update_profile_response import UpdateProfileResponse
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
from bible_way.presenters.get_specific_user_posts_response import GetSpecificUserPostsResponse
from bible_way.presenters.get_user_comments_response import GetUserCommentsResponse
from bible_way.presenters.get_promotions_response import GetPromotionsResponse
from bible_way.presenters.get_wallpapers_response import GetWallpapersResponse
from bible_way.presenters.get_stickers_response import GetStickersResponse
from bible_way.presenters.create_testimonial_response import CreateTestimonialResponse
from bible_way.presenters.get_testimonials_response import GetTestimonialsResponse
from bible_way.presenters.get_user_testimonials_response import GetUserTestimonialsResponse
from bible_way.presenters.admin.get_testimonials_response import AdminGetTestimonialsResponse
from bible_way.presenters.admin.approve_testimonial_response import AdminApproveTestimonialResponse
from bible_way.presenters.admin.reject_testimonial_response import AdminRejectTestimonialResponse
from bible_way.presenters.create_prayer_request_response import CreatePrayerRequestResponse
from bible_way.presenters.update_prayer_request_response import UpdatePrayerRequestResponse
from bible_way.presenters.delete_prayer_request_response import DeletePrayerRequestResponse
from bible_way.presenters.get_all_prayer_requests_response import GetAllPrayerRequestsResponse
from bible_way.presenters.get_user_prayer_requests_response import GetUserPrayerRequestsResponse
from bible_way.presenters.get_specific_user_prayer_requests_response import GetSpecificUserPrayerRequestsResponse
from bible_way.presenters.create_prayer_request_comment_response import CreatePrayerRequestCommentResponse
from bible_way.presenters.get_prayer_request_comments_response import GetPrayerRequestCommentsResponse
from bible_way.presenters.like_prayer_request_response import LikePrayerRequestResponse
from bible_way.presenters.unlike_prayer_request_response import UnlikePrayerRequestResponse
from bible_way.presenters.like_verse_response import LikeVerseResponse
from bible_way.presenters.unlike_verse_response import UnlikeVerseResponse
from bible_way.presenters.get_verse_response import GetVerseResponse
from bible_way.presenters.get_all_verses_response import GetAllVersesResponse
from bible_way.presenters.admin.create_verse_response import CreateVerseResponse
from bible_way.presenters.admin.create_promotion_response import CreatePromotionResponse
from bible_way.presenters.admin.create_category_response import CreateCategoryResponse
from bible_way.presenters.get_categories_response import GetCategoriesResponse
from bible_way.presenters.admin.get_categories_response import GetCategoriesResponse as AdminGetCategoriesResponse
from bible_way.presenters.admin.create_age_group_response import CreateAgeGroupResponse
from bible_way.presenters.get_age_groups_response import GetAgeGroupsResponse
from bible_way.presenters.admin.get_age_groups_response import GetAgeGroupsResponse as AdminGetAgeGroupsResponse
from bible_way.presenters.admin.get_languages_response import GetLanguagesResponse
from bible_way.presenters.admin.create_book_response import CreateBookResponse
from bible_way.presenters.admin.create_chapters_response import CreateChaptersResponse
from bible_way.presenters.get_all_books_response import GetAllBooksResponse
from bible_way.presenters.get_books_by_category_and_age_group_response import GetBooksByCategoryAndAgeGroupResponse
from bible_way.presenters.get_book_chapters_response import GetBookChaptersResponse
from bible_way.presenters.search_chapters_response import SearchChaptersResponse
from bible_way.interactors.create_highlight_interactor import CreateHighlightInteractor
from bible_way.interactors.get_highlights_interactor import GetHighlightsInteractor
from bible_way.interactors.delete_highlight_interactor import DeleteHighlightInteractor
from bible_way.presenters.create_highlight_response import CreateHighlightResponse
from bible_way.interactors.create_post_share_link_interactor import CreatePostShareLinkInteractor
from bible_way.interactors.create_profile_share_link_interactor import CreateProfileShareLinkInteractor
from bible_way.interactors.get_shared_post_interactor import GetSharedPostInteractor
from bible_way.interactors.get_shared_profile_interactor import GetSharedProfileInteractor
from bible_way.presenters.create_post_share_link_response import CreatePostShareLinkResponse
from bible_way.presenters.create_profile_share_link_response import CreateProfileShareLinkResponse
from bible_way.presenters.get_shared_post_response import GetSharedPostResponse
from bible_way.presenters.get_shared_profile_response import GetSharedProfileResponse
from bible_way.presenters.get_highlights_response import GetHighlightsResponse
from bible_way.presenters.delete_highlight_response import DeleteHighlightResponse
from bible_way.interactors.create_reading_note_interactor import CreateReadingNoteInteractor
from bible_way.presenters.create_reading_note_response import CreateReadingNoteResponse
from bible_way.interactors.get_reading_notes_interactor import GetReadingNotesInteractor
from bible_way.presenters.get_reading_notes_response import GetReadingNotesResponse
from bible_way.interactors.update_reading_note_interactor import UpdateReadingNoteInteractor
from bible_way.presenters.update_reading_note_response import UpdateReadingNoteResponse
from bible_way.interactors.delete_reading_note_interactor import DeleteReadingNoteInteractor
from bible_way.presenters.delete_reading_note_response import DeleteReadingNoteResponse
from bible_way.interactors.create_bookmark_interactor import CreateBookmarkInteractor
from bible_way.presenters.create_bookmark_response import CreateBookmarkResponse
from bible_way.interactors.get_bookmarks_interactor import GetBookmarksInteractor
from bible_way.presenters.get_bookmarks_response import GetBookmarksResponse
from bible_way.interactors.delete_bookmark_interactor import DeleteBookmarkInteractor
from bible_way.presenters.delete_bookmark_response import DeleteBookmarkResponse
from bible_way.interactors.toggle_bookmark_interactor import ToggleBookmarkInteractor
from bible_way.presenters.toggle_bookmark_response import ToggleBookmarkResponse
from bible_way.interactors.create_reading_progress_interactor import CreateReadingProgressInteractor
from bible_way.presenters.create_reading_progress_response import CreateReadingProgressResponse
from bible_way.interactors.get_reading_progress_interactor import GetReadingProgressInteractor
from bible_way.presenters.get_reading_progress_response import GetReadingProgressResponse
from bible_way.jwt_authentication.jwt_tokens import UserAuthentication
from bible_way.storage import UserDB
from bible_way.services.elasticsearch_service import ElasticsearchService

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
    response =SignupInteractor(storage=UserDB(), response=SignupResponse(), authentication=UserAuthentication()).\
        signup_interactor(user_name=user_name, email=email, password=password, country=country, age=age, preferred_language=preferred_language, confirm_password=confirm_password)
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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    user_id = str(request.user.user_id)
    response = LogoutInteractor(storage=UserDB(), response=LogoutResponse()).\
        logout_interactor(user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def verify_email_view(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    if not email or not otp:
        return VerifyEmailResponse().invalid_otp_response()
    
    response = VerifyEmailInteractor(
        storage=UserDB(), 
        response=VerifyEmailResponse(), 
        authentication=UserAuthentication()
    ).verify_email_interactor(email=email, otp=otp)
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def resend_verification_email_view(request):
    email = request.data.get('email')
    
    if not email:
        return ResendVerificationEmailResponse().user_not_found_response()
    
    response = ResendVerificationEmailInteractor(
        storage=UserDB(), 
        response=ResendVerificationEmailResponse()
    ).resend_verification_email_interactor(email=email)
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
def get_complete_user_profile_view(request):
    user_id = request.data.get('user_id', '').strip()
    current_user = str(request.user.user_id)

    response = GetCompleteUserProfileInteractor(
        storage=UserDB(),
        response=GetCompleteUserProfileResponse()
    ).get_complete_user_profile_interactor(user_id=user_id, current_user=current_user)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user_id = str(request.user.user_id)
    preferred_language = request.data.get('preferred_language', '').strip() or None
    age = request.data.get('age', None)
    country = request.data.get('country', '').strip() or None
    profile_picture_url = request.data.get('profile_picture_url', '').strip() or None
    
    response = UpdateProfileInteractor(
        storage=UserDB(),
        response=UpdateProfileResponse()
    ).update_profile_interactor(
        user_id=user_id,
        preferred_language=preferred_language,
        age=age,
        country=country,
        profile_picture_url=profile_picture_url
    )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_users_view(request):
    query = request.query_params.get('q', '').strip()
    limit = request.query_params.get('limit', 20)
    current_user_id = str(request.user.user_id)
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20
    
    response = SearchUsersInteractor(storage=UserDB(), response=SearchUsersResponse()).\
        search_users_interactor(query=query, limit=limit, current_user_id=current_user_id)
    return response

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_recommended_users_view(request):
    if request.method == 'GET':
        user_id = request.query_params.get('user_id', '').strip()
    else:
        user_id = request.data.get('user_id', '').strip()
    
    limit = request.query_params.get('limit', 20) if request.method == 'GET' else request.data.get('limit', 20)
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 20
    
    response = GetRecommendedUsersInteractor(storage=UserDB(), response=GetRecommendedUsersResponse()).\
        get_recommended_users_interactor(user_id=user_id, limit=limit)
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

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_specific_user_posts_view(request):
    user_id = request.data.get('user_id', '').strip()
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
    
    response = GetSpecificUserPostsInteractor(storage=UserDB(), response=GetSpecificUserPostsResponse()).\
        get_specific_user_posts_interactor(user_id=user_id, current_user_id=current_user_id, limit=limit, offset=offset)
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

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_all_wallpapers_view(request):
    response = GetWallpapersInteractor(storage=UserDB(), response=GetWallpapersResponse()).\
        get_all_wallpapers_interactor()
    return response

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_all_stickers_view(request):
    response = GetStickersInteractor(storage=UserDB(), response=GetStickersResponse()).\
        get_all_stickers_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_prayer_request_view(request):
    user_id = str(request.user.user_id)
    description = request.data.get('description')
    
    media_files = request.FILES.getlist('media')
    
    response = CreatePrayerRequestInteractor(storage=UserDB(), response=CreatePrayerRequestResponse()).\
        create_prayer_request_interactor(user_id=user_id, description=description, media_files=media_files)
    return response

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_prayer_request_view(request):
    user_id = str(request.user.user_id)
    prayer_request_id = request.data.get('prayer_request_id')
    description = request.data.get('description')
    
    response = UpdatePrayerRequestInteractor(storage=UserDB(), response=UpdatePrayerRequestResponse()).\
        update_prayer_request_interactor(
            prayer_request_id=prayer_request_id,
            user_id=user_id,
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
        
    current_user_id = str(request.user.user_id)
    
    response = GetAllPrayerRequestsInteractor(storage=UserDB(), response=GetAllPrayerRequestsResponse()).\
        get_all_prayer_requests_interactor(limit=limit, offset=offset, current_user_id=current_user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_prayer_requests_view(request):
    user_id = str(request.user.user_id)
    current_user_id = str(request.user.user_id)
    
    try:
        limit = int(request.query_params.get('limit', 10))
    except (ValueError, TypeError):
        limit = 10
    
    try:
        offset = int(request.query_params.get('offset', 0))
    except (ValueError, TypeError):
        offset = 0
    
    response = GetUserPrayerRequestsInteractor(storage=UserDB(), response=GetUserPrayerRequestsResponse()).\
        get_user_prayer_requests_interactor(user_id=user_id, limit=limit, offset=offset, current_user_id=current_user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_specific_user_prayer_requests_view(request):
    user_id = request.data.get('user_id', '').strip()
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
    
    response = GetSpecificUserPrayerRequestsInteractor(storage=UserDB(), response=GetSpecificUserPrayerRequestsResponse()).\
        get_specific_user_prayer_requests_interactor(user_id=user_id, current_user_id=current_user_id, limit=limit, offset=offset)
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

# ==================== Testimonial APIs ====================
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_testimonial_view(request):
    user_id = str(request.user.user_id)
    description = request.data.get('description')
    rating = request.data.get('rating')
    
    # Handle rating conversion with proper validation
    if rating is not None and rating != '':
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            rating = None
    else:
        rating = None
    
    media_files = request.FILES.getlist('media')
    
    response = CreateTestimonialInteractor(storage=UserDB(), response=CreateTestimonialResponse()).\
        create_testimonial_interactor(user_id=user_id, description=description, rating=rating, media_files=media_files)
    return response

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_testimonials_view(request):
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
    
    response = GetTestimonialsInteractor(storage=UserDB(), response=GetTestimonialsResponse()).\
        get_testimonials_interactor(limit=limit, offset=offset)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_testimonials_view(request):
    user_id = str(request.user.user_id)
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
    
    response = GetUserTestimonialsInteractor(storage=UserDB(), response=GetUserTestimonialsResponse()).\
        get_user_testimonials_interactor(user_id=user_id, limit=limit, offset=offset)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_verse_view(request):
    user_id = str(request.user.user_id)
    verse_id = request.data.get('verse_id')
    
    response = LikeVerseInteractor(storage=UserDB(), response=LikeVerseResponse()).\
        like_verse_interactor(verse_id=verse_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def unlike_verse_view(request):
    user_id = str(request.user.user_id)
    verse_id = request.data.get('verse_id')
    
    response = UnlikeVerseInteractor(storage=UserDB(), response=UnlikeVerseResponse()).\
        unlike_verse_interactor(verse_id=verse_id, user_id=user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_verse_view(request):
    user_id = str(request.user.user_id)
    response = GetVerseInteractor(storage=UserDB(), response=GetVerseResponse()).\
        get_verse_interactor(user_id=user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_verses_view(request):
    user_id = str(request.user.user_id)
    
    response = GetAllVersesInteractor(storage=UserDB(), response=GetAllVersesResponse()).\
        get_all_verses_interactor(user_id=user_id)
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
    image_files = request.FILES.getlist('images')
    
    response = CreatePromotionInteractor(storage=UserDB(), response=CreatePromotionResponse()).\
        create_promotion_interactor(
            title=title,
            description=description,
            price=price,
            redirect_link=redirect_link,
            meta_data_str=meta_data,
            image_files=image_files
        )
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_category_view(request):
    category_name = request.data.get('category_name')
    cover_image_file = request.FILES.get('cover_image')
    description = request.data.get('description')
    display_order = request.data.get('display_order', 0)
    
    response = CreateCategoryInteractor(storage=UserDB(), response=CreateCategoryResponse()).\
        create_category_interactor(
            category_name=category_name,
            cover_image_file=cover_image_file,
            description=description,
            display_order=display_order
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_categories_view(request):
    response = GetCategoriesInteractor(storage=UserDB(), response=GetCategoriesResponse()).\
        get_categories_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_age_group_view(request):
    age_group_name = request.data.get('age_group_name')
    cover_image_file = request.FILES.get('cover_image')
    description = request.data.get('description')
    display_order = request.data.get('display_order', 0)
    
    response = CreateAgeGroupInteractor(storage=UserDB(), response=CreateAgeGroupResponse()).\
        create_age_group_interactor(
            age_group_name=age_group_name,
            cover_image_file=cover_image_file,
            description=description,
            display_order=display_order
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_age_groups_view(request):
    response = GetAgeGroupsInteractor(storage=UserDB(), response=GetAgeGroupsResponse()).\
        get_age_groups_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_books_by_category_and_age_group_view(request):
    user_id = str(request.user.user_id)
    category_id = request.data.get('category_id')
    age_group_id = request.data.get('age_group') or request.data.get('age_group_id')
    
    response = GetBooksByCategoryAndAgeGroupInteractor(storage=UserDB(), response=GetBooksByCategoryAndAgeGroupResponse()).\
        get_books_by_category_and_age_group_interactor(
            user_id=user_id,
            category_id=category_id,
            age_group_id=age_group_id
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_books_by_category_and_age_group_get_view(request):
    user_id = str(request.user.user_id)
    category_id = request.query_params.get('category_id', '').strip()
    age_group_id = request.query_params.get('age_group_id', '').strip()
    
    response = GetBooksByCategoryAndAgeGroupInteractor(storage=UserDB(), response=GetBooksByCategoryAndAgeGroupResponse()).\
        get_books_by_category_and_age_group_interactor(
            user_id=user_id,
            category_id=category_id,
            age_group_id=age_group_id
        )
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_book_chapters_view(request):
    book_id = request.data.get('book_id')

    response = GetBookChaptersInteractor(storage=UserDB(), response=GetBookChaptersResponse()).\
        get_book_chapters_interactor(
            book_id=book_id
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_books_view(request):
    """Get all books with ID and title - accessible to any logged-in user"""
    response = GetAllBooksInteractor(storage=UserDB(), response=GetAllBooksResponse()).\
        get_all_books_interactor()
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_languages_view(request):
    """Get all languages - accessible to any logged-in user"""
    response = GetLanguagesInteractor(storage=UserDB(), response=GetLanguagesResponse()).\
        get_languages_interactor()
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_chapters_view(request):
    book_id = request.data.get('book_id')
    language_id = request.data.get('language_id')
    search_text = request.data.get('search_text')
    
    response = SearchChaptersInteractor(
        es_service=ElasticsearchService(),
        response=SearchChaptersResponse()
    ).search_chapters_interactor(
        book_id=book_id,
        language_id=language_id,
        search_text=search_text
    )
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_book_view(request):
    title = request.data.get('title')
    description = request.data.get('description')
    category = request.data.get('category')
    agegroup = request.data.get('agegroup')
    language = request.data.get('language')
    cover_image_file = request.FILES.get('cover_image')
    
    response = CreateBookInteractor(storage=UserDB(), response=CreateBookResponse()).\
        create_book_interactor(
            title=title,
            description=description,
            category_id=category,
            age_group_id=agegroup,
            language_id=language,
            cover_image_file=cover_image_file
        )
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_create_chapters_view(request):
    book_id = request.data.get('book_id')
    bookdata = request.data.get('bookdata')

    files_dict = {}
    for key in request.FILES.keys():
        if key.startswith('file_'):
            files_dict[key] = request.FILES[key]

    response = CreateChaptersInteractor(storage=UserDB(), response=CreateChaptersResponse()).\
        create_chapters_interactor(
            book_id=book_id,
            bookdata=bookdata,
            files_dict=files_dict
        )
    return response


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_categories_view(request):
    response = AdminGetCategoriesInteractor(storage=UserDB(), response=AdminGetCategoriesResponse()).\
        get_categories_interactor()
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_languages_view(request):
    response = GetLanguagesInteractor(storage=UserDB(), response=GetLanguagesResponse()).\
        get_languages_interactor()
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_age_groups_view(request):
    response = AdminGetAgeGroupsInteractor(storage=UserDB(), response=AdminGetAgeGroupsResponse()).\
        get_age_groups_interactor()
    return response

# ==================== Admin Testimonial APIs ====================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_get_testimonials_view(request):
    limit = request.query_params.get('limit', 10)
    offset = request.query_params.get('offset', 0)
    status_filter = request.query_params.get('status', 'all')
    
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
    
    try:
        offset = int(offset)
    except (ValueError, TypeError):
        offset = 0
    
    response = AdminGetTestimonialsInteractor(storage=UserDB(), response=AdminGetTestimonialsResponse()).\
        get_testimonials_interactor(limit=limit, offset=offset, status_filter=status_filter)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_approve_testimonial_view(request):
    testimonial_id = request.data.get('testimonial_id')
    
    response = AdminApproveTestimonialInteractor(storage=UserDB(), response=AdminApproveTestimonialResponse()).\
        approve_testimonial_interactor(testimonial_id=testimonial_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_reject_testimonial_view(request):
    testimonial_id = request.data.get('testimonial_id')
    
    response = AdminRejectTestimonialInteractor(storage=UserDB(), response=AdminRejectTestimonialResponse()).\
        reject_testimonial_interactor(testimonial_id=testimonial_id)
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

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_highlight_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    chapter_id = request.data.get('chapter_id', '').strip()
    block_id = request.data.get('block_id', '').strip() or None
    start_offset = request.data.get('start_offset', '').strip()
    end_offset = request.data.get('end_offset', '').strip()
    color = request.data.get('color', 'yellow').strip() or 'yellow'
    
    response = CreateHighlightInteractor(storage=UserDB(), response=CreateHighlightResponse()).\
        create_highlight_interactor(
            user_id=user_id,
            book_id=book_id,
            chapter_id=chapter_id,
            block_id=block_id,
            start_offset=start_offset,
            end_offset=end_offset,
            color=color
        )
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_highlights_view(request, book_id: str):
    user_id = request.query_params.get('user_id', '').strip()
    
    if not user_id:
        user_id = str(request.user.user_id)
    
    response = GetHighlightsInteractor(storage=UserDB(), response=GetHighlightsResponse()).\
        get_highlights_interactor(user_id=user_id, book_id=book_id)
    return response

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_highlight_view(request):
    user_id = str(request.user.user_id)
    highlight_id = request.data.get('highlight_id', '').strip()
    
    response = DeleteHighlightInteractor(storage=UserDB(), response=DeleteHighlightResponse()).\
        delete_highlight_interactor(highlight_id=highlight_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_reading_note_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    content = request.data.get('content', '').strip()
    chapter_id = request.data.get('chapter_id', '').strip() or None
    block_id = request.data.get('block_id', '').strip() or None

    response = CreateReadingNoteInteractor(storage=UserDB(), response=CreateReadingNoteResponse()).\
        create_reading_note_interactor(
            user_id=user_id,
            book_id=book_id,
            content=content,
            chapter_id=chapter_id,
            block_id=block_id
        )
    return response
def create_post_share_link_view(request):
    user_id = str(request.user.user_id)
    post_id = request.data.get('post_id', '').strip()
    
    response = CreatePostShareLinkInteractor(storage=UserDB(), response=CreatePostShareLinkResponse()).\
        create_post_share_link_interactor(post_id=post_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_profile_share_link_view(request):
    created_by_user_id = str(request.user.user_id)
    user_id = request.data.get('user_id', '').strip()
    
    # If user_id not provided, default to current user's profile
    if not user_id:
        user_id = created_by_user_id
    
    response = CreateProfileShareLinkInteractor(storage=UserDB(), response=CreateProfileShareLinkResponse()).\
        create_profile_share_link_interactor(user_id=user_id, created_by_user_id=created_by_user_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_reading_notes_view(request, book_id: str):
    user_id = request.query_params.get('user_id', '').strip()
    
    if not user_id:
        user_id = str(request.user.user_id)
    
    response = GetReadingNotesInteractor(storage=UserDB(), response=GetReadingNotesResponse()).\
        get_reading_notes_interactor(user_id=user_id, book_id=book_id)
    return response

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_reading_note_view(request):
    user_id = str(request.user.user_id)
    note_id = request.data.get('note_id', '').strip()
    content = request.data.get('content', '').strip()
    
    response = UpdateReadingNoteInteractor(storage=UserDB(), response=UpdateReadingNoteResponse()).\
        update_reading_note_interactor(note_id=note_id, user_id=user_id, content=content)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_reading_note_view(request):
    user_id = str(request.user.user_id)
    note_id = request.data.get('note_id', '').strip()
    
    response = DeleteReadingNoteInteractor(storage=UserDB(), response=DeleteReadingNoteResponse()).\
        delete_reading_note_interactor(note_id=note_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_bookmark_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    
    response = CreateBookmarkInteractor(storage=UserDB(), response=CreateBookmarkResponse()).\
        create_bookmark_interactor(user_id=user_id, book_id=book_id)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_bookmarks_view(request):
    user_id = str(request.user.user_id)
    
    response = GetBookmarksInteractor(storage=UserDB(), response=GetBookmarksResponse()).\
        get_bookmarks_interactor(user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_bookmark_view(request):
    user_id = str(request.user.user_id)
    bookmark_id = request.data.get('bookmark_id', '').strip()
    
    response = DeleteBookmarkInteractor(storage=UserDB(), response=DeleteBookmarkResponse()).\
        delete_bookmark_interactor(bookmark_id=bookmark_id, user_id=user_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def toggle_bookmark_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    
    response = ToggleBookmarkInteractor(storage=UserDB(), response=ToggleBookmarkResponse()).\
        toggle_bookmark_interactor(user_id=user_id, book_id=book_id)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_reading_progress_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    chapter_id = request.data.get('chapter_id', '').strip() or None
    progress_percentage = request.data.get('progress_percentage')
    block_id = request.data.get('block_id', '').strip() or None
    
    response = CreateReadingProgressInteractor(storage=UserDB(), response=CreateReadingProgressResponse()).\
        create_reading_progress_interactor(
            user_id=user_id,
            book_id=book_id,
            chapter_id=chapter_id,
            progress_percentage=progress_percentage,
            block_id=block_id
        )
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_reading_progress_view(request):
    user_id = str(request.user.user_id)
    book_id = request.data.get('book_id', '').strip()
    
    response = GetReadingProgressInteractor(storage=UserDB(), response=GetReadingProgressResponse()).\
        get_reading_progress_interactor(
            user_id=user_id,
            book_id=book_id
        )
    return response

@api_view(['POST'])
def get_shared_post_view(request, token: str):
    response = GetSharedPostInteractor(storage=UserDB(), response=GetSharedPostResponse()).\
        get_shared_post_interactor(token=token)
    return response

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_shared_profile_view(request, token: str):
    response = GetSharedProfileInteractor(storage=UserDB(), response=GetSharedProfileResponse()).\
        get_shared_profile_interactor(token=token)
    return response

