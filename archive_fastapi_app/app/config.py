from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(description="Database URL")
    api_key: str = Field(description="API key for access to write delete and update routes")
    admin_username: str = Field(description="Admin interface username")
    admin_password: str = Field(description="Admin interface password")
    secret_key: str = Field(description="Secret key for session middleware")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    log_level: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    log_json: bool = Field(default=False, description="Output logs in JSON format (for production)")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def convert_to_async_url(cls, v: str) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy."""
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = {"development", "staging", "production"}
        if v not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(valid_environments)}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level."""
        v = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v


settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to provide Settings instance.
    Using this as a dependency allows for easier testing and follows FastAPI best practices.
    """
    return settings
