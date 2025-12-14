from bible_way.storage import UserDB
from bible_way.presenters.admin.create_book_response import CreateBookResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from bible_way.utils.markdown_parser import MarkdownBookParser
from bible_way.models import Category, AgeGroup, Language
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
import os
import json


class CreateBookInteractor:
    def __init__(self, storage: UserDB, response: CreateBookResponse):
        self.storage = storage
        self.response = response

    def create_book_interactor(self, markdown_file, category_id: str, age_group_id: str, language_id: str,
                              title: str = None, cover_image_file=None, description: str = None,
                              author: str = None, book_order: int = 0, metadata_str: str = None) -> Response:
        # Validation
        if not markdown_file:
            return self.response.validation_error_response("Markdown file is required")
        
        # Validate file extension
        if not markdown_file.name.lower().endswith('.md'):
            return self.response.validation_error_response("File must be a .md (markdown) file")
        
        # Validate required IDs
        try:
            Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return self.response.validation_error_response(f"Category with id '{category_id}' not found")
        
        try:
            AgeGroup.objects.get(age_group_id=age_group_id)
        except AgeGroup.DoesNotExist:
            return self.response.validation_error_response(f"Age group with id '{age_group_id}' not found")
        
        try:
            Language.objects.get(language_id=language_id)
        except Language.DoesNotExist:
            return self.response.validation_error_response(f"Language with id '{language_id}' not found")
        
        # Parse metadata
        metadata = {}
        if metadata_str:
            try:
                metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
            except json.JSONDecodeError:
                return self.response.validation_error_response("Invalid JSON format for metadata")
        
        try:
            # Read markdown file content
            markdown_file.seek(0)  # Reset file pointer
            markdown_content = markdown_file.read().decode('utf-8')
            filename = markdown_file.name
            
            # Parse markdown
            parser = MarkdownBookParser(markdown_content)
            detected_title = parser.detect_book_title(provided_title=title, filename=filename)
            book_title = title or detected_title
            
            # Parse chapters
            chapters = parser.parse_chapters(book_title=book_title)
            
            if not chapters:
                return self.response.parsing_error_response(
                    "No chapters detected in markdown file. Please ensure the file contains chapter markers."
                )
            
            # Upload markdown file to S3
            markdown_file.seek(0)  # Reset for upload
            book_id_preview = os.urandom(8).hex()
            markdown_key = f"books/markdown/{book_id_preview}/{filename}"
            source_file_url = None
            try:
                source_file_url = s3_upload_file(markdown_file, markdown_key)
            except Exception as e:
                return self.response.error_response(f"Failed to upload markdown file to S3: {str(e)}")
            
            # Upload cover image to S3 if provided
            cover_image_url = None
            if cover_image_file:
                try:
                    cover_image_file.seek(0)
                    cover_key = f"books/cover_images/{book_id_preview}/{cover_image_file.name}"
                    cover_image_url = s3_upload_file(cover_image_file, cover_key)
                except Exception as e:
                    return self.response.error_response(f"Failed to upload cover image: {str(e)}")
            
            # Create book and chapters in transaction
            with transaction.atomic():
                # Create book
                book = self.storage.create_book(
                    title=book_title,
                    category_id=category_id,
                    age_group_id=age_group_id,
                    language_id=language_id,
                    cover_image_url=cover_image_url,
                    description=description or '',
                    author=author or '',
                    book_order=book_order,
                    source_file_name=filename,
                    source_file_url=source_file_url,
                    metadata=metadata
                )
                
                # Prepare chapters data for bulk create
                chapters_data = []
                for chapter in chapters:
                    chapters_data.append({
                        'chapter_number': chapter['chapter_number'],
                        'chapter_title': chapter['chapter_title'],
                        'content': chapter['content'],
                        'content_order': chapter['content_order'],
                        'metadata': chapter.get('metadata', {})
                    })
                
                # Bulk create chapters
                self.storage.bulk_create_book_contents(book, chapters_data)
                
                # Update book parsing status
                total_chapters = len(chapters)
                self.storage.update_book_parsed_status(
                    book_id=str(book.book_id),
                    total_chapters=total_chapters,
                    parsed_at=timezone.now()
                )
            
            # Get parsing info
            parsing_info = parser.get_parsing_info()
            
            # Build response data
            book_data = {
                "book_id": str(book.book_id),
                "title": book.title,
                "detected_title": detected_title,
                "category_id": str(book.category.category_id),
                "age_group_id": str(book.age_group.age_group_id),
                "language_id": str(book.language.language_id),
                "parsing_info": {
                    "pattern_detected": parsing_info.get('pattern_detected'),
                    "chapters_found": total_chapters,
                    "parsing_method": "auto_detected"
                },
                "total_chapters": total_chapters,
                "is_parsed": book.is_parsed,
                "parsed_at": book.parsed_at.isoformat() if book.parsed_at else None,
                "source_file_name": book.source_file_name,
                "source_file_url": book.source_file_url
            }
            
            return self.response.book_created_successfully_response(book_data)
            
        except UnicodeDecodeError:
            return self.response.parsing_error_response("File encoding error. Please ensure the file is UTF-8 encoded.")
        except Exception as e:
            return self.response.error_response(f"Failed to create book: {str(e)}")

