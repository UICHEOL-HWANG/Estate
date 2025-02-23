import redis
import httpx
import json


LIKE_URI = "http://localhost:8002"
r = redis.Redis(host="localhost", port=6378, decode_responses=True)

CACHE_EXPIRE_TIME_LIKES = 300  # ✅ 5분 캐싱 (TTL 설정)


async def get_likes_count(item_id: int, item_type: str):
    """
    ✅ 좋아요 개수를 Redis에서 조회, 없으면 API 호출 후 캐싱
    """
    if item_type not in ["post", "comment"]:
        raise ValueError("Invalid item_type. Must be 'post' or 'comment'.")

    cache_key = f"like_count:{item_type}:{item_id}"

    # ✅ 1️⃣ Redis 캐시 확인
    cached_likes = r.get(cache_key)
    if cached_likes is not None:
        return int(cached_likes)  # ✅ 캐시에 있으면 바로 반환

    # ✅ 2️⃣ 캐시에 없으면 HTTP 요청 수행
    endpoint = "board_like" if item_type == "post" else "comment_like"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LIKE_URI}/{endpoint}/{item_type}/{item_id}/count")
            response.raise_for_status()
            like_count = response.json().get("like_count", 0)

            # ✅ 3️⃣ Redis에 캐싱 (5분 TTL)
            r.setex(cache_key, CACHE_EXPIRE_TIME_LIKES, like_count)
            return like_count
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return 0  # ❗ 404일 경우 기본값 0 반환
            raise
        except httpx.RequestError:
            return 0  # ❗ 요청 실패 시 기본값 0 반환
