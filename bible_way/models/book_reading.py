from django.db import models
from django.utils import timezone
import uuid
from .user import User


class LanguageChoices(models.TextChoices):
    ENGLISH = 'EN', 'English'
    GERMAN = 'DE', 'German'
    FRENCH = 'FR', 'French'
    SPANISH = 'ES', 'Spanish'
    ITALIAN = 'IT', 'Italian'
    PORTUGUESE = 'PT', 'Portuguese'
    RUSSIAN = 'RU', 'Russian'
    DUTCH = 'NL', 'Dutch'
    SWEDISH = 'SV', 'Swedish'
    POLISH = 'PL', 'Polish'
    GREEK = 'EL', 'Greek'
    ASSAMESE = 'AS', 'Assamese'
    BENGALI = 'BN', 'Bengali'
    BODO = 'BRX', 'Bodo'
    HINDI = 'HI', 'Hindi'
    GUJARATI = 'GU', 'Gujarati'
    KANNADA = 'KN', 'Kannada'
    KASHMIRI = 'KS', 'Kashmiri'
    KONKANI = 'KOK', 'Konkani'
    MAITHILI = 'MAI', 'Maithili'
    MALAYALAM = 'ML', 'Malayalam'
    MANIPURI = 'MNI', 'Manipuri'
    MARATHI = 'MR', 'Marathi'
    NEPALI = 'NE', 'Nepali'
    ODIA = 'OR', 'Odia'
    PUNJABI = 'PA', 'Punjabi'
    SANSKRIT = 'SA', 'Sanskrit'
    SANTALI = 'SAT', 'Santali'
    SINDHI = 'SD', 'Sindhi'
    TAMIL = 'TA', 'Tamil'
    TELUGU = 'TE', 'Telugu'
    URDU = 'UR', 'Urdu'
    DOGRI = 'DOG', 'Dogri'
    SWAHILI = 'SW', 'Swahili'
    AFRIKAANS = 'AF', 'Afrikaans'
    HAUSA = 'HA', 'Hausa'
    ZULU = 'ZU', 'Zulu'
    YORUBA = 'YO', 'Yoruba'
    CHINESE_SIMPLIFIED = 'ZH_CN', 'Chinese (Simplified)'
    ARABIC = 'AR', 'Arabic'


class CategoryChoices(models.TextChoices):
    SEGREGATE_BIBLES = 'SEGREGATE_BIBLES', 'Segregate Bibles'
    BIBLE_READER = 'BIBLE_READER', 'BibleReader'


class AgeGroupChoices(models.TextChoices):
    CHILDREN = 'CHILDREN', 'Children'
    TEEN = 'TEEN', 'Teen'
    ADULT_1 = 'ADULT_1', 'Adult 1'
    ADULT_2 = 'ADULT_2', 'Adult 2'
    ADULT_3 = 'ADULT_3', 'Adult 3'
    ADULT_4 = 'ADULT_4', 'Adult 4'
    ADULT_5 = 'ADULT_5', 'Adult 5'
    SENIOR = 'SENIOR', 'Senior'
    ALL = 'ALL', 'All'


class Category(models.Model):
    category_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(
        max_length=35,
        choices=CategoryChoices.choices
    )
    cover_image_url = models.URLField(blank=True, null=True, help_text="Cover image for dashboard section")
    description = models.TextField(blank=True, help_text="Description of the category")
    display_order = models.IntegerField(default=0, help_text="Order for displaying categories in dashboard")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_category'
        ordering = ['display_order', 'category_name']

    def __str__(self):
        return self.get_category_name_display()


class Language(models.Model):
    language_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    language_name = models.CharField(
        max_length=10,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH
    )

    def __str__(self):
        return self.get_language_name_display()


class AgeGroup(models.Model):
    age_group_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    age_group_name = models.CharField(
        max_length=10,
        choices=AgeGroupChoices.choices
    )
    cover_image_url = models.URLField(blank=True, null=True, help_text="Cover image for age group dashboard (used in SEGREGATE_BIBLES)")
    description = models.TextField(blank=True, help_text="Description of the age group")
    display_order = models.IntegerField(default=0, help_text="Order for displaying age groups in dashboard")
    age_group_created_at = models.DateTimeField(auto_now_add=True)
    age_group_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_age_group'
        ordering = ['display_order', 'age_group_name']

    def __str__(self):
        return self.get_age_group_name_display()


class Book(models.Model):
    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE, related_name='books')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='books')
    cover_image_url = models.URLField(blank=True, null=True)
    book_order = models.IntegerField(default=0, help_text="Order for displaying books in list", null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Whether the book is active and visible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_book'
        ordering = ['book_order', 'title']
        indexes = [
            models.Index(fields=['category', 'age_group']),
            models.Index(fields=['category', 'language']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        category_name = str(self.category) if self.category else "No Category"
        return f"{self.title} - {category_name}"

class Chapters(models.Model):
    chapter_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    chapter_number = models.IntegerField(default=0, help_text="Chapter number", null=True, blank=True)
    chapter_name = models.CharField(max_length=255, blank=True, null=True)
    chapter_url = models.URLField(blank=True, null=True, help_text="URL/path to the chapter file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Additional metadata (e.g., testament: Old/New)")
    video_url = models.URLField(blank=True, null=True, help_text="URL/path to the video file")

    class Meta:
        db_table = 'bible_way_chapters'

    def __str__(self):
        return f"{self.title} - {self.book.title}"


class ReadingProgress(models.Model):
    reading_progress_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progresses')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_progresses')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    block_id = models.CharField(max_length=255, blank=True, null=True)
    chapter_id = models.ForeignKey(Chapters, on_delete=models.CASCADE, related_name='reading_progresses',blank=True, null=True)
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_reading_progress'
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.progress_percentage}%)"


class ReadingNote(models.Model):
    note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_notes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_notes')
    chapter_id = models.UUIDField(blank=True, null=True)
    block_id = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_reading_note'

    def __str__(self):
        return f"Note {self.note_id} by {self.user.username} on {self.book.title}"


class Highlight(models.Model):
    highlight_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='highlights')
    chapter = models.ForeignKey(Chapters, on_delete=models.CASCADE, related_name='highlights',default=None)
    start_block_id = models.CharField(max_length=255, blank=True, null=True)
    end_block_id = models.CharField(max_length=255, blank=True, null=True)
    start_offset = models.CharField(max_length=255)
    end_offset = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'bible_way_highlight'

    def __str__(self):
        return f"Highlight {self.highlight_id} by {self.user.username} on {self.book.title}"

class Bookmark(models.Model):
    bookmark_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_bookmark'

    def __str__(self):
        return f"Bookmark {self.bookmark_id} by {self.user.username} on {self.book.title}"
    