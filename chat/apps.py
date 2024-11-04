from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_demo_user(sender, **kwargs):
    from django.contrib.auth.models import User
    from django.core.management import call_command
    
    # Create demo user using the management command
    call_command('ensure_demo_user')

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        post_migrate.connect(create_demo_user, sender=self) 