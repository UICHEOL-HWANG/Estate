from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from model.database import get_db
from model.models import Post

from dto.post import PostCreate, PostUpdate, PostResponse
from util.auth import get_user_info

board_router = APIRouter(
    prefix="/board",
    tags=["board"],
    responses={404: {"description": "Not found"}},
)


@board_router.post("/")
def create_post(post: PostCreate, authorization: str, db: Session = Depends(get_db) ):
    print(f"📌 Received Authorization Header: {authorization}")  # ✅ 디버깅용 로그 추가
    # ✅ JWT 토큰을 이용하여 Django에서 회원 정보 가져오기
    user_info = get_user_info(authorization)

    print(user_info)
    author_id = user_info["id"]  # ✅ Django에서 가져온 회원 ID

    # ✅ 새로운 게시글 생성
    new_post = Post(title=post.title, content=post.content, author_id=author_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "message": "게시글이 성공적으로 등록되었습니다.",
        "post": {
            "id": new_post.id,
            "title": new_post.title,
            "content": new_post.content,
            "author": user_info["username"],  # ✅ Django에서 가져온 username
            "created_at": new_post.created_at
        }
    }

@board_router.get("/{post_id}")
def read_post(post_id: int, authorization: str, db: Session = Depends(get_db), ):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # ✅ Django 회원 서비스에서 현재 로그인한 사용자 정보 조회
    user_info = get_user_info(authorization)

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": user_info["username"],  # ✅ Django에서 가져온 username
        "created_at": post.created_at
    }

# ✅ 게시글 수정 (Authorization 필수)
@board_router.put("/{post_id}/", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    authorization: str,
    db: Session = Depends(get_db),  # ✅ 필수 헤더 처리
):
    user_info = get_user_info(authorization)
    author_id = user_info["id"]

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.author_id != author_id:
        raise HTTPException(status_code=403, detail="본인의 게시글만 수정할 수 있습니다.")

    post.title = post_data.title
    post.content = post_data.content
    db.commit()
    db.refresh(post)

    return post

# ✅ 게시글 삭제 (Authorization 필수)
@board_router.delete("/{post_id}/")
def delete_post(
    post_id: int,
    authorization: str,
    db: Session = Depends(get_db)
):
    user_info = get_user_info(authorization)
    author_id = user_info["id"]

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.author_id != author_id:
        raise HTTPException(status_code=403, detail="본인의 게시글만 삭제할 수 있습니다.")

    db.delete(post)
    db.commit()

    return {"message": "게시글이 삭제되었습니다."}

