from pydantic import BaseModel

class LikeResponse(BaseModel):
    message: str
    like_count: int

class LikeCount(BaseModel):
    post_id : int
    like_count : int

