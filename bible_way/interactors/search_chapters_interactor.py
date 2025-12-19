from bible_way.services.elasticsearch_service import ElasticsearchService
from bible_way.presenters.search_chapters_response import SearchChaptersResponse
from rest_framework.response import Response


class SearchChaptersInteractor:
    def __init__(self, es_service: ElasticsearchService, response: SearchChaptersResponse):
        self.es_service = es_service
        self.response = response

    def search_chapters_interactor(self, book_id: str, language_id: str, search_text: str) -> Response:
        # Validation
        if not book_id or (isinstance(book_id, str) and not book_id.strip()):
            return self.response.validation_error_response("Book ID is required")
        
        if not language_id or (isinstance(language_id, str) and not language_id.strip()):
            return self.response.validation_error_response("Language ID is required")
        
        if not search_text or (isinstance(search_text, str) and not search_text.strip()):
            return self.response.validation_error_response("Search text is required")
        
        try:
            # Perform search using Elasticsearch
            results = self.es_service.search_chapters(
                book_id=book_id,
                language_id=language_id,
                search_text=search_text.strip()
            )
            
            return self.response.search_success_response(results)
        except Exception as e:
            return self.response.error_response(f"Search failed: {str(e)}")
