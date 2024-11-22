import logging
from typing import List, Dict
from tavily import TavilyClient

logger = logging.getLogger(__name__)

class TavilyService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = TavilyClient(api_key=api_key)

    def get_response(self, query: str, search_results: List[Dict]) -> str:
        try:
            # Отправляем запрос к Tavily API
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            if not response or 'error' in response:
                return "Произошла ошибка при получении ответа от Tavily API"
            
            # Форматируем ответ
            result = "На основе найденной информации:\n\n"
            for item in response.get('results', []):
                result += f"• {item.get('content', '')}\n\n"
            
            return result

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса Tavily: {str(e)}")
            return "Произошла ошибка при обработке запроса к Tavily API. Пожалуйста, попробуйте позже."
