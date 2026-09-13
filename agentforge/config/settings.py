"""
AgentForge AI Configuration Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global Application Settings"""
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
    TAVILY_API_KEY: str | None = None
    EXA_API_KEY: str | None = None
    
    # Database
    DATABASE_URL: str | None = None
    DIRECT_URL: str | None = None
    
    # Security
    JWT_SECRET: str = "dev-secret-key-change-in-production-min-32-chars-long"
    MAX_TASK_LENGTH: int = 4000
    
    # ADK Configuration
    DEFAULT_LLM_MODEL: str = "gemini-2.5-flash"
    
    @property
    def is_api_key_configured(self) -> bool:
        """Return True if GOOGLE_API_KEY is non-empty and not a placeholder."""
        if not self.GOOGLE_API_KEY:
            return False
        return not (self.GOOGLE_API_KEY.startswith("your_") or "placeholder" in self.GOOGLE_API_KEY.lower())


settings = Settings()
