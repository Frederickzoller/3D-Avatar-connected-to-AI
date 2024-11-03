INSTALLED_APPS = [
    # ...
    'rest_framework',
    'chat',
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

# OpenAI settings
OPENAI_API_KEY = 'your-api-key-here' 