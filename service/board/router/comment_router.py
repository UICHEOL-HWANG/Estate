from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db
from model.models import Comment, Post
from dto.comment import CommentCreate, CommentResponse
from util.auth import get_user_info
from typing import List


import redis
from util.mapping import get_likes_count

comment_router = APIRouter(
    prefix="/comment",
    tags=["comment"],
    responses={404: {"description": "Not found"}},
)

r = redis.Redis(host="localhost", port=6378, decode_responses=True)

# ✅ 댓글 작성
@comment_router.post("/{post_id}/")
def create_comment(
    post_id: int,
    comment_data: CommentCreate,  # ✅ Pydantic 모델 사용
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    ✅ 댓글 작성 API (Redis Stream에 추가)
    """
    user_info = get_user_info(authorization)
    author_id = user_info["id"]
    author_name = user_info["username"]

    new_comment = Comment(
        post_id=post_id,
        content=comment_data.content,  # ✅ Pydantic 모델에서 `content` 가져오기
        author_id=author_id,
        author_name=author_name
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # ✅ Redis Stream에 댓글 생성 이벤트 추가
    event_data = {
        "event_type": "create",
        "comment_id": new_comment.id,
        "post_id": post_id,
        "content": new_comment.content,
        "author": new_comment.author_name,
        "created_at": str(new_comment.created_at)
    }
    r.xadd("comment_stream", event_data)

    return {"message": "댓글이 등록되었습니다.", "comment": event_data}


@comment_router.get("/{post_id}/", response_model=list[CommentResponse])
async def get_comments(post_id: int, db: Session = Depends(get_db)):
    """
    특정 게시글의 댓글 목록 조회 (+ 각 댓글의 좋아요 개수 포함)
    """
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()

    # ✅ 각 댓글의 좋아요 개수 가져오기 (비동기 처리)
    for comment in comments:
        comment.like_count = await get_likes_count(comment.id, "comment")  # ✅ 댓글 좋아요 개수 추가

    return comments

# ✅ 댓글 수정
@comment_router.put("/{post_id}/{comment_id}/")
def update_comment(
    post_id: int,
    comment_id: int,
    authorization: str,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 제공되지 않았습니다.")

    user_info = get_user_info(authorization)
    author_id = user_info["id"]

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.author_id != author_id:
        raise HTTPException(status_code=403, detail="본인의 댓글만 수정할 수 있습니다.")

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return {"message": "댓글이 수정되었습니다.", "comment": CommentResponse.from_orm(comment)}

# ✅ 댓글 삭제
@comment_router.delete("/{post_id}/{comment_id}/")
def delete_comment(
    post_id: int,
    authorization: str,
    comment_id: int,
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 제공되지 않았습니다.")

    user_info = get_user_info(authorization)
    author_id = user_info["id"]

    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if comment.author_id != author_id:
        raise HTTPException(status_code=403, detail="본인의 댓글만 삭제할 수 있습니다.")

    db.delete(comment)
    db.commit()

    return {"message": "댓글이 삭제되었습니다."}

@comment_router.get("/user/{user_id}/", response_model=list[CommentResponse])
async def get_user_comments(user_id: int, db: Session = Depends(get_db)):
    """
    특정 회원이 작성한 댓글 목록 조회
    """
    comments = db.query(Comment).filter(Comment.author_id == user_id).all()

    # ✅ SQLAlchemy 모델을 Pydantic 모델로 변환
    comment_list = []
    for comment in comments:
        like_count = await get_likes_count(comment.id, "comment")  # ✅ 댓글 좋아요 개수 추가
        comment_list.append({
            "id": comment.id,
            "post_id": comment.post_id,
            "author_id": comment.author_id,  # ✅ 추가
            "author_name": comment.author_name,  # ✅ 추가
            "content": comment.content,
            "created_at": comment.created_at,
            "like_count": like_count
        })

    print(f"📌 FastAPI 응답 데이터: {comment_list}")  # ✅ 응답 로그 확인
    return comment_list  # ✅ 수정된 데이터 반환


