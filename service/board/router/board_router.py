from fastapi import APIRouter, Depends, HTTPException, Query, Header

from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy import func

from model.database import get_db
from model.models import Post, Comment

from dto.post import PostCreate, PostUpdate, PostResponse

from util.auth import get_user_info
from util.mapping import get_likes_count

from typing import Dict, List

board_router = APIRouter(
    prefix="/board",
    tags=["board"],
    responses={404: {"description": "Not found"}},
)

@board_router.post("/")
def create_post(post: PostCreate, authorization: str = Header(...), db: Session = Depends(get_db) ):
    print(f"📌 Received Authorization Header: {authorization}")  # ✅ 디버깅용 로그 추가
    print(f"📌 Received Post Data: {post.dict()}")
    # ✅ JWT 토큰을 이용하여 Django에서 회원 정보 가져오기
    user_info = get_user_info(authorization)


    print(user_info)
    author_id = user_info["id"]  # ✅ Django에서 가져온 회원 ID
    author_name = user_info["username"]

    # ✅ 새로운 게시글 생성
    new_post = Post(title=post.title, content=post.content, author_id=author_id, author_name=author_name)
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
async def read_post(post_id: int,  db: Session = Depends(get_db), authorization: str = Header(...),):
    """
    특정 게시글을 조회하고, 좋아요 개수도 함께 반환
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # ✅ Django 회원 서비스에서 현재 로그인한 사용자 정보 조회
    user_info = get_user_info(authorization)

    # ✅ `like_service`에서 좋아요 개수 가져오기 (비동기 호출)
    like_count = await get_likes_count(post_id, "post")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": user_info["username"],  # ✅ Django에서 가져온 username
        "created_at": post.created_at,
        "like_count": like_count  # ✅ 좋아요 개수 포함
    }
# ✅ 게시글 수정 (Authorization 필수)
@board_router.put("/{post_id}/", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    authorization: str = Header(...),
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
    authorization: str = Header(...),
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

@board_router.get("/all/", response_model=List[dict])
async def get_all_posts(
    db: Session = Depends(get_db)
):
    """
    ✅ 모든 게시글 조회 API (좋아요 & 댓글 개수 포함)
    """
    posts = db.query(Post).all()

    # ✅ posts가 None일 경우 빈 리스트 반환 (오류 방지)
    if not posts:
        return []

    # ✅ 모든 게시글 반환 (좋아요 & 댓글 개수 포함)
    result = []
    for post in posts:
        like_count = await get_likes_count(post.id, "post")  # ✅ 게시글 좋아요 개수 가져오기
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()  # ✅ 댓글 개수 조회

        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
            "like_count": like_count,  # ✅ 좋아요 개수 추가
            "comment_count": comment_count, # ✅ 댓글 개수 추가,
            "author" : post.author_name
        })

    return result  # ✅ 리스트 반환


@board_router.get("/sort/", response_model=List[dict])  # ✅ 경로 변경 (`/sort/`)
async def get_posts(
    sort_by: str = Query("latest", enum=["latest", "likes"], description="정렬 기준"),
    db: Session = Depends(get_db)
):
    """
    ✅ 게시글 목록 조회 (정렬 가능)
    - `latest` : 최신순 정렬 (기본값)
    - `likes` : 좋아요 많은 순 정렬
    """
    if sort_by == "latest":
        posts = db.query(Post).order_by(desc(Post.created_at)).all()
    elif sort_by == "likes":
        posts = db.query(Post).all()
        posts.sort(key=lambda p: get_likes_count(p.id, "post"), reverse=True)

    # ✅ 좋아요 개수 포함하여 반환
    result = []
    for post in posts:
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()  # ✅ 댓글 개수 조회
        like_count = await get_likes_count(post.id, "post")
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count" : comment_count
        })

    return result


@board_router.get("/search/", response_model=List[dict])
async def search_posts(
    q: str = Query(..., description="검색할 키워드"),
    db: Session = Depends(get_db)
):
    """
    ✅ 게시글 검색 기능 (제목/내용 기준)
    """
    posts = db.query(Post).filter(
        Post.title.contains(q) | Post.content.contains(q)
    ).all()

    result = []
    for post in posts:
        like_count = await get_likes_count(post.id, "post")
        comment_count = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count
        })

    return result