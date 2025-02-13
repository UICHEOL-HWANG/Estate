from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    database_url: str  # ✅ 데이터베이스 URL만 유지

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"  # ✅ .env 파일에서 불러오기

settings = Settings()