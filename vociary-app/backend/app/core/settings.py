# backend/app/core/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from urllib.parse import quote_plus

# Remember to ensure 'pydantic-settings' is in your requirements.txt
class Settings(BaseSettings):
    """
    Configuration settings loaded from environment variables or the .env file.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        extra='ignore' 
    )
    
    # --- CORE ---
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # --- AUTH ---
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- DATABASE ---
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """Constructs the full PostgreSQL connection URL."""
        # Note: The database.py file replaces 'postgresql://' with 'postgresql+psycopg://'
        return (
            f"postgresql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- AI SERVICES (Groq Only) ---
    GROQ_API_KEY: str
    LLM_MODEL_NAME: str
    STT_MODEL_NAME: str # Groq-optimized Whisper model name
    
    # --- CORS ---
    FRONTEND_URL: str
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Returns a list of allowed CORS origins."""
        return [self.FRONTEND_URL]


settings = Settings()