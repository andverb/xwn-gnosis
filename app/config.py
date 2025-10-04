from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(description="Database URL")
    api_key: str = Field(description="API key for access to write delete and update routes")
    environment: str = Field(default="development", description="Environment: development, staging, production")
    model_config = SettingsConfigDict(env_file=".env", env_prefix="gnosis_")


settings = Settings()
