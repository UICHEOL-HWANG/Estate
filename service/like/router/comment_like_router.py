from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db

import redis

from dto.like import LikeResponse, LikeCount
from util.auth import get_user_info
from model.models import PostLike, CommentLike

comment_like_router = APIRouter(
    prefix="/comment_like",
    tags=["comment_like"],
    responses={404: {"description": "Not found"}},
)


r = redis.Redis(host="localhost", port=6378, decode_responses=True)
CACHE_EXPIRE_TIME = 300  # ✅ 5분 TTL

# ✅ 댓글 좋아요 토글 API
@comment_like_router.post("/comment/{comment_id}/", response_model=LikeResponse)
async def toggle_like_comment(
        comment_id: int,
        authorization: str = Header(...),
        db: Session = Depends(get_db)
):
    """
    ✅ 댓글 좋아요 토글 (인증 + Redis Stream 사용)
    """
    user_info = await get_user_info(authorization)
    user_id = user_info["id"]

    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == user_id
    ).first()

    if existing_like:
        # ✅ 좋아요 취소
        db.delete(existing_like)
        db.commit()
        message = "댓글 좋아요가 취소되었습니다."
    else:
        # ✅ 좋아요 추가
        new_like = CommentLike(comment_id=comment_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        message = "댓글에 좋아요가 추가되었습니다."

    # ✅ Redis 캐시 업데이트
    like_cache_key = f"like_count:comment:{comment_id}"
    new_like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()
    r.setex(like_cache_key, CACHE_EXPIRE_TIME, new_like_count)

    return LikeResponse(message=message, like_count=new_like_count)


@comment_like_router.get("/comment/{comment_id}/count", response_model=LikeResponse)
async def get_comment_like_count(comment_id: int, db: Session = Depends(get_db)):
    """
    ✅ 댓글 좋아요 개수 조회 (Redis 캐싱 적용)
    """
    like_cache_key = f"like_count:comment:{comment_id}"
    cached_count = r.get(like_cache_key)

    if cached_count is not None:
        print(f"📌 Redis 캐시에서 댓글 {comment_id} 좋아요 개수 조회")
        return LikeResponse(message="댓글 좋아요 개수 조회 성공 (캐싱)", like_count=int(cached_count))

    # ✅ Redis에 없으면 DB 조회 후 캐싱
    like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()
    r.setex(like_cache_key, CACHE_EXPIRE_TIME, like_count)  # ✅ 5분 TTL 설정

    return LikeResponse(message="댓글 좋아요 개수 조회 성공", like_count=like_count)

