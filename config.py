import os

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Varunloni@12@127.0.0.1/dental_lab_db'
    
class ProductionConfig(Config):
    DEBUG = False
    # For production, consider using environment variables
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:Varunloni@12@127.0.0.1/dental_lab_db'
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Varunloni@12@127.0.0.1/dental_lab_test_db'
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 