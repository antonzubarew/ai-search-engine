import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class GigaChatService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.gigachat.ai/v1/chat/completions"  # Replace with actual API endpoint

    def get_response(self, query: str, search_results: List[Dict]) -> str:
        try:
            # Format context from search results
            context = "\n".join([
                f"Источник: {result['title']}\n{result['snippet']}"
                for result in search_results
            ])

            # Prepare prompt
            prompt = f"""
            Вопрос: {query}
            
            Контекст из поиска:
            {context}
            
            Пожалуйста, предоставьте подробный ответ на русском языке, основываясь на предоставленном контексте.
            """

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            return response.json()['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            logger.error(f"GigaChat API error: {str(e)}")
            return "Извините, произошла ошибка при обработке запроса."
