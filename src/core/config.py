from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Global application settings."""
    app_name: str = "MCP Framework"
    version: str = "0.1.0"
    debug: bool = False
    
    # Security
    master_key: str = "change-this-in-production-12345678"
    api_key_header: str = "X-MCP-API-KEY"
    
    # Infrastructure
    connectors_dir: str = "src/infrastructure/connectors"
    redis_url: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
