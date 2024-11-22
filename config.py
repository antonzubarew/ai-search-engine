import os


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
    GIGACHAT_API_KEY = os.environ.get('GIGACHAT_API_KEY', '')
    MAX_QUERY_LENGTH = 200
    CACHE_TIMEOUT = 3600  # 1 hour
