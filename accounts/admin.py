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

from .models import WhaleUser

class WhaleUserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'display_name', 'lifetime_coin_burn', 'last_activity', 'send_gift_button', 'send_vip_button']
    search_fields = ['phone_number', 'display_name']
    ordering = ['-lifetime_coin_burn']

    def get_queryset(self, request):
        # Only show users with lifetime_coin_burn > 5000 (Adjust as needed)
        qs = super().get_queryset(request)
        return qs.filter(lifetime_coin_burn__gt=5000)

    def send_gift_button(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        # Link to a custom admin view for sending a gift
        url = reverse('admin:send_whale_gift', args=[obj.pk])
        return format_html('<a class="button" href="{}">ارسال هدیه اختصاصی</a>', url)
    send_gift_button.short_description = 'ارسال هدیه'

    def send_vip_button(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        # Link to a custom admin view for VIP boost
        url = reverse('admin:send_whale_vip', args=[obj.pk])
        return format_html('<a class="button" href="{}">افزایش ویژه (VIP)</a>', url)
    send_vip_button.short_description = 'ارسال VIP'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/send_gift/', self.admin_site.admin_view(self.send_gift_view), name='send_whale_gift'),
            path('<int:user_id>/send_vip/', self.admin_site.admin_view(self.send_vip_view), name='send_whale_vip'),
        ]
        return custom_urls + urls

    def send_gift_view(self, request, user_id):
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        # Placeholder for sending a custom gift logic
        user = self.get_object(request, user_id)
        if user:
            messages.success(request, f'هدیه اختصاصی برای {user.display_name} ارسال شد.')
        return HttpResponseRedirect('../')

    def send_vip_view(self, request, user_id):
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        # Placeholder for sending VIP logic
        user = self.get_object(request, user_id)
        if user:
            messages.success(request, f'اشتراک ویژه برای {user.display_name} تمدید شد.')
        return HttpResponseRedirect('../')

admin.site.register(WhaleUser, WhaleUserAdmin)
