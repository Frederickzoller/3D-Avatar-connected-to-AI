from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Ensures demo user exists'

    def handle(self, *args, **kwargs):
        username = 'demo_user'
        password = 'demo_password'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Demo user "{username}" already exists')
        except User.DoesNotExist:
            User.objects.create_user(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created demo user "{username}"')) 