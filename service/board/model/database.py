from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings

# Database engine
engine = create_engine(settings.database_url)

# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db  # db 세션을 FastAPI의 Depends로 사용하도록 yield
    finally:
        db.close()  # 사용 후 세션 종료
