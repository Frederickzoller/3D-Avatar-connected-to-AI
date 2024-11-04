from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'user__username')
    ordering = ('-updated_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'timestamp', 'content_preview')
    list_filter = ('role', 'timestamp', 'conversation')
    search_fields = ('content', 'conversation__title')
    ordering = ('-timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'