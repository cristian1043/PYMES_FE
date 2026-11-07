import os
try:
    from dotenv import load_dotenv 
    load_dotenv()
except ImportError:
    pass

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'frontend-secret')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000/api').rstrip('/')
    PORT = int(os.getenv('PORT', 5001))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    DEBUG = True
    
config = {'development': DevelopmentConfig, 'default': DevelopmentConfig}
