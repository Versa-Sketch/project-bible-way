from bible_way.storage import UserDB
from bible_way.presenters.admin.update_book_metadata_response import UpdateBookMetadataResponse
from bible_way.models import Book
from rest_framework.response import Response
import json


class UpdateBookMetadataInteractor:
    def __init__(self, storage: UserDB, response: UpdateBookMetadataResponse):
        self.storage = storage
        self.response = response

    def update_book_metadata_interactor(self, book_id: str, metadata: dict) -> Response:
        # Validation
        if not book_id:
            return self.response.validation_error_response("Book ID is required")
        
        if metadata is None:
            return self.response.validation_error_response("Metadata is required")
        
        # Validate metadata is a dictionary
        if not isinstance(metadata, dict):
            return self.response.validation_error_response("Metadata must be a valid JSON object")
        
        # Validate book exists
        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            return self.response.validation_error_response(f"Book with id '{book_id}' does not exist")
        except Exception as e:
            return self.response.error_response(f"Error retrieving book: {str(e)}")
        
        try:
            # Update book metadata
            updated_book = self.storage.update_book_metadata(book_id=book_id, metadata=metadata)
            
            return self.response.metadata_updated_successfully_response()
        except Exception as e:
            return self.response.error_response(f"Failed to update book metadata: {str(e)}")

