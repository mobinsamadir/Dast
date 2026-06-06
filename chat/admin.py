from django.contrib import admin
from .models import ChatRoom, Message

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room_type', 'created_at', 'admin')
    list_filter = ('room_type', 'created_at')
    search_fields = ('name',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'short_text', 'timestamp', 'is_flagged')
    list_filter = ('is_flagged', 'timestamp')
    search_fields = ('text', 'sender__phone_number')

    def short_text(self, obj):
        if obj.text:
            return obj.text[:50]
        return "Media"
    short_text.short_description = "Content"

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)

from .models import UserReport

def suspend_reported_user(modeladmin, request, queryset):
    for report in queryset:
        user = report.reported_user
        user.status = 'Blocked'
        user.save()
        report.is_resolved = True
        report.save()

suspend_reported_user.short_description = "مسدود کردن کامل کاربران گزارش شده"

class UserReportAdmin(admin.ModelAdmin):
    actions = [suspend_reported_user]
    list_display = ('id', 'reporter', 'reported_user', 'short_reason', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('reporter__phone_number', 'reported_user__phone_number', 'reason')

    def short_reason(self, obj):
        return obj.reason[:50]
    short_reason.short_description = "Reason"

admin.site.register(UserReport, UserReportAdmin)
