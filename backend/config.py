from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    gemini_api_key: str
    
    # Polymarket API (adjust based on their actual API structure)
    polymarket_api_base_url: str = "https://clob.polymarket.com"
    polymarket_gamma_api_url: str = "https://gamma-api.polymarket.com"
    
    # App Settings
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    max_requests_per_minute: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()