import os
from dotenv import load_dotenv 

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'frontend-secret')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000/api').rstrip('/')
    PORT = int(os.getenv('PORT', 5001))

class DevelopmentConfig(Config):
    DEBUG = True
    
config = {'development': DevelopmentConfig, 'default': DevelopmentConfig}