from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from router.board_router import board_router
from router.comment_router import comment_router
from util.board_consumer import BoardConsumer

# ✅ Lifespan 이벤트 핸들러 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [board_service] FastAPI 서버 시작: Redis Consumer 실행 중...")
    consumer = BoardConsumer()
    consumer.start()  # ✅ Redis Consumer 실행
    yield  # 🚀 앱이 실행된 후 여기까지 실행됨
    print("❌ [board_service] FastAPI 서버 종료")

# ✅ FastAPI 인스턴스 생성 (lifespan 추가)
app = FastAPI(lifespan=lifespan)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
)

# ✅ 라우터 등록
app.include_router(board_router)
app.include_router(comment_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
