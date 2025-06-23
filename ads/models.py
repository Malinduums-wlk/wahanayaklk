from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils.text import slugify

def generate_ad_id():
    while True:
        # Generate a random 6-digit number
        digits = ''.join(random.choices(string.digits, k=6))
        ad_id = f'A{digits}'
        # Check if this ID already exists
        if not Vehicle.objects.filter(ad_id=ad_id).exists():
            return ad_id

class Vehicle(models.Model):
    CONDITION_CHOICES = [
        ('brand_new', 'Brand New'),
        ('used', 'Used (Registered)'),
        ('recondition', 'Recondition (Unregistered)')
    ]

    TRANSMISSION_CHOICES = [
        ('auto', 'Auto'),
        ('manual', 'Manual')
    ]

    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    # Basic Info
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad_id = models.CharField(max_length=7, unique=True, default=generate_ad_id)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    is_urgent = models.BooleanField(default=False)
    
    # Contact Info
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15, null=True, blank=True)
    
    # Vehicle Details
    mileage = models.IntegerField(null=True, blank=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, null=True, blank=True)
    engine = models.CharField(max_length=100, null=True, blank=True)
    year = models.IntegerField()
    registered = models.IntegerField(null=True, blank=True)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, null=True, blank=True)
    exterior_color = models.CharField(max_length=50, null=True, blank=True)
    interior_color = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=200)
    
    # Description
    description = models.TextField(null=True, blank=True)
    
    # Features
    air_condition = models.BooleanField(default=False)
    power_windows = models.BooleanField(default=False)
    power_mirrors = models.BooleanField(default=False)
    power_seats = models.BooleanField(default=False)
    power_steering = models.BooleanField(default=False)
    sun_roof = models.BooleanField(default=False)
    abs = models.BooleanField(default=False)
    led = models.BooleanField(default=False)
    reverse_camera = models.BooleanField(default=False)
    air_bags = models.BooleanField(default=False)
    
    # Price
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    @property
    def expires_at(self):
        from datetime import timedelta
        return self.created_at + timedelta(days=30)

    def save(self, *args, **kwargs):
        # Automatically generate a unique slug if it is missing
        if not self.slug:
            base_slug = slugify(f"{self.make}-{self.model}-{self.year}")
            slug_candidate = base_slug
            counter = 1
            while Vehicle.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='vehicle_images/')
    
    def __str__(self):
        return f"Image for {self.vehicle}"

class VehicleAd(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    class Meta:
        ordering = ['-created_at']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vehicle')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.vehicle.title}"
