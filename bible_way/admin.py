from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    UserFollowers,
    Category,
    Language,
    AgeGroup,
    Module,
    Conversation,
    ConversationMember,
    Message,
    MessageReadReceipt,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('user_name', 'email', 'country', 'age', 'preferred_language', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'country', 'preferred_language')
    search_fields = ('user_name', 'email', 'country')
    ordering = ('user_name',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_id', 'user_name', 'country', 'age', 'preferred_language')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_name', 'email', 'country', 'age', 'preferred_language')}),
    )


@admin.register(UserFollowers)
class UserFollowersAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower_id', 'followed_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower_id__user_name', 'followed_id__user_name')
    readonly_fields = ('id', 'created_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'category_name', 'get_category_name_display')
    search_fields = ('category_name',)
    readonly_fields = ('category_id',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_id', 'language_name', 'get_language_name_display')
    search_fields = ('language_name',)
    readonly_fields = ('language_id',)


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('age_group_id', 'age_group_name', 'get_age_group_name_display', 'age_group_created_at', 'age_group_updated_at')
    list_filter = ('age_group_name', 'age_group_created_at')
    search_fields = ('age_group_name',)
    readonly_fields = ('age_group_id', 'age_group_created_at', 'age_group_updated_at')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_id', 'title', 'category', 'age_group', 'language', 'created_at')
    list_filter = ('category', 'age_group', 'language', 'created_at')
    search_fields = ('title', 'description', 'text_content')
    readonly_fields = ('module_id', 'created_at')
    raw_id_fields = ('category', 'age_group', 'language')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'created_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__user_name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by',)


@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'user', 'is_admin', 'joined_at', 'left_at', 'last_read_at')
    list_filter = ('is_admin', 'joined_at', 'left_at')
    search_fields = ('conversation__name', 'user__user_name')
    readonly_fields = ('joined_at',)
    raw_id_fields = ('conversation', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'text_preview', 'created_at', 'edited_at', 'is_deleted_for_everyone')
    list_filter = ('is_deleted_for_everyone', 'created_at', 'edited_at')
    search_fields = ('text', 'sender__user_name', 'conversation__name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('conversation', 'sender', 'reply_to')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('message__text', 'user__user_name')
    readonly_fields = ('read_at',)
    raw_id_fields = ('message', 'user')
