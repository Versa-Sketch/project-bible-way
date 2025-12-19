from elasticsearch_dsl import Document, Keyword, Text, connections
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def ensure_connection():
    """Ensure elasticsearch-dsl connection is set up"""
    try:
        # Try to get existing connection
        connections.get_connection('default')
        return True
    except KeyError:
        # Connection doesn't exist, create it
        try:
            es_host = getattr(settings, 'ELASTICSEARCH_HOST', 'localhost')
            es_port = getattr(settings, 'ELASTICSEARCH_PORT', 9200)
            use_ssl = getattr(settings, 'ELASTICSEARCH_USE_SSL', False)
            verify_certs = getattr(settings, 'ELASTICSEARCH_VERIFY_CERTS', True)
            username = getattr(settings, 'ELASTICSEARCH_USERNAME', '')
            password = getattr(settings, 'ELASTICSEARCH_PASSWORD', '')
            
            # Build full URL with scheme, host, and port
            scheme = 'https' if use_ssl else 'http'
            es_url = f"{scheme}://{es_host}:{es_port}"
            
            # Build connection config with full URL
            connection_config = {
                'hosts': [es_url],
                'verify_certs': verify_certs,
            }
            
            if username and password:
                connection_config['http_auth'] = (username, password)
            
            connections.create_connection(alias='default', **connection_config)
            logger.info(f"✅ Elasticsearch DSL connection established: {es_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup elasticsearch-dsl connection: {str(e)}")
            return False


class ChapterBlockDocument(Document):
    """Elasticsearch document for individual chapter blocks"""
    
    book_id = Keyword()
    language_id = Keyword()
    chapter_id = Keyword()
    chapter_name = Text(fields={'keyword': Keyword()})
    block_id = Keyword()
    text = Text(analyzer='standard')
    markdown = Text(analyzer='standard')
    
    class Index:
        name = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'chapters_index')
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    def save(self, **kwargs):
        # Ensure connection exists before saving
        ensure_connection()
        # Generate document ID as chapter_id_block_id
        if not self.meta.id:
            self.meta.id = f"{self.chapter_id}_{self.block_id}"
        return super().save(**kwargs)
    
    @classmethod
    def init(cls, index=None, using='default'):
        """Initialize the index, ensuring connection exists first"""
        ensure_connection()
        return super().init(index=index, using=using)
