import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MEGAN AI OS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment config
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Ollama AI Configuration
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemma:2b")
    VISION_MODEL_NAME: str = os.getenv("VISION_MODEL_NAME", "llava")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
