from dataclasses import dataclass

@dataclass
class SignupResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class LoginResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class GoogleSignupResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class GoogleLoginResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class UserProfileResponseDTO:
    user_id: str
    user_name: str
    email: str
    country: str
    age: int | None
    preferred_language: str | None
    profile_picture_url: str | None
    is_admin: bool
    following_count: int
    followers_count: int


@dataclass
class CompleteUserProfileResponseDTO:
    user_id: str
    user_name: str
    email: str
    country: str
    age: int | None
    preferred_language: str | None
    profile_picture_url: str | None
    is_admin: bool
    followers_count: int
    following_count: int
    is_following: bool