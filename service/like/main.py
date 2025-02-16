from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from router.board_like_router import board_like_router
from router.comment_like_router import comment_like_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
)

app.include_router(board_like_router)
app.include_router(comment_like_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

