from bible_way.storage import UserDB
from bible_way.presenters.admin.create_chapters_response import CreateChaptersResponse
from bible_way.storage.s3_utils import upload_file_to_s3 as s3_upload_file
from rest_framework.response import Response
import json
import re


class CreateChaptersInteractor:
    def __init__(self, storage: UserDB, response: CreateChaptersResponse):
        self.storage = storage
        self.response = response

    def _sanitize_book_title(self, title: str) -> str:
        title_lower = title.lower()
        title_no_special = re.sub(r'[^a-z0-9\s]', '', title_lower)
        title_sanitized = re.sub(r'\s+', '_', title_no_special).strip('_')
        return title_sanitized

    def create_chapters_interactor(self, book_id: str, bookdata: str, files_dict: dict) -> Response:
        if not book_id or (isinstance(book_id, str) and not book_id.strip()):
            return self.response.validation_error_response("Book ID is required")
        
        if not bookdata or not bookdata.strip():
            return self.response.validation_error_response("Bookdata is required")
        
        try:
            chapters_data = json.loads(bookdata)
        except json.JSONDecodeError:
            return self.response.validation_error_response("Invalid JSON format for bookdata")
        
        if not isinstance(chapters_data, list):
            return self.response.validation_error_response("Bookdata must be an array")
        
        if len(chapters_data) == 0:
            return self.response.validation_error_response("At least one chapter is required")
        
        try:
            book = self.storage.get_book_by_id(book_id)
        except Exception:
            return self.response.validation_error_response(f"Book with id '{book_id}' does not exist")
        
        for idx, chapter_data in enumerate(chapters_data):
            if not isinstance(chapter_data, dict):
                return self.response.validation_error_response(f"Chapter at index {idx} must be an object")
            
            if not chapter_data.get('title') or not chapter_data.get('title').strip():
                return self.response.validation_error_response(f"Title is required for chapter at index {idx}")
            
            if not chapter_data.get('description') or not chapter_data.get('description').strip():
                return self.response.validation_error_response(f"Description is required for chapter at index {idx}")
        
        if len(files_dict) != len(chapters_data):
            return self.response.validation_error_response(f"Number of files ({len(files_dict)}) must match number of chapters ({len(chapters_data)})")
        
        for idx in range(len(chapters_data)):
            file_key = f'file_{idx}'
            if file_key not in files_dict:
                return self.response.validation_error_response(f"File missing for chapter at index {idx}. Expected '{file_key}'")
        
        try:
            book_title_sanitized = self._sanitize_book_title(book.title)
            max_chapter_number = self.storage.get_max_chapter_number(book_id)
            current_chapter_number = max_chapter_number + 1
            
            created_chapters = []
            
            for idx, chapter_data in enumerate(chapters_data):
                file_key = f'file_{idx}'
                chapter_file = files_dict[file_key]
                
                try:
                    original_filename = chapter_file.name
                    s3_key = f"books/{book_title_sanitized}/chapters/{original_filename}"
                    chapter_url = s3_upload_file(chapter_file, s3_key)
                except Exception as e:
                    return self.response.error_response(f"Failed to upload file for chapter at index {idx}: {str(e)}")
                
                metadata = chapter_data.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}
                
                try:
                    chapter = self.storage.create_chapter(
                        book_id=book_id,
                        title=chapter_data['title'].strip(),
                        description=chapter_data['description'].strip(),
                        chapter_url=chapter_url,
                        chapter_number=current_chapter_number,
                        metadata=metadata if isinstance(metadata, dict) else {}
                    )
                    created_chapters.append(chapter)
                    current_chapter_number += 1
                except Exception as e:
                    return self.response.error_response(f"Failed to create chapter at index {idx}: {str(e)}")
            
            chapters_count = len(created_chapters)
            return self.response.chapters_uploaded_successfully_response(chapters_count, book_id)
        except Exception as e:
            return self.response.error_response(f"Failed to create chapters: {str(e)}")
