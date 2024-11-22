import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.search_url = "https://customsearch.googleapis.com/customsearch/v1"

    def search(self, query: str) -> List[Dict]:
        try:
            params = {
                'key': self.api_key,
                'q': query,
                'cx': 'YOUR_SEARCH_ENGINE_ID',  # Replace with actual search engine ID
                'num': 5,  # Number of results
                'lr': 'lang_ru'  # Russian language results
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            
            results = response.json().get('items', [])
            return [
                {
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                }
                for item in results
            ]
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Search API error: {str(e)}")
            return []
