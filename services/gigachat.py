import requests
from typing import List, Dict
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class GigaChatService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    def get_auth_token(self) -> str:
        try:
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
            auth_response = requests.post(
                auth_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "RqUID": str(uuid.uuid4()),
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={"scope": "GIGACHAT_API_PERS"},
                verify=False
            )
            
            if auth_response.status_code == 401:
                logger.error("Ошибка авторизации при получении OAuth токена")
                raise Exception("Ошибка авторизации при получении OAuth токена")
                
            auth_response.raise_for_status()
            return auth_response.json()["access_token"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении OAuth токена: {str(e)}")
            raise Exception("Не удалось получить OAuth токен")
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

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

            # Get OAuth token for authentication
            auth_token = self.get_auth_token()
            
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,  # Add timeout to prevent hanging
                verify=False  # Отключаем проверку SSL сертификата
            )
            
            if response.status_code == 401:
                logger.error("Ошибка авторизации GigaChat API: неверный ключ доступа")
                return "Ошибка авторизации при подключении к GigaChat. Пожалуйста, проверьте настройки API ключа."
                
            if response.status_code == 429:
                logger.error("Превышен лимит запросов к GigaChat API")
                return "Превышен лимит запросов к GigaChat. Пожалуйста, попробуйте позже."
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
                return response_data['choices'][0]['message']['content']
            except (KeyError, json.JSONDecodeError) as e:
                logger.error(f"Ошибка при обработке ответа GigaChat: {str(e)}")
                return "Получен некорректный ответ от сервиса GigaChat. Пожалуйста, попробуйте позже."

        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error при подключении к GigaChat API: {str(e)}")
            return "Ошибка SSL при подключении к GigaChat. Пожалуйста, попробуйте позже."
            
        except requests.exceptions.Timeout:
            logger.error("Timeout при подключении к GigaChat API")
            return "Превышено время ожидания ответа от GigaChat. Пожалуйста, попробуйте позже."
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка подключения к GigaChat API: {str(e)}")
            return "Не удалось подключиться к сервису GigaChat. Пожалуйста, проверьте подключение к интернету и попробуйте позже."
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GigaChat API error: {str(e)}")
            return "Произошла ошибка при обработке запроса к GigaChat. Пожалуйста, попробуйте позже."
