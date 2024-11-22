import logging
from typing import List, Dict
from gigachat import GigaChat

logger = logging.getLogger(__name__)

class GigaChatService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            # Инициализация клиента GigaChat с отключенной проверкой SSL
            self.client = GigaChat(credentials=api_key, verify_ssl_certs=False)
            logger.info("GigaChat клиент успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации GigaChat клиента: {str(e)}")
            self.client = None

    def get_response(self, query: str, search_results: List[Dict]) -> str:
        if not self.client:
            return "Ошибка: Клиент GigaChat не инициализирован"

        try:
            # Формируем контекст из результатов поиска
            context = "\n".join([
                f"Источник: {result['title']}\n{result['snippet']}"
                for result in search_results
            ])

            # Формируем системный промпт
            system_prompt = "Вы - русскоязычный ассистент, который помогает находить информацию и отвечать на вопросы. Используйте предоставленный контекст для формирования ответа."

            # Формируем пользовательский промпт
            user_prompt = f'''
            Вопрос: {query}
            
            Контекст из поиска:
            {context}
            
            Пожалуйста, предоставьте подробный ответ на русском языке.
            '''

            # Отправляем запрос к API
            logger.info("Отправляем запрос к GigaChat API")
            response = self.client.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])

            logger.info("Получен успешный ответ от GigaChat API")
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка при обработке запроса GigaChat: {error_msg}")
            
            if "auth" in error_msg.lower():
                return "Ошибка авторизации при подключении к GigaChat. Пожалуйста, проверьте настройки API ключа."
            elif "timeout" in error_msg.lower():
                return "Превышено время ожидания ответа от GigaChat. Пожалуйста, попробуйте позже."
            elif "rate" in error_msg.lower():
                return "Превышен лимит запросов к GigaChat. Пожалуйста, попробуйте позже."
            else:
                return "Произошла ошибка при обработке запроса к GigaChat. Пожалуйста, попробуйте позже."