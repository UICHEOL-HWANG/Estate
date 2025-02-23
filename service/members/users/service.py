import redis
import json
import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import UserDetailSerializer


FASTAPI_URL = "http://localhost:8008"  # ✅ FastAPI 서버 주소
r = redis.Redis(host="localhost", port=6378, decode_responses=True)
CACHE_EXPIRE_TIME_USER = 300  # ✅ 5분 캐싱

def get_user_comments(user_id):
    """
    ✅ FastAPI에서 특정 사용자의 댓글을 Redis에서 가져오고, 없으면 API 호출 후 캐싱
    """
    cache_key = f"user_comments:{user_id}"

    # ✅ 1️⃣ Redis 캐시 확인
    cached_comments = r.get(cache_key)
    if cached_comments:
        print(f"📌 Redis 캐시에서 사용자 {user_id}의 댓글 조회")
        return json.loads(cached_comments)

    # ✅ 2️⃣ FastAPI에서 댓글 가져오기
    try:
        response = requests.get(f"{FASTAPI_URL}/comment/user/{user_id}/")
        response.raise_for_status()
        comments = response.json()

        # ✅ 3️⃣ Redis에 캐싱 (5분 TTL)
        r.setex(cache_key, CACHE_EXPIRE_TIME_USER, json.dumps(comments))
        print(f"📌 Redis에 사용자 {user_id}의 댓글 캐싱 완료 (TTL: {CACHE_EXPIRE_TIME_USER}초)")

        return comments
    except requests.RequestException as e:
        print(f"FastAPI 요청 실패: {e}")
        return []

