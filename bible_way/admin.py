from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    UserFollowers,
    Post,
    Media,
    Comment,
    Reaction,
    Share,
    Promotion,
    PromotionImage,
    PrayerRequest,
    Verse,
    Category,
    Language,
    AgeGroup,
    Module,
    Book,
    BookContent,
    ReadingProgress,
    ReadingNote,
    Highlight,
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
    readonly_fields = ('user_id',)
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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'user', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__user_name', 'user__email')
    readonly_fields = ('post_id', 'created_at', 'updated_at')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_id', 'post', 'media_type', 'url', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('post__title', 'url')
    readonly_fields = ('media_id', 'created_at')
    raw_id_fields = ('post',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'post', 'user', 'description_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('description', 'user__user_name', 'post__title')
    readonly_fields = ('comment_id', 'created_at', 'updated_at')
    raw_id_fields = ('post', 'user')
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('reaction_id', 'user', 'reaction_type', 'post', 'comment', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__user_name', 'post__title')
    readonly_fields = ('reaction_id', 'created_at')
    raw_id_fields = ('user', 'post', 'comment')


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('share_id', 'post', 'shared_by', 'shared_to', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'shared_by__user_name', 'shared_to__user_name', 'message')
    readonly_fields = ('share_id', 'created_at')
    raw_id_fields = ('post', 'shared_by', 'shared_to')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('promotion_id', 'title', 'price', 'redirect_link', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'redirect_link')
    readonly_fields = ('promotion_id', 'created_at', 'updated_at')
    raw_id_fields = ('media',)


@admin.register(PromotionImage)
class PromotionImageAdmin(admin.ModelAdmin):
    list_display = ('promotion_image_id', 'promotion', 'image_type', 'order', 'created_at')
    list_filter = ('image_type', 'created_at')
    search_fields = ('promotion__title', 'image_url')
    readonly_fields = ('promotion_image_id', 'created_at')
    raw_id_fields = ('promotion',)


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('prayer_request_id', 'user', 'name', 'email', 'phone_number', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone_number', 'description', 'user__user_name')
    readonly_fields = ('prayer_request_id', 'created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ('verse_id', 'title', 'description_preview', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    readonly_fields = ('verse_id',)
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_preview.short_description = 'Description Preview'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'category', 'age_group', 'language', 'author', 'book_order', 'created_at')
    list_filter = ('category', 'age_group', 'language', 'created_at')
    search_fields = ('title', 'description', 'author')
    readonly_fields = ('book_id', 'created_at', 'updated_at')
    raw_id_fields = ('category', 'age_group', 'language')


@admin.register(BookContent)
class BookContentAdmin(admin.ModelAdmin):
    list_display = ('book_content_id', 'book', 'chapter_number', 'chapter_title', 'content_order', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('chapter_title', 'content', 'book__title')
    readonly_fields = ('book_content_id', 'created_at', 'updated_at')
    raw_id_fields = ('book',)


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('reading_progress_id', 'user', 'book', 'progress_percentage', 'last_read_at', 'updated_at')
    list_filter = ('last_read_at', 'updated_at')
    search_fields = ('user__user_name', 'book__title')
    readonly_fields = ('reading_progress_id', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'book', 'book_content')


@admin.register(ReadingNote)
class ReadingNoteAdmin(admin.ModelAdmin):
    list_display = ('note_id', 'user', 'book', 'book_content', 'note_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('note_text', 'user__user_name', 'book__title')
    readonly_fields = ('note_id', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'book', 'book_content')
    
    def note_preview(self, obj):
        return obj.note_text[:50] + '...' if len(obj.note_text) > 50 else obj.note_text
    note_preview.short_description = 'Note Preview'


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('highlight_id', 'user', 'book', 'book_content', 'color', 'created_at', 'updated_at')
    list_filter = ('color', 'created_at', 'updated_at')
    search_fields = ('highlighted_text', 'user__user_name', 'book__title')
    readonly_fields = ('highlight_id', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'book', 'book_content')
