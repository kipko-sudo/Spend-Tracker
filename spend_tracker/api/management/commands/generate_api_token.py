from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates or retrieves an API token for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to generate token for')
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate token if it already exists',
        )

    def handle(self, *args, **options):
        username = options['username']
        regenerate = options['regenerate']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')
        
        if regenerate:
            # Delete existing token if it exists
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Regenerated API token for user "{username}": {token.key}'))
        else:
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Generated new API token for user "{username}": {token.key}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Existing API token for user "{username}": {token.key}'))