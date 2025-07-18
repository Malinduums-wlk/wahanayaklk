from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random

# Create your models here.

class UserProfile(models.Model):
    LISTING_CHOICES = [
        ('user', 'User'),
        ('company', 'Company')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=8, unique=True, blank=True)
    is_premium = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    listing_type = models.CharField(max_length=10, choices=LISTING_CHOICES, default='user')
    
    # Badge fields
    has_verified_badge = models.BooleanField(default=False)
    verified_badge_end_date = models.DateField(null=True, blank=True)
    has_premium_badge = models.BooleanField(default=False)
    premium_badge_end_date = models.DateField(null=True, blank=True)
    has_trusted_badge = models.BooleanField(default=False)
    trusted_badge_end_date = models.DateField(null=True, blank=True)
    
    # Password reset OTP fields
    reset_otp = models.CharField(max_length=6, null=True, blank=True)
    reset_otp_expiry = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Generate a unique ID like #U123456
            while True:
                new_id = f'#U{random.randint(100000, 999999)}'
                if not UserProfile.objects.filter(unique_id=new_id).exists():
                    self.unique_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def generate_otp(self):
        """Generate a 6-digit OTP and set expiry (10 minutes)"""
        self.reset_otp = str(random.randint(100000, 999999))
        self.reset_otp_expiry = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.reset_otp
    
    def verify_otp(self, otp):
        """Verify if the provided OTP is correct and not expired"""
        if not self.reset_otp or not self.reset_otp_expiry:
            return False
        
        if timezone.now() > self.reset_otp_expiry:
            return False
        
        if self.reset_otp == otp:
            return True
        
        return False
    
    def clear_otp(self):
        """Clear the OTP after successful use"""
        self.reset_otp = None
        self.reset_otp_expiry = None
        self.save()

class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cover_photo = models.ImageField(upload_to='shop_covers/', null=True, blank=True)
    company_name = models.CharField(max_length=100)
    contact_number1 = models.CharField(max_length=20)
    contact_number2 = models.CharField(max_length=20, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()
    google_map_link = models.URLField(max_length=500, null=True, blank=True)
    facebook_link = models.URLField(max_length=200, null=True, blank=True)
    youtube_link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.company_name} Shop"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser:
        return
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    profile.save()
