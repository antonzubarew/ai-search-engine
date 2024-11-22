from duckduckgo_search import DDGS
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, api_key: str = None):  # api_key parameter kept for compatibility
        self.ddgs = DDGS()

    def search(self, query: str) -> List[Dict]:
        try:
            # Search with DuckDuckGo
            results = list(self.ddgs.text(
                query,
                region='ru-ru',  # Russian region
                safesearch='off',
                max_results=5
            ))
            
            return [
                {
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'link': result.get('link', '')
                }
                for result in results
            ]
        
        except Exception as e:
            logger.error(f"DuckDuckGo Search error: {str(e)}")
            return []
