from django.contrib import admin
from project_chat.models import Conversation, ConversationMember, Message, MessageReadReceipt


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'created_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by',)


@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'user', 'is_admin', 'joined_at', 'left_at', 'last_read_at')
    list_filter = ('is_admin', 'joined_at', 'left_at')
    search_fields = ('conversation__name', 'user__username')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('conversation', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'text_preview', 'file_type', 'file_name', 'created_at', 'edited_at', 'is_deleted_for_everyone')
    list_filter = ('is_deleted_for_everyone', 'file_type', 'created_at', 'edited_at')
    search_fields = ('text', 'sender__username', 'conversation__name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('conversation', 'sender', 'reply_to')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('message__text', 'user__username')
    readonly_fields = ('read_at',)
    raw_id_fields = ('message', 'user')
