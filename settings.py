from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    secret_key: str
    app_name: str = "Youkie"
    sqlalchemy_database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
