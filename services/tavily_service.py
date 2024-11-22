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
            logger.info(f"Отправляем запрос к Tavily API: {query}")
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            logger.info("Получен ответ от Tavily API")
            
            if not response:
                logger.error("Получен пустой ответ от Tavily API")
                return "Не удалось получить ответ от Tavily API"
                
            if 'error' in response:
                logger.error(f"Ошибка Tavily API: {response['error']}")
                return f"Ошибка при получении ответа: {response.get('error')}"
            
            # Форматируем ответ
            result = "На основе найденной информации:\n\n"
            for item in response.get('results', []):
                result += f"• {item.get('content', '')}\n\n"
            
            return result

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса Tavily: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"
