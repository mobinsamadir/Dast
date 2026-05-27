from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['phone_number', 'display_name', 'status', 'is_staff']
    search_fields = ['phone_number', 'display_name']
    ordering = ['phone_number']

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'display_name', 'gender', 'birth_date', 'marital_status')}),
        ('Physical & Health', {'fields': ('height', 'weight', 'skin_color', 'beauty', 'style', 'health_status')}),
        ('Social & Economic', {'fields': ('income', 'car_status', 'housing_status', 'lifestyle', 'children_count', 'eldest_child_age')}),
        ('Location', {'fields': ('province', 'city', 'location_lat', 'location_lng', 'show_location')}),
        ('Matching Info', {'fields': ('bio', 'spouse_expectation', 'seeking', 'target_gender')}),
        ('Account Status & Security', {'fields': ('status', 'security_phrase', 'profile_picture', 'referral_code', 'referred_by', 'is_totp_enabled')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
