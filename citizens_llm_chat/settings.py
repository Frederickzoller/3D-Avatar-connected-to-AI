import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Raise error if critical environment variables are missing
def get_env_variable(var_name, default=None, required=True):
    """Get an environment variable with better error handling"""
    try:
        return os.environ[var_name]
    except KeyError:
        if required:
            error_msg = f'Set the {var_name} environment variable'
            raise ImproperlyConfigured(error_msg)
        return default

# LLM settings
LLM_MODEL = "facebook/opt-125m"  # Using a smaller model for testing
HF_API_TOKEN = get_env_variable('HF_API_TOKEN', default='', required=False)  # Make it optional for initial deployment

# Voice synthesis settings - Make optional
ELEVENLABS_API_KEY = get_env_variable('ELEVENLABS_API_KEY', default='', required=False)
VOICE_SYNTHESIS_ENABLED = os.environ.get('VOICE_SYNTHESIS_ENABLED', 'False').lower() == 'true'
DEFAULT_VOICE_ID = os.environ.get('DEFAULT_VOICE_ID', 'default')

# Avatar storage settings - Only configure if storage is enabled
if os.environ.get('USE_S3_STORAGE', 'False').lower() == 'true':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = get_env_variable('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = get_env_variable('AWS_S3_REGION_NAME')
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False

# Remove the first INSTALLED_APPS definition completely and keep only these:
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'storages',
    'corsheaders',
]

LOCAL_APPS = [
    'chat',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Middleware configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Make sure this is first
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Basic Django settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-temporary-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Allows all subdomains of onrender.com
    'threed-avatar-connected-to-ai-1.onrender.com',  # Your specific Render URL
    '*',  # Allow all hosts in development
]

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Add ROOT_URLCONF setting
ROOT_URLCONF = 'citizens_llm_chat.urls'

# Add WSGI_APPLICATION setting
WSGI_APPLICATION = 'citizens_llm_chat.wsgi.application'

# Add CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']  # Add your frontend domains here
CSRF_USE_SESSIONS = True  # Store CSRF tokens in sessions for better security

# Add APPEND_SLASH setting
APPEND_SLASH = True  # This prevents Django from enforcing trailing slashes

# Add these to your existing settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'chat.middleware': {
            'handlers': ['console'],
            'level': 'INFO',  # Change to INFO to reduce debug noise
            'propagate': False,
        },
    },
}

# Make sure these authentication backends are included
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Add CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",  # Add local development server
    "http://127.0.0.1:5500",
    "https://threed-avatar-connected-to-ai-1.onrender.com",  # Add deployed Render URL
]

CORS_ALLOW_CREDENTIALS = True
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
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Disable CSRF for API endpoints
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://threed-avatar-connected-to-ai-1.onrender.com",  # Add deployed Render URL
]

SECURE_SSL_REDIRECT = not DEBUG
USE_X_FORWARDED_HOST = True

# Update CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://threed-avatar-connected-to-ai-1.onrender.com",
]

# Remove duplicate CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = False  # Changed from True since we're not using credentials
CORS_PREFLIGHT_MAX_AGE = 86400

# Update CORS headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Remove duplicate CSRF settings and keep only one set
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://threed-avatar-connected-to-ai-1.onrender.com",
]