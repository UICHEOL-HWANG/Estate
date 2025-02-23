from fastapi import APIRouter, Depends, HTTPException, Query, Header

from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy import func
import redis
import json
import asyncio

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

# Caching Ready
r = redis.Redis(host="localhost", port=6378, decode_responses=True)

CACHE_EXPIRE_TIME_POSTS = 60  # ✅ 캐시 TTL (1분)
CACHE_EXPIRE_TIME_LIKES = 300

@board_router.post("/")
def create_post(post: PostCreate, authorization: str = Header(...), db: Session = Depends(get_db) ):
    print(f"📌 Received Authorization Header: {authorization}")  # ✅ 디버깅용 로그 추가
    print(f"📌 Received Post Data: {post.dict()}")
    # ✅ JWT 토큰을 이용하여 Django에서 회원 정보 가져오기
    user_info = get_user_info(authorization)


    author_id = user_info["id"]  # ✅ Django에서 가져온 회원 ID
    author_name = user_info["username"]

    # ✅ 새로운 게시글 생성
    new_post = Post(title=post.title, content=post.content, author_id=author_id, author_name=author_name)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # ✅ Redis Stream에 게시글 생성 이벤트 추가
    event_data = {
        "event_type": "create",
        "post_id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "author": new_post.author_name,
        "created_at": str(new_post.created_at)
    }
    r.xadd("post_stream", event_data)

    return {"message": "게시글이 등록되었습니다.", "post": event_data}

@board_router.get("/{post_id}")
async def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    ✅ 특정 게시글을 조회하고, 좋아요 개수를 캐싱하여 반환
    """
    cache_key = f"post:{post_id}"

    # ✅ 1️⃣ Redis 캐시 확인
    cached_data = r.get(cache_key)
    if cached_data:
        print(f"📌 Redis 캐시에서 게시글 {post_id} 조회")
        return json.loads(cached_data)

    # ✅ 2️⃣ DB 조회
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # ✅ 3️⃣ 좋아요 개수 캐싱 확인
    like_cache_key = f"like_count:post:{post_id}"
    cached_likes = r.get(like_cache_key)
    if cached_likes is not None:
        like_count = int(cached_likes)
    else:
        like_count = await get_likes_count(post_id, "post")
        r.setex(like_cache_key, CACHE_EXPIRE_TIME_LIKES, like_count)

    # ✅ 4️⃣ 최종 데이터 구성
    post_data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author_name,
        "created_at": post.created_at.isoformat(),  # ✅ JSON 직렬화 가능하도록 변환
        "like_count": like_count
    }

    # ✅ 5️⃣ Redis 캐싱 (5분 TTL 설정)
    r.setex(cache_key, CACHE_EXPIRE_TIME_POSTS, json.dumps(post_data))
    print(f"📌 Redis에 게시글 {post_id} 캐싱 완료 (TTL: {CACHE_EXPIRE_TIME_POSTS}초)")

    return post_data


@board_router.put("/{post_id}/")
def update_post(post_id: int, post_data: PostUpdate, authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    ✅ 게시글 수정 API (Redis Stream에 추가)
    """
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

    # ✅ Redis Stream에 게시글 수정 이벤트 추가
    event_data = {
        "event_type": "update",
        "post_id": post.id,
        "title": post.title,
        "content": post.content,
        "updated_at": str(post.updated_at)
    }
    r.xadd("post_stream", event_data)

    return {"message": "게시글이 수정되었습니다.", "post": event_data}

# ✅ 게시글 삭제 (Authorization 필수)

@board_router.delete("/{post_id}/")
def delete_post(post_id: int, authorization: str = Header(...), db: Session = Depends(get_db)):
    """
    ✅ 게시글 삭제 API (Redis Stream에 추가)
    """
    user_info = get_user_info(authorization)
    author_id = user_info["id"]

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.author_id != author_id:
        raise HTTPException(status_code=403, detail="본인의 게시글만 삭제할 수 있습니다.")

    db.delete(post)
    db.commit()

    # ✅ Redis Stream에 게시글 삭제 이벤트 추가
    event_data = {
        "event_type": "delete",
        "post_id": post_id
    }
    r.xadd("post_stream", event_data)

    return {"message": "게시글이 삭제되었습니다."}

@board_router.get("/all/", response_model=list[dict])
async def get_all_posts(db: Session = Depends(get_db)):
    """
    ✅ 모든 게시글 조회 API (좋아요 & 댓글 개수 포함)
    """

    cache_key = "all_posts"

    # ✅ 1️⃣ Redis에서 캐시된 데이터 확인
    cached_data = r.get(cache_key)
    if cached_data:
        print("📌 Redis 캐시에서 게시글 목록 조회")
        return json.loads(cached_data)  # ✅ 캐싱된 데이터 반환

    # ✅ 2️⃣ DB에서 게시글 목록 조회
    posts = db.query(Post).all()

    if not posts:
        return []  # ✅ 게시글이 없으면 빈 리스트 반환

    # ✅ 3️⃣ 댓글 개수를 한 번에 조회
    post_ids = [post.id for post in posts]
    comment_counts = {
        post_id: count for post_id, count in
        db.query(Comment.post_id, func.count(Comment.id))
          .filter(Comment.post_id.in_(post_ids))
          .group_by(Comment.post_id)
          .all()
    }

    # ✅ 4️⃣ 좋아요 개수를 병렬로 가져오기
    like_tasks = [get_likes_count(post.id, "post") for post in posts]
    like_counts = await asyncio.gather(*like_tasks)  # 🚀 병렬 실행

    # ✅ 5️⃣ 최종 데이터 구성 (`created_at`을 문자열로 변환)
    result = []
    for idx, post in enumerate(posts):
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "author": post.author_name,
            "created_at": post.created_at.isoformat(),  # ✅ JSON 직렬화를 위해 문자열 변환
            "like_count": like_counts[idx],  # ✅ 비동기 병렬 처리된 좋아요 개수 사용
            "comment_count": comment_counts.get(post.id, 0)  # ✅ 미리 가져온 댓글 개수 사용
        })

    # ✅ 6️⃣ Redis에 캐싱 (1분 TTL 설정)
    r.setex(cache_key, CACHE_EXPIRE_TIME_POSTS, json.dumps(result))
    print(f"📌 Redis에 게시글 목록 캐싱 완료 (TTL: {CACHE_EXPIRE_TIME_POSTS}초)")

    return result

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