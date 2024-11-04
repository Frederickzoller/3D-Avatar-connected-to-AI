import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',  # Required for token authentication
    'chat',
    'storages',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# Raise error if critical environment variables are missing
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f'Set the {var_name} environment variable'
        raise ImproperlyConfigured(error_msg)

# LLM settings
LLM_CONFIG = {
    'model_name': "Qwen/Qwen2.5-72B-Instruct",
    'max_length': 512,
    'temperature': 0.7,
    'device': 'cpu',
    'load_in_8bit': True,  # Reduce memory usage
    'torch_dtype': 'float32'
}

# Environment variables with better error handling
def get_env_variable(var_name, default=None, required=True):
    value = os.environ.get(var_name, default)
    if value is None and required:
        error_msg = f'Required environment variable {var_name} is not set'
        logger.error(error_msg)
        raise ImproperlyConfigured(error_msg)
    return value

# Update HF_API_TOKEN with better error handling
HF_API_TOKEN = get_env_variable('HF_API_TOKEN', required=True)
LLM_MODEL = LLM_CONFIG['model_name']

# Add debug logging for LLM configuration
if DEBUG:
    logger.info(f"LLM Configuration: {json.dumps(LLM_CONFIG, indent=2)}")
    logger.info(f"HF_API_TOKEN set: {bool(HF_API_TOKEN)}")

# Voice synthesis settings
ELEVENLABS_API_KEY = get_env_variable('ELEVENLABS_API_KEY')
VOICE_SYNTHESIS_ENABLED = os.environ.get('VOICE_SYNTHESIS_ENABLED', 'True').lower() == 'true'
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
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'chat.middleware.ApiCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
        'chat': {  # Add this logger for our app
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Make sure these authentication backends are included
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Add CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://threed-avatar-connected-to-ai-1.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

# Add these headers to allow the necessary request headers
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

# Allow all HTTP methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Add CORS_ORIGIN_ALLOW_ALL for development
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True

# Ensure CORS middleware is at the top
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Keep this first
    'django.middleware.common.CommonMiddleware',  # This should come right after
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'chat.middleware.ApiCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add this to help with proxy settings
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')