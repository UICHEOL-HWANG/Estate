from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db
from model.models import Comment, Post
from dto.comment import CommentCreate, CommentResponse
from util.auth import get_user_info
from typing import List

comment_router = APIRouter(
    prefix="/comment",
    tags=["comment"],
    responses={404: {"description": "Not found"}},
)

# ✅ 댓글 작성
@comment_router.post("/{post_id}/")
def create_comment(
    post_id: int,
    authorization: str,
    comment: CommentCreate,
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 제공되지 않았습니다.")

    user_info = get_user_info(authorization)
    author_id = user_info["id"]  # ✅ Django에서 가져온 회원 ID

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    new_comment = Comment(post_id=post_id, author_id=author_id, content=comment.content)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {"message": "댓글이 성공적으로 등록되었습니다.", "comment": CommentResponse.from_orm(new_comment)}

# ✅ 특정 게시글의 댓글 목록 조회
@comment_router.get("/{post_id}/", response_model=List[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
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
