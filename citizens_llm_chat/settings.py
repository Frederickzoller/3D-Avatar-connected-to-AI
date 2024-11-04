import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
import json
import logging

# Configure logger first
logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Basic Django settings - Move these up since DEBUG is used in logging config
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-temporary-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Environment variables with better error handling
def get_env_variable(var_name, default=None, required=True):
    value = os.environ.get(var_name, default)
    if value is None and required:
        error_msg = f'Required environment variable {var_name} is not set'
        logger.error(error_msg)
        raise ImproperlyConfigured(error_msg)
    return value

# Rest Framework settings
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

# LLM settings
LLM_CONFIG = {
    'model_name': "Qwen/Qwen2.5-72B-Instruct",
    'max_length': 512,
    'temperature': 0.7,
    'device': 'cpu',
    'load_in_8bit': True,  # Reduce memory usage
    'torch_dtype': 'float32'
}

# Update HF_API_TOKEN with better error handling
HF_API_TOKEN = get_env_variable('HF_API_TOKEN', required=True)
LLM_MODEL = LLM_CONFIG['model_name']

# Add debug logging for LLM configuration
if DEBUG:
    logger.info(f"LLM Configuration: {json.dumps(LLM_CONFIG, indent=2)}")
    logger.info(f"HF_API_TOKEN set: {bool(HF_API_TOKEN)}")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'chat',
    'storages',
    'corsheaders',
]

# CORS settings - Preserved exactly as before
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://threed-avatar-connected-to-ai-1.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

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

# Middleware - Keep CORS middleware first
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Keep this first
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'chat.middleware.ApiCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

# Logging configuration
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
        'chat': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'citizens_llm_chat': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']
CSRF_USE_SESSIONS = True

# Other Django settings
ROOT_URLCONF = 'citizens_llm_chat.urls'
WSGI_APPLICATION = 'citizens_llm_chat.wsgi.application'
APPEND_SLASH = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Host settings
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'threed-avatar-connected-to-ai-1.onrender.com',
    '*',
]

# Proxy settings
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')