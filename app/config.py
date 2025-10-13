from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(description="Database URL")
    api_key: str = Field(description="API key for access to write delete and update routes")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    model_config = SettingsConfigDict(env_file=".env")

    @field_validator("database_url")
    @classmethod
    def convert_to_async_url(cls, v: str) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy."""
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to provide Settings instance.
    Using this as a dependency allows for easier testing and follows FastAPI best practices.
    """
    return settings
