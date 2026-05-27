from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'first_name', 'last_name', 'display_name', 'gender', 'birth_date', 'marital_status', 'seeking', 'security_phrase')
