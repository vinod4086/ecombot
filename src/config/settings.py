"""Application settings and configuration"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    langsmith_api_key: Optional[str] = os.getenv("LANGSMITH_API_KEY")

    # Database Configuration
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "ecombot_db")
    postgres_user: str = os.getenv("POSTGRES_USER", "ecombot_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "ecombot_password")

    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "redis_password")

    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openrouter")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    llm_model: str = os.getenv("LLM_MODEL", "mistral-7b")
    litellm_proxy_url: str = os.getenv("LITELLM_PROXY_URL", "http://localhost:8000")

    # ChromaDB Configuration
    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))

    # Application
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def postgres_dsn(self) -> str:
        """PostgreSQL connection string"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"

    @property
    def chroma_url(self) -> str:
        """ChromaDB connection URL"""
        return f"http://{self.chroma_host}:{self.chroma_port}"


# Global settings instance
settings = Settings()
