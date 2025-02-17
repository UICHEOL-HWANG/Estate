from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db

from dto.like import LikeResponse, LikeCount
from util.auth import get_user_info
from model.models import PostLike, CommentLike

board_like_router = APIRouter(
    prefix="/board_like",
    tags=["board_like"],
    responses={404: {"description": "Not found"}},
)

@board_like_router.post("/post/{post_id}/toggle", response_model=LikeResponse)
async def toggle_like_post(
        post_id: int,
        authorization: str = Header(...),
        db: Session = Depends(get_db)
):
    """
    ✅ 게시글 좋아요 토글 API
    - 좋아요가 눌려있으면 취소
    - 좋아요가 없으면 추가
    """

    # ✅ JWT 토큰에서 유저 정보 가져오기
    user_info = get_user_info(authorization)
    user_id = user_info['id']

    # ✅ 현재 좋아요 여부 확인
    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()

    if existing_like:
        # ✅ 좋아요 취소
        db.delete(existing_like)
        db.commit()
        action = "취소됨"
    else:
        # ✅ 좋아요 추가
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        db.commit()
        action = "추가됨"

    # ✅ 업데이트된 좋아요 개수 반환
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()

    return LikeResponse(
        message=f"게시글 좋아요 {action}.",
        like_count=like_count
    )


@board_like_router.get("/post/{post_id}/count")
async def get_like_count(post_id: int, db: Session = Depends(get_db), response_model=LikeCount):
    """
    특정 게시글의 좋아요 개수 조회
    """
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return {"post_id": post_id, "like_count": like_count}


@board_like_router.get("/post/{post_id}/status", response_model=LikeResponse)
async def get_like_status(
        post_id: int,
        authorization: str = Header(...),
        db: Session = Depends(get_db)
):
    """ 현재 유저가 좋아요를 눌렀는지 확인 """
    user_info = get_user_info(authorization)
    user_id = user_info['id']

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == user_id
    ).first()

    liked = bool(existing_like)
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()

    return LikeResponse(message="좋아요 상태 조회", like_count=like_count, liked=liked)