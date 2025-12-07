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
from bible_way.presenters.user_profile_response import UserProfileResponse
from bible_way.presenters.follow_user_response import FollowUserResponse
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
    google_id = request.data.get('google_id')
    email = request.data.get('email')
    name = request.data.get('name')
    country = request.data.get('country')
    age = request.data.get('age')
    preferred_language = request.data.get('preferred_language')
    profile_picture_url = request.data.get('profile_picture_url')
    response = GoogleAuthInteractor(storage=UserDB(), response=GoogleAuthResponse(), authentication=UserAuthentication()).\
        google_signup_interactor(google_id=google_id, email=email, name=name, country=country, age=age, preferred_language=preferred_language, profile_picture_url=profile_picture_url)
    return response

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def google_login_view(request):
    google_id = request.data.get('google_id')
    email = request.data.get('email')
    response = GoogleLoginInteractor(storage=UserDB(), response=GoogleAuthResponse(), authentication=UserAuthentication()).\
        google_login_interactor(google_id=google_id, email=email)
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
