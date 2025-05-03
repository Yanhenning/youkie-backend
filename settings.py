import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str
    secret_key: str
    app_name: str = "Youkie"
    sqlalchemy_database_url: str
    production_url: str
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
    sqlalchemy_database_url=os.getenv("SQLALCHEMY_DATABASE_URL", ""),
    production_url=os.getenv("PRODUCTION_URL", ""),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256")
)
