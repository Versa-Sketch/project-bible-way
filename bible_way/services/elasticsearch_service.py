from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, RequestError
from elasticsearch_dsl import connections
from bible_way.services.documents import ChapterBlockDocument
import logging

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for managing Elasticsearch operations for chapter search"""
    
    def __init__(self):
        self.client = self._get_client()
        self.index_name = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'chapters_index')
        self._setup_connection()
        self._ensure_index_exists()
    
    def _get_client(self):
        """Initialize and return Elasticsearch client"""
        try:
            es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'localhost')
            es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
            use_ssl = getattr(settings, 'ELASTICSEARCH_USE_SSL', False)
            verify_certs = getattr(settings, 'ELASTICSEARCH_VERIFY_CERTS', True)
            username = getattr(settings, 'ELASTICSEARCH_USERNAME', '')
            password = getattr(settings, 'ELASTICSEARCH_PASSWORD', '')
            
            scheme = 'https' if use_ssl else 'http'
            # Build full URL with scheme, host, and port
            es_url = f"{scheme}://{es_host}:{es_port}"
            logger.info(f"Connecting to Elasticsearch at {es_url} (Verify certs: {verify_certs})")
            
            # Disable SSL warnings if not verifying certificates
            if use_ssl and not verify_certs:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Build Elasticsearch client config with full URL
            es_config = {
                'hosts': [es_url],
                'verify_certs': verify_certs,
            }
            
            # Add authentication if provided
            if username and password:
                es_config['basic_auth'] = (username, password)
            
            client = Elasticsearch(**es_config)
            
            # Test connection immediately
            try:
                info = client.info()
                logger.info(f"✅ Elasticsearch client connection successful - Cluster: {info['cluster_name']}, Version: {info['version']['number']}")
            except Exception as conn_error:
                logger.error(f"❌ Initial connection test failed: {conn_error}")
                return None
            
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _setup_connection(self):
        """Setup elasticsearch-dsl connection"""
        if not self.client:
            logger.warning("Elasticsearch client not available, skipping DSL connection setup")
            return
        
        try:
            # Configure elasticsearch-dsl connection
            es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'localhost')
            es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
            use_ssl = getattr(settings, 'ELASTICSEARCH_USE_SSL', False)
            verify_certs = getattr(settings, 'ELASTICSEARCH_VERIFY_CERTS', True)
            username = getattr(settings, 'ELASTICSEARCH_USERNAME', '')
            password = getattr(settings, 'ELASTICSEARCH_PASSWORD', '')
            
            # Remove existing connection if it exists
            try:
                connections.remove_connection('default')
            except:
                pass
            
            # Build full URL with scheme, host, and port
            scheme = 'https' if use_ssl else 'http'
            es_url = f"{scheme}://{es_host}:{es_port}"
            
            # Build connection config with full URL
            connection_config = {
                'hosts': [es_url],
                'verify_certs': verify_certs,
            }
            
            # Add authentication if provided
            if username and password:
                connection_config['http_auth'] = (username, password)
            
            # Create new connection
            connections.create_connection(alias='default', **connection_config)
            logger.info(f"✅ Elasticsearch DSL connection established: {es_url}")
        except Exception as e:
            logger.error(f"❌ Failed to setup elasticsearch-dsl connection: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _ensure_index_exists(self):
        """Create index with proper mapping if it doesn't exist"""
        if not self.client:
            logger.warning("Elasticsearch client not available, skipping index creation")
            return
        
        try:
            # Check if index exists using the client
            if not self.client.indices.exists(index=self.index_name):
                # Ensure connection is set up before creating index
                self._setup_connection()
                
                # Create index using the document mapping
                try:
                    # Ensure connection is set up
                    from bible_way.services.documents import ensure_connection
                    ensure_connection()
                    ChapterBlockDocument.init(using='default')
                    logger.info(f"Created Elasticsearch index: {self.index_name}")
                except Exception as init_error:
                    # Fallback: create index manually if DSL fails
                    logger.warning(f"DSL init failed, creating index manually: {str(init_error)}")
                    mapping = {
                        "mappings": {
                            "properties": {
                                "book_id": {"type": "keyword"},
                                "language_id": {"type": "keyword"},
                                "chapter_id": {"type": "keyword"},
                                "chapter_name": {
                                    "type": "text",
                                    "fields": {"keyword": {"type": "keyword"}}
                                },
                                "block_id": {"type": "keyword"},
                                "text": {"type": "text", "analyzer": "standard"},
                                "markdown": {"type": "text", "analyzer": "standard"}
                            }
                        }
                    }
                    self.client.indices.create(index=self.index_name, body=mapping)
                    logger.info(f"Created Elasticsearch index manually: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch index: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    def index_chapter(self, chapter_id: str, book_id: str, language_id: str, 
                      chapter_name: str, metadata: dict):
        """Index all blocks of a chapter in Elasticsearch"""
        if not self.client:
            logger.warning("Elasticsearch client not available, skipping indexing")
            return False
        
        try:
            # Extract blocks from metadata
            blocks = metadata.get('blocks', [])
            
            if not blocks:
                logger.warning(f"No blocks found for chapter {chapter_id}")
                return True
            
            # Ensure connection exists before indexing
            from bible_way.services.documents import ensure_connection
            ensure_connection()
            
            indexed_count = 0
            for block in blocks:
                try:
                    block_id = block.get('blockId', '')
                    if not block_id:
                        continue
                    
                    doc = ChapterBlockDocument(
                        meta={'id': f"{chapter_id}_{block_id}"},
                        book_id=str(book_id),
                        language_id=str(language_id),
                        chapter_id=str(chapter_id),
                        chapter_name=chapter_name or "",
                        block_id=block_id,
                        text=block.get('text', ''),
                        markdown=block.get('markdown', '')
                    )
                    doc.save(using='default')
                    indexed_count += 1
                except Exception as block_error:
                    logger.warning(f"Failed to index block {block.get('blockId', '')} for chapter {chapter_id}: {str(block_error)}")
                    continue
            
            logger.info(f"Indexed {indexed_count} blocks for chapter {chapter_id} in Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Failed to index chapter {chapter_id}: {str(e)}")
            return False
    
    def update_chapter_index(self, chapter_id: str, book_id: str, language_id: str,
                            chapter_name: str, metadata: dict):
        """Update an existing chapter document in Elasticsearch"""
        return self.index_chapter(chapter_id, book_id, language_id, chapter_name, metadata)
    
    def delete_chapter_index(self, chapter_id: str):
        """Delete all blocks of a chapter from Elasticsearch"""
        if not self.client:
            logger.warning("Elasticsearch client not available, skipping deletion")
            return False
        
        try:
            # Ensure connection exists
            from bible_way.services.documents import ensure_connection
            ensure_connection()
            
            # Delete all blocks for this chapter
            from elasticsearch_dsl import Q
            search = ChapterBlockDocument.search(using='default')
            search = search.filter('term', chapter_id=str(chapter_id))
            
            deleted_count = 0
            for doc in search.scan():
                doc.delete(using='default')
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} blocks for chapter {chapter_id} from Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chapter {chapter_id}: {str(e)}")
            return False
    
    def search_chapters(self, book_id: str, language_id: str, search_text: str, 
                       from_index: int = 0, size: int = 100):
        """
        Search for text within chapter blocks with highlighting
        
        Args:
            book_id: Filter by book ID
            language_id: Filter by language ID
            search_text: Text to search for
            from_index: Starting index for pagination
            size: Number of results to return
        
        Returns:
            List of matching blocks with chapter context and highlighted text
        """
        if not self.client:
            logger.warning("Elasticsearch client not available, returning empty results")
            return []
        
        try:
            # Ensure connection exists
            from bible_way.services.documents import ensure_connection
            ensure_connection()
            
            from elasticsearch_dsl import Q
            
            # Search using elasticsearch-dsl
            search = ChapterBlockDocument.search(using='default')
            
            # Build query: match text and filter by book_id and language_id
            search = search.query(
                Q('match', text={'query': search_text, 'fuzziness': 'AUTO'}) &
                Q('term', book_id=str(book_id)) &
                Q('term', language_id=str(language_id))
            )
            
            # Add highlighting configuration
            search = search.highlight(
                'text',                          # Field to highlight
                pre_tags=['<mark>'],             # Opening tag for matched text
                post_tags=['</mark>'],           # Closing tag for matched text
                fragment_size=150,               # Characters around each match
                number_of_fragments=3,           # Maximum fragments to return
                require_field_match=True         # Only highlight if field matches
            )
            
            # Apply pagination
            search = search[from_index:from_index + size]
            
            # Execute search
            response = search.execute()
            
            results = []
            for hit in response:
                # Get highlighted text if available, otherwise use original text
                highlighted_text = None
                if hasattr(hit.meta, 'highlight') and hasattr(hit.meta.highlight, 'text'):
                    # Join all highlight fragments with "..."
                    highlighted_text = ' ... '.join(hit.meta.highlight.text)
                
                result = {
                    "block_id": hit.block_id,
                    "text": hit.text,
                    "chapter_id": hit.chapter_id,
                    "chapter_name": hit.chapter_name
                }
                
                # Add highlighted_text only if highlights are available
                if highlighted_text:
                    result["highlighted_text"] = highlighted_text
                
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {str(e)}")
            return []
