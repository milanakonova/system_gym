"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Название приложения
    APP_NAME: str = "Gym Management System"
    APP_VERSION: str = "1.0.0"
    
    # База данных
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/gym_sistem"
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

