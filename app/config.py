from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str = Field(default="sqlite://rules.db", description="Database URL")
    api_key: str = Field(default="dev-secret-key", description="API key for auth")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="gnosis_")


settings = Settings()
