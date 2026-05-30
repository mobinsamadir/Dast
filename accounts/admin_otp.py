from django_otp.admin import OTPAdminSite
from django.contrib import admin
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice

User = get_user_model()

class CustomOTPAdminSite(OTPAdminSite):
    def has_permission(self, request):
        """
        Require TOTP for any superuser/staff
        """
        # If the user is staff/superuser and hasn't passed TOTP verification, deny access to the admin panel
        return super().has_permission(request) and request.user.is_verified()

# We replace the default admin site with our CustomOTPAdminSite
admin.site = CustomOTPAdminSite(name='otpadmin')

# Re-register all apps that were previously registered. We don't have to do it manually if we monkey patch or do it correctly.
# A simpler way to enforce TOTP on the default admin site is to use an AdminSite subclass.
