from django.db import models
from django.utils import timezone
import uuid
from .user import User


class LanguageChoices(models.TextChoices):
    ENGLISH = 'EN', 'English'
    SPANISH = 'ES', 'Spanish'
    FRENCH = 'FR', 'French'
    GERMAN = 'DE', 'German'
    ITALIAN = 'IT', 'Italian'
    PORTUGUESE = 'PT', 'Portuguese'
    RUSSIAN = 'RU', 'Russian'
    CHINESE_SIMPLIFIED = 'ZH_CN', 'Chinese (Simplified)'
    CHINESE_TRADITIONAL = 'ZH_TW', 'Chinese (Traditional)'
    JAPANESE = 'JA', 'Japanese'
    KOREAN = 'KO', 'Korean'
    ARABIC = 'AR', 'Arabic'
    HINDI = 'HI', 'Hindi'
    BENGALI = 'BN', 'Bengali'
    URDU = 'UR', 'Urdu'
    TURKISH = 'TR', 'Turkish'
    POLISH = 'PL', 'Polish'
    DUTCH = 'NL', 'Dutch'
    GREEK = 'EL', 'Greek'
    HEBREW = 'HE', 'Hebrew'
    SWEDISH = 'SV', 'Swedish'
    NORWEGIAN = 'NO', 'Norwegian'
    DANISH = 'DA', 'Danish'
    FINNISH = 'FI', 'Finnish'
    CZECH = 'CS', 'Czech'
    ROMANIAN = 'RO', 'Romanian'
    HUNGARIAN = 'HU', 'Hungarian'
    THAI = 'TH', 'Thai'
    VIETNAMESE = 'VI', 'Vietnamese'
    INDONESIAN = 'ID', 'Indonesian'
    MALAY = 'MS', 'Malay'
    TAGALOG = 'TL', 'Tagalog'
    SWAHILI = 'SW', 'Swahili'
    AMHARIC = 'AM', 'Amharic'
    YORUBA = 'YO', 'Yoruba'
    ZULU = 'ZU', 'Zulu'
    PERSIAN = 'FA', 'Persian'
    UKRAINIAN = 'UK', 'Ukrainian'
    TAMIL = 'TA', 'Tamil'
    TELUGU = 'TE', 'Telugu'
    MARATHI = 'MR', 'Marathi'
    GUJARATI = 'GU', 'Gujarati'


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
        max_length=6,
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
    book_order = models.IntegerField(default=0, help_text="Order for displaying books in list")
    is_active = models.BooleanField(default=True, help_text="Whether the book is active and visible")
    source_file_url = models.URLField(blank=True, null=True, help_text="URL/path to the source markdown file")
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Additional metadata (e.g., testament: Old/New)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True, default=dict, help_text="Additional metadata (e.g., testament: Old/New)")

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



class ReadingProgress(models.Model):
    reading_progress_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progresses')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_progresses')
    last_position = models.CharField(max_length=255, blank=True)  # e.g., "chapter:verse" or "section:paragraph"
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_reading_progress'
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.user_name} - {self.book.title} ({self.progress_percentage}%)"


class ReadingNote(models.Model):
    note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_notes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_notes')
    note_text = models.TextField()
    position_reference = models.CharField(max_length=255, blank=True)  # Where in content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_reading_note'

    def __str__(self):
        return f"Note {self.note_id} by {self.user.user_name} on {self.book.title}"


class Highlight(models.Model):
    highlight_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='highlights')
    highlighted_text = models.TextField()
    start_position = models.CharField(max_length=255)
    end_position = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bible_way_highlight'

    def __str__(self):
        return f"Highlight {self.highlight_id} by {self.user.user_name} on {self.book.title}"


