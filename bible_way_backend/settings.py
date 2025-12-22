from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# Optional Firebase import
try:
    import firebase_admin
    from firebase_admin import credentials
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-2l7)6pd1jtn6_f)d)b$lh-&502@2b@x$5%4m0kwz-o7opz4q*d'
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    "bibleway.io",
    "www.bibleway.io",
    "api.bibleway.io",
    "www.api.bibleway.io",
    "13.201.42.31",  # ✅ AWS EC2 IP address
    "127.0.0.1",
    "localhost",
]

# -------------------------------------------------------------------
# DATA UPLOAD SETTINGS
# -------------------------------------------------------------------
# Increase limits for large data uploads (e.g., bulk chapter creation)
# 500MB limit (524288000 bytes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000
# No limit on number of fields (set to a very large number)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
# 500MB limit for file uploads in memory
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000

# -------------------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'daphne',  # Must be FIRST for ASGI support
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'storages',
    'bible_way',
    "project_chat",
    "project_notifications",
]

# -------------------------------------------------------------------
# MIDDLEWARE (ORDER MATTERS!)
# -------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST BE FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'bible_way.middleware.DisableCSRFForAPI',  # ✅ Custom middleware to exempt API endpoints (MUST BE BEFORE CSRF)
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------------------------------------------
# CORS CONFIGURATION (FOR FRONTEND)
# -------------------------------------------------------------------
# ✅ TEMPORARY: Allow all origins for debugging
# Once working, restrict to specific domains
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Only allow requests from bibleway.io domains (not used when ALLOW_ALL is True)
# CORS_ALLOWED_ORIGINS = [
#     "https://bibleway.io",
#     "https://www.bibleway.io",
#     "http://bibleway.io",
#     "http://www.bibleway.io",
#     "http://13.201.42.31",
# ]

# Explicitly allow all methods and headers for maximum compatibility
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'accept-language',
    'authorization',
    'content-type',
    'content-length',
    'dnt',
    'origin',
    'referer',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-forwarded-for',
    'x-forwarded-proto',
    'cache-control',
    'pragma',
    # ✅ Additional headers for modern browsers
    'sec-ch-ua',
    'sec-ch-ua-mobile',
    'sec-ch-ua-platform',
]

# Expose headers that frontend might need to read
CORS_EXPOSE_HEADERS = [
    'content-type',
    'authorization',
    'x-csrftoken',
]

# Cache preflight requests for 1 hour
CORS_PREFLIGHT_MAX_AGE = 3600

# -------------------------------------------------------------------
# CSRF CONFIG
# -------------------------------------------------------------------
# Allow all origins - Configure CSRF to be maximally permissive
# Note: Django doesn't support wildcards in CSRF_TRUSTED_ORIGINS
# For API endpoints using JWT auth, CSRF is not required
CSRF_TRUSTED_ORIGINS = [
    "https://bibleway.io",
    "https://www.bibleway.io",
    "https://api.bibleway.io",
    "https://www.api.bibleway.io",
    "https://www.api.bibleway.io",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8000",
    "http://localhost",
    "http://127.0.0.1",
    # Add any other specific origins you need
]
# Make CSRF cookies work with all cross-origin requests
# ✅ CRITICAL: SameSite=None REQUIRES Secure=True (browser requirement)
CSRF_COOKIE_SECURE = True  # Required when using SameSite=None
CSRF_COOKIE_SAMESITE = 'None'  # Allow all cross-site requests
CSRF_USE_SESSIONS = False  # Use cookie-based CSRF tokens
# CSRF is effectively bypassed for API endpoints via JWT authentication

# -------------------------------------------------------------------
ROOT_URLCONF = 'bible_way_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bible_way_backend.wsgi.application'

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------
# ASGI Application for WebSocket support
ASGI_APPLICATION = 'bible_way_backend.asgi.application'

# Database Configuration
# Production: AWS RDS MySQL Configuration
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#             'charset': 'utf8mb4',
#         }
#     }
# }

# Local Development: SQLite Configuration (Commented out - uncomment to use locally)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------------------------------------------------
# AUTH
# -------------------------------------------------------------------
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom User Model
AUTH_USER_MODEL = 'bible_way.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC / MEDIA (S3)
# -------------------------------------------------------------------
STATIC_URL = 'static/'

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_DEFAULT_ACL = 'public-read'

# S3 Presigned URL Configuration
AWS_S3_PRESIGNED_URL_EXPIRATION = int(os.getenv('AWS_S3_PRESIGNED_URL_EXPIRATION', '3600'))  # Default 1 hour
AWS_S3_USE_PRESIGNED_URLS = os.getenv('AWS_S3_USE_PRESIGNED_URLS', 'True').lower() == 'true'

# AWS SES Configuration for Email
# Uses the same AWS credentials as S3 (from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars)
AWS_SES_REGION = os.getenv('AWS_SES_REGION', 'ap-south-1')  # Default to ap-south-1 (Mumbai)
AWS_SES_FROM_EMAIL = os.getenv('AWS_SES_FROM_EMAIL', 'noreply@bibleway.com')

# -------------------------------------------------------------------
# ZEPTOMAIL CONFIGURATION
# -------------------------------------------------------------------
ZEPTOMAIL_API_TOKEN = os.getenv('ZEPTOMAIL_API_TOKEN', '')
ZEPTOMAIL_FROM_EMAIL = os.getenv('ZEPTOMAIL_FROM_EMAIL', 'noreply@linchpinsoftsolution.com')
ZEPTOMAIL_OTP_EXPIRY_MINUTES = int(os.getenv('ZEPTOMAIL_OTP_EXPIRY_MINUTES', '15'))

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# -------------------------------------------------------------------
# FIREBASE
# -------------------------------------------------------------------
CRED_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if FIREBASE_AVAILABLE and firebase_admin and not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CRED_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized")
    except Exception as e:
        print("Firebase init error:", e)
# Optional AWS Settings
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }
# AWS_QUERYSTRING_AUTH = False
# AWS_S3_VERIFY = True

# Channel Layers Configuration for WebSocket support
USE_REDIS = os.getenv('USE_REDIS', 'false').lower() == 'true'

if USE_REDIS:
    # Production: Redis channel layer
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
                "capacity": 1500,
                "expiry": 60,
            },
        },
    }
else:
    # Development: InMemory channel layer (no Redis required)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

# -------------------------------------------------------------------
# ELASTICSEARCH CONFIGURATION
# -------------------------------------------------------------------
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
ELASTICSEARCH_USE_SSL = os.getenv('ELASTICSEARCH_USE_SSL', 'False').lower() == 'true'
ELASTICSEARCH_VERIFY_CERTS = os.getenv('ELASTICSEARCH_VERIFY_CERTS', 'True').lower() == 'true'
ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME', '')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', '')
ELASTICSEARCH_INDEX_NAME = os.getenv('ELASTICSEARCH_INDEX_NAME', 'chapters_index')
