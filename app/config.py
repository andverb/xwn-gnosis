from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(description="Database URL")
    api_key: str = Field(description="API key for access to write delete and update routes")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    # model_config = SettingsConfigDict(env_file=".env", env_prefix="gnosis_")

    @field_validator("database_url")
    @classmethod
    def convert_to_async_url(cls, v: str) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for async SQLAlchemy."""
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
