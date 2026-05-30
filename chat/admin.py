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
