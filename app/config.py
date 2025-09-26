from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str = Field(default="sqlite://rules.db", description="Database URL")
    api_key: str = Field(default="dev-secret-key", description="API key for access to write delete and update routes")
    secret_key: str = Field(default="", description="Secret for cookies signing etc")
    admin_password: str = Field(default="", description="Admin password")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="gnosis_")


settings = Settings()
