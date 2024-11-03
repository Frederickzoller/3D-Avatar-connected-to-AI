import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()


INSTALLED_APPS = [
    # ...
    'rest_framework',
    'chat',
    'storages',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
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
LLM_MODEL = "Qwen/Qwen2.5-72B-Instruct"
LLM_API_KEY = get_env_variable('LLM_API_KEY')  # If needed for your setup

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