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
