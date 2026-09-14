"""
AgentForge AI Configuration Settings
"""
from typing import Any
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global Application Settings with validation and security guards."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "AgentForge AI"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Keys & Services
    GOOGLE_API_KEY: str | None = None
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_PROVIDER: str = "gemini"  # gemini, local, sentence-transformers
    TAVILY_API_KEY: str | None = None
    EXA_API_KEY: str | None = None

    # Database
    DATABASE_URL: str | None = None
    DIRECT_URL: str | None = None

    # Security & JWT Auth
    JWT_SECRET: str = "dev-secret-key-change-in-production-min-64-bytes-long-secure-random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "*"
    MAX_REQUEST_SIZE: int = 10485760  # 10MB max upload size
    MAX_TASK_LENGTH: int = 4000

    @model_validator(mode="after")
    def validate_production_config(self) -> "Settings":
        """Enforce strict configuration rules in production mode."""
        if self.APP_ENV == "production":
            if "dev-secret" in self.JWT_SECRET.lower() or len(self.JWT_SECRET) < 32:
                raise ValueError("Production environment requires a secure JWT_SECRET of at least 32 characters.")
            if not self.is_gemini_configured:
                # Log or warn if production key missing
                pass
        return self

    @property
    def is_gemini_configured(self) -> bool:
        """Return True if GOOGLE_API_KEY is present and not a placeholder."""
        if not self.GOOGLE_API_KEY:
            return False
        k = self.GOOGLE_API_KEY.lower()
        return not (k.startswith("your_") or "placeholder" in k or "your-api-key" in k)

    @property
    def is_postgres_configured(self) -> bool:
        """Return True if DATABASE_URL points to PostgreSQL."""
        if not self.DATABASE_URL:
            return False
        return self.DATABASE_URL.startswith("postgresql") or self.DATABASE_URL.startswith("postgres")

    @property
    def is_local_embedding_configured(self) -> bool:
        """Return True if local embedding fallback is active."""
        return self.EMBEDDING_PROVIDER.lower() in ("local", "sentence-transformers") or not self.is_gemini_configured

    def get_safe_config_summary(self) -> dict[str, Any]:
        """
        Return non-sensitive configuration status summary.
        Never exposes raw API keys, passwords, or JWT secrets.
        """
        return {
            "app_name": self.APP_NAME,
            "app_env": self.APP_ENV,
            "log_level": self.LOG_LEVEL,
            "google_model": self.GOOGLE_MODEL,
            "embedding_provider": self.EMBEDDING_PROVIDER,
            "jwt_algorithm": self.JWT_ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "max_request_size": self.MAX_REQUEST_SIZE,
            "providers": {
                "gemini_api_configured": self.is_gemini_configured,
                "use_vertex_ai": self.GOOGLE_GENAI_USE_VERTEXAI,
                "local_embedding_active": self.is_local_embedding_configured,
                "postgresql_configured": self.is_postgres_configured,
                "tavily_configured": bool(self.TAVILY_API_KEY and not self.TAVILY_API_KEY.startswith("your_")),
            }
        }


settings = Settings()

