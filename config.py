import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-pet-adoption-key-12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'pet_photos')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
