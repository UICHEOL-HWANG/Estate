from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db

from dto.like import LikeResponse, LikeCount
from util.auth import get_user_info
from model.models import PostLike, CommentLike

comment_like_router = APIRouter(
    prefix="/comment_like",
    tags=["comment_like"],
    responses={404: {"description": "Not found"}},
)

# ✅ 댓글 좋아요 토글 API
@comment_like_router.post("/comment/{comment_id}/", response_model=LikeResponse)
async def toggle_like_comment(
        comment_id: int,
        authorization: str = Header(...),
        db: Session = Depends(get_db)
):
    user_info = get_user_info(authorization)
    user_id = user_info["id"]

    existing_like = db.query(CommentLike).filter(
        CommentLike.comment_id == comment_id,
        CommentLike.user_id == user_id
    ).first()

    if existing_like:
        # ✅ 좋아요 취소
        db.delete(existing_like)
        db.commit()
        like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()
        return LikeResponse(message="댓글 좋아요가 취소되었습니다.", like_count=like_count)

    # ✅ 좋아요 추가
    new_like = CommentLike(comment_id=comment_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()

    return LikeResponse(message="댓글에 좋아요가 추가되었습니다.", like_count=like_count)


@comment_like_router.delete("/comment/{comment_id}/", response_model=LikeResponse)
async def like_comment(
        comment_id : int,
        authorization : str,
        db : Session = Depends(get_db)
):
    user_info = get_user_info(authorization)
    user_id = user_info['id']

    existing_like = db.query(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.user_id == user_id).first()
    if not existing_like:
        raise HTTPException(status_code=400, detail="좋아요를 누른 적이 없습니다.")

    db.delete(existing_like)
    db.commit()

    like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()
    return LikeResponse(message="댓글 좋아요가 취소되었습니다.", like_count=like_count)


# ✅ 댓글 좋아요 개수 조회
@comment_like_router.get("/comment/{comment_id}/count", response_model=LikeResponse)
def get_comment_like_count(comment_id: int, db: Session = Depends(get_db)):
    """
    특정 댓글의 좋아요 개수 조회
    """
    like_count = db.query(CommentLike).filter(CommentLike.comment_id == comment_id).count()
    return LikeResponse(message="댓글 좋아요 개수 조회 성공", like_count=like_count)

