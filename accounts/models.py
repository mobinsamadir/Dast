from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'users/avatars/{filename}'

class CustomUser(AbstractUser):
    username = None # Remove standard username
    phone_number = models.CharField(max_length=15, unique=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    display_name = models.CharField(max_length=150)

    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)

    MARITAL_CHOICES = (('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed'))
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, null=True, blank=True)

    children_count = models.IntegerField(default=0)
    eldest_child_age = models.IntegerField(null=True, blank=True)

    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    skin_color = models.CharField(max_length=50, null=True, blank=True)
    beauty = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)

    STYLE_CHOICES = (('Hijab', 'Hijab'), ('Non_Hijab', 'Non_Hijab'), ('Other', 'Other'))
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, null=True, blank=True)

    health_status = models.CharField(max_length=150, null=True, blank=True)
    income = models.CharField(max_length=100, null=True, blank=True)
    car_status = models.CharField(max_length=100, null=True, blank=True)
    housing_status = models.CharField(max_length=100, null=True, blank=True)

    LIFESTYLE_CHOICES = (('With_Family', 'With Family'), ('Independent', 'Independent'))
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES, null=True, blank=True)

    province = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    show_location = models.BooleanField(default=False)

    bio = models.TextField(null=True, blank=True)
    spouse_expectation = models.TextField(null=True, blank=True)

    security_phrase = models.CharField(max_length=255, null=True, blank=True)

    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')

    SEEKING_CHOICES = (
        ('Friend', 'Friend'), ('Benefit', 'Benefit'), ('Situationship', 'Situationship'),
        ('Partner', 'Partner'), ('Roommate', 'Roommate'), ('Spouse', 'Spouse')
    )
    seeking = models.CharField(max_length=20, choices=SEEKING_CHOICES, null=True, blank=True)
    target_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    profile_picture = models.ImageField(upload_to=user_directory_path, null=True, blank=True)

    STATUS_CHOICES = (('Active', 'Active'), ('Blocked', 'Blocked'), ('Unverified', 'Unverified'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unverified')

    is_totp_enabled = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'display_name']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()

        if self.profile_picture:
            img = Image.open(self.profile_picture)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=75)
            output.seek(0)
            self.profile_picture = InMemoryUploadedFile(
                output, 'ImageField',
                f"{self.profile_picture.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number
