import httpx

LIKE_URI = "http://localhost:8002"

async def get_likes_count(item_id: int, item_type: str):
    """
    `like_service`의 좋아요 개수 조회 API를 호출하는 유틸 함수 (비동기)
    - `item_type`: "post" 또는 "comment"
    """
    if item_type not in ["post", "comment"]:
        raise ValueError("Invalid item_type. Must be 'post' or 'comment'.")

    # ✅ "post"는 `board_like`, "comment"는 `comment_like` 경로 사용
    endpoint = "board_like" if item_type == "post" else "comment_like"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{LIKE_URI}/{endpoint}/{item_type}/{item_id}/count")
            response.raise_for_status()
            return response.json().get("like_count", 0)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return 0  # ❗ 404일 경우 좋아요 개수는 0으로 반환
            raise
        except httpx.RequestError:
            return 0  # 요청 실패 시 기본값 0
