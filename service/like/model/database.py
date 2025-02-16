from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings  # ✅ settings에서 database_url 가져오기

# ✅ Database engine 설정
engine = create_engine(settings.database_url)

# ✅ Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ SQLAlchemy Base
Base = declarative_base()

# ✅ FastAPI의 Depends에서 사용할 DB 세션 함수
def get_db():
    db = SessionLocal()
    try:
        yield db  # ✅ db 세션을 FastAPI의 Depends로 사용
    finally:
        db.close()  # ✅ 사용 후 세션 종료
