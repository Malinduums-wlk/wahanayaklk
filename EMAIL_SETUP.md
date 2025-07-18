# Email Setup Guide for Wahanayak

This guide explains how to set up welcome emails using Zoho Mail for your Django application.

## Zoho Mail Configuration

### 1. Get Zoho App Password

1. Log into your Zoho Mail account (hello@wahanayak.lk)
2. Go to **Settings** → **Mail Accounts** → **Security**
3. Generate an **App Password** (not your regular password)
4. Copy this app password - you'll need it for the environment variables

### 2. Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Zoho Mail Configuration
EMAIL_HOST_USER=hello@wahanayak.lk
EMAIL_HOST_PASSWORD=your_zoho_app_password_here
```

**Important:** Never commit your `.env` file to version control!

### 3. Testing the Email Setup

#### Test with a specific user ID:
```bash
python manage.py test_email --user-id 1
```

#### Test with a specific email address:
```bash
python manage.py test_email --email test@example.com
```

### 4. Email Features

#### Welcome Email
- Sent automatically when users register
- Beautiful HTML design with your branding
- Includes getting started guide
- Responsive design for mobile and desktop

#### Admin Notifications
- Sent to admin when new users register
- Includes user details and registration date
- Helps you monitor new registrations

### 5. Email Templates

The email templates are located in:
- `templates/users/emails/welcome_email.html` - HTML version
- `templates/users/emails/welcome_email.txt` - Plain text version
- `templates/users/emails/admin_notification.html` - Admin notification HTML
- `templates/users/emails/admin_notification.txt` - Admin notification text

### 6. Troubleshooting

#### Common Issues:

1. **Authentication Error**: Make sure you're using an App Password, not your regular password
2. **Connection Error**: Verify your Zoho Mail settings and internet connection
3. **Template Error**: Check that all email templates exist in the correct locations

#### Debug Mode:
In development, emails are printed to the console instead of being sent. To test actual email sending:

1. Set `DEBUG = False` in settings.py temporarily
2. Configure your Zoho Mail credentials
3. Test the email functionality
4. Set `DEBUG = True` back for development

### 7. Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure your Zoho Mail credentials in environment variables
3. Test email functionality thoroughly
4. Monitor email delivery and bounce rates

### 8. Security Notes

- Always use App Passwords for SMTP authentication
- Never commit credentials to version control
- Use environment variables for sensitive data
- Monitor email logs for any issues

## Support

If you encounter any issues with the email setup, check:
1. Zoho Mail account settings
2. App Password configuration
3. Environment variables
4. Django email settings

For additional help, contact your system administrator or refer to the Django email documentation. 