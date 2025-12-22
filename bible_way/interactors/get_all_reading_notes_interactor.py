from bible_way.storage import UserDB
from bible_way.presenters.get_all_reading_notes_response import GetAllReadingNotesResponse
from rest_framework.response import Response
from bible_way.models.book_reading import Chapters
from collections import defaultdict


class GetAllReadingNotesInteractor:
    def __init__(self, storage: UserDB, response: GetAllReadingNotesResponse):
        self.storage = storage
        self.response = response

    def get_all_reading_notes_interactor(self, user_id: str) -> Response:
        if not user_id or not user_id.strip():
            return self.response.validation_error_response("user_id is required")
        
        user_id = user_id.strip()
        
        try:
            reading_notes = self.storage.get_all_reading_notes_by_user(user_id=user_id)
            
            # Group notes by book and chapter
            # Structure: {(book_id, book_name): {(chapter_id or None): [(chapter_id, chapter_name, note_data), ...]}}
            books_dict = defaultdict(lambda: defaultdict(list))
            
            # Cache chapter lookups to avoid repeated database queries
            chapter_cache = {}
            
            for note in reading_notes:
                book_id = str(note.book.book_id)
                book_name = note.book.title
                chapter_id = str(note.chapter_id) if note.chapter_id else None
                
                # Get chapter name if chapter_id exists
                chapter_name = None
                if chapter_id:
                    if chapter_id not in chapter_cache:
                        try:
                            chapter = Chapters.objects.get(chapter_id=note.chapter_id)
                            chapter_cache[chapter_id] = chapter.chapter_name or chapter.title
                        except Chapters.DoesNotExist:
                            chapter_cache[chapter_id] = None
                    chapter_name = chapter_cache[chapter_id]
                
                note_data = {
                    "note_id": str(note.note_id),
                    "content": note.content,
                    "block_id": note.block_id if note.block_id else None,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                    "updated_at": note.updated_at.isoformat() if note.updated_at else None
                }
                
                # Use chapter_id as key, or None for notes without chapters
                chapter_key = chapter_id if chapter_id else None
                books_dict[(book_id, book_name)][chapter_key].append({
                    "chapter_id": chapter_id,
                    "chapter_name": chapter_name,
                    "note_data": note_data
                })
            
            # Format the response structure
            formatted_data = []
            for (book_id, book_name), chapters_dict in books_dict.items():
                chapters_list = []
                
                # Add chapters with notes
                for chapter_key, notes_list in chapters_dict.items():
                    # Extract chapter info from first item (all notes in same chapter have same chapter_id/name)
                    chapter_id = notes_list[0]["chapter_id"] if notes_list else None
                    chapter_name = notes_list[0]["chapter_name"] if notes_list else None
                    
                    # Extract notes (just the note_data part)
                    notes = [item["note_data"] for item in notes_list]
                    
                    chapters_list.append({
                        "chapter_id": chapter_id,
                        "chapter_name": chapter_name,
                        "notes": notes
                    })
                
                formatted_data.append({
                    "book_id": book_id,
                    "book_name": book_name,
                    "chapters": chapters_list
                })
            
            return self.response.reading_notes_retrieved_successfully_response(formatted_data)
        except Exception as e:
            return self.response.error_response(f"Failed to retrieve reading notes: {str(e)}")

