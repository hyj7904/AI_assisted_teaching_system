import os

class Config:
    # 使用固定的密钥，避免每次重启变化
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'teaching-assistant-system-secret-key-2023'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///teaching_assistant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 文件大小限制
