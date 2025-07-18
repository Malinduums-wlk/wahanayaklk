from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.utils import send_otp_email

class Command(BaseCommand):
    help = 'Test OTP functionality for password reset'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='User ID to send OTP to')
        parser.add_argument('--email', type=str, help='Email address to send OTP to')

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        email = options.get('email')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Generating OTP for user: {user.username} ({user.email})')
                
                # Generate OTP
                otp = user.userprofile.generate_otp()
                self.stdout.write(f'Generated OTP: {otp}')
                
                # Send OTP email
                success = send_otp_email(user, otp)
                if success:
                    self.stdout.write(self.style.SUCCESS('OTP email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send OTP email'))
                    
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
        
        elif email:
            try:
                user = User.objects.get(email=email)
                self.stdout.write(f'Generating OTP for user: {user.username} ({user.email})')
                
                # Generate OTP
                otp = user.userprofile.generate_otp()
                self.stdout.write(f'Generated OTP: {otp}')
                
                # Send OTP email
                success = send_otp_email(user, otp)
                if success:
                    self.stdout.write(self.style.SUCCESS('OTP email sent successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to send OTP email'))
                    
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {email} does not exist'))
        
        else:
            self.stdout.write(self.style.WARNING('Please provide either --user-id or --email argument')) 