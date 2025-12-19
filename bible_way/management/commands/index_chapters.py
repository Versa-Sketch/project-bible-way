from django.core.management.base import BaseCommand
from bible_way.models.book_reading import Chapters
from bible_way.services.elasticsearch_service import ElasticsearchService


class Command(BaseCommand):
    help = 'Index all existing chapters in Elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--book-id',
            type=str,
            default=None,
            help='Index chapters for a specific book ID only'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-index even if chapter already exists in Elasticsearch'
        )

    def handle(self, *args, **options):
        book_id = options.get('book_id')
        force = options.get('force', False)
        
        es_service = ElasticsearchService()
        
        if not es_service.client:
            self.stdout.write(self.style.ERROR('Elasticsearch client not available. Please check your configuration.'))
            return
        
        # Get chapters to index (use select_related for better performance)
        if book_id:
            chapters = Chapters.objects.select_related('book', 'book__language').filter(book_id=book_id)
            self.stdout.write(f'Indexing chapters for book: {book_id}')
        else:
            chapters = Chapters.objects.select_related('book', 'book__language').all()
            self.stdout.write('Indexing all chapters')
        
        total_chapters = chapters.count()
        self.stdout.write(f'Found {total_chapters} chapters to index')
        
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, chapter in enumerate(chapters, 1):
            try:
                # Get chapter metadata
                metadata = chapter.metadata if chapter.metadata else {}
                chapter_name = metadata.get('chapterName', '') if isinstance(metadata, dict) else ''
                
                # Get book and language info
                book = chapter.book
                language_id = str(book.language.language_id)
                
                # Index the chapter
                success = es_service.index_chapter(
                    chapter_id=str(chapter.chapter_id),
                    book_id=str(book.book_id),
                    language_id=language_id,
                    chapter_name=chapter_name,
                    metadata=metadata if isinstance(metadata, dict) else {}
                )
                
                if success:
                    indexed_count += 1
                else:
                    skipped_count += 1
                
                if idx % 10 == 0:
                    self.stdout.write(f'Processed {idx}/{total_chapters} chapters...')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Error indexing chapter {chapter.chapter_id}: {str(e)}')
                )
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\nIndexing complete!\n'
            f'  Indexed: {indexed_count}\n'
            f'  Skipped: {skipped_count}\n'
            f'  Errors: {error_count}'
        ))
