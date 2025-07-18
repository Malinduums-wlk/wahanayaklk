from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.utils import send_welcome_email, send_admin_notification

class Command(BaseCommand):
    help = 'Test email functionality'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='User ID to send test email to')
        parser.add_argument('--email', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        email = options.get('email')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Sending welcome email to user: {user.username} ({user.email})')
                success = send_welcome_email(user)
                if success:
                    self.stdout.write(self.style.SUCCESS('Welcome email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send welcome email'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
        
        elif email:
            # Create a test user for email testing
            test_user = User.objects.create_user(
                username='test_user',
                email=email,
                first_name='Test',
                last_name='User',
                password='testpass123'
            )
            self.stdout.write(f'Sending test welcome email to: {email}')
            success = send_welcome_email(test_user)
            if success:
                self.stdout.write(self.style.SUCCESS('Test welcome email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('Failed to send test welcome email'))
            
            # Clean up test user
            test_user.delete()
        
        else:
            self.stdout.write(self.style.WARNING('Please provide either --user-id or --email argument')) 