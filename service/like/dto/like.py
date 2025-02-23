from pydantic import BaseModel

class LikeResponse(BaseModel):
    message: str
    like_count: int

class LikeCount(BaseModel):
    post_id: int
    like_count: int

    class Config:
        from_attributes = True  # ✅ ORM에서 변환 가능하도록 설정
