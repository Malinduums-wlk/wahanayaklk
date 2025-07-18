from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

def send_welcome_email(user):
    """
    Send a welcome email to newly registered users
    """
    subject = 'Welcome to Wahanayak! 🚗'
    
    # Prepare context for the email template
    context = {
        'user': user,
        'first_name': user.first_name or user.username,
        'site_name': 'Wahanayak',
        'site_url': 'https://wahanayak.lk',
    }
    
    # Render the email template
    html_message = render_to_string('users/emails/welcome_email.html', context)
    plain_message = render_to_string('users/emails/welcome_email.txt', context)
    
    try:
        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email to {user.email}: {str(e)}")
        return False

def send_admin_notification(user):
    """
    Send notification to admin about new user registration
    """
    subject = f'New User Registration: {user.username}'
    
    context = {
        'user': user,
        'site_name': 'Wahanayak',
    }
    
    html_message = render_to_string('users/emails/admin_notification.html', context)
    plain_message = render_to_string('users/emails/admin_notification.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # Send to admin email
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")
        return False

def send_otp_email(user, otp):
    """
    Send OTP email for password reset
    """
    subject = 'Password Reset OTP - Wahanayak'
    
    context = {
        'user': user,
        'otp': otp,
        'site_name': 'Wahanayak',
        'expiry_minutes': 10,
    }
    
    html_message = render_to_string('users/emails/otp_email.html', context)
    plain_message = render_to_string('users/emails/otp_email.txt', context)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email to {user.email}: {str(e)}")
        return False 