import os


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
    GIGACHAT_API_KEY = os.environ.get(
        'GIGACHAT_API_KEY',
        'YTRhYWUxNDAtNDA3Yy00NzA5LTk1YzgtOTdlMmY3ODQ0OWY5OmQxNzgxYTM0LThkMzgtNGM0ZC04OTRjLTBkYWM2ODVmNWQ5NA'
    )
    MAX_QUERY_LENGTH = 200
    CACHE_TIMEOUT = 3600  # 1 hour
