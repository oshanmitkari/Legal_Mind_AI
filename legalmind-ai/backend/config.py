import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///legalmind.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # AI/LLM
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # FAISS
    FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), 'data/faiss_index')
    LAW_DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), 'data/law_documents')
    
    # Registry (simulated Bar Council)
    REGISTRY_PATH = os.path.join(os.path.dirname(__file__), 'data/advocate_registry.json')
    
    # Pagination
    CASES_PER_PAGE = 10
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
