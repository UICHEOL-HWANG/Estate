from fastapi import APIRouter, Depends, HTTPException
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

@board_like_router.post("/post/{post_id}/", response_model=LikeResponse)
async def like_post(
        post_id : int,
        authorization : str,
        db : Session = Depends(get_db)
):

    # JWT
    user_info = get_user_info(authorization)
    user_id = user_info['id']

    existing_like = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == user_id).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="이미 좋아요를 눌렀습니다.")

    # ✅ 새로운 좋아요 추가
    new_like = PostLike(post_id=post_id, user_id=user_id)
    db.add(new_like)
    db.commit()

    # ✅ 업데이트된 좋아요 개수 반환
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return LikeResponse(message="게시글에 좋아요가 추가되었습니다.", like_count=like_count)


@board_like_router.get("/post/{post_id}/count")
async def get_like_count(post_id: int, db: Session = Depends(get_db), response_model=LikeCount):
    """
    특정 게시글의 좋아요 개수 조회
    """
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return {"post_id": post_id, "like_count": like_count}


@board_like_router.delete("/post/{post_id}/", response_model=LikeResponse)
async def unlike_post(
        post_id : int,
        authorization : str,
        db : Session = Depends(get_db)
):
    # JWT
    user_info = get_user_info(authorization)
    user_id = user_info['id']

    existing_like = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == user_id).first()
    if not existing_like:
        raise HTTPException(status_code=400, detail="좋아요를 누른 적이 없습니다.")


    db.delete(existing_like)
    db.commit()

    # ✅ 업데이트된 좋아요 개수 반환
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    return LikeResponse(message="게시글 좋아요가 취소되었습니다.", like_count=like_count)