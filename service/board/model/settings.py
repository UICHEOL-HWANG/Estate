from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"

settings = Settings()