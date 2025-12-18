"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


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
    
    # CORS - может быть строкой (разделенной запятыми) или списком
    CORS_ORIGINS: Union[str, List[str]] = "*"
    
    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Преобразует строку CORS_ORIGINS в список"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Разделяем по запятой и очищаем пробелы
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

