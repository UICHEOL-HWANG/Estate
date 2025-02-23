import redis
import json
import uuid
import time
from fastapi import HTTPException

r = redis.Redis(host="localhost", port=6378, decode_responses=True)

def get_user_info(authorization: str):
    if not authorization.startswith("Bearer "):
        print(f"🚨 잘못된 Authorization 형식: {authorization}")
        raise HTTPException(status_code=401, detail="잘못된 토큰 형식: Bearer 필요")

    token = authorization.split("Bearer ")[1]
    request_id = str(uuid.uuid4())

    request_data = {
        "request_id": request_id,
        "access_token": token
    }

    print(f"📌 Redis Stream 인증 요청 추가: {request_data}")

    # ✅ Redis Stream에 요청 추가
    r.xadd("auth_request_stream", request_data)
    print(f"📌 Redis Stream 추가 완료!")

    # ✅ Redis Pub/Sub 구독하여 응답 기다림 (타임아웃 5초 설정)
    pubsub = r.pubsub()
    pubsub.subscribe(f"auth_response_{request_id}")

    timeout = time.time() + 5  # 5초 동안 응답을 기다림
    for message in pubsub.listen():
        print(f"📌 Pub/Sub 메시지 수신: {message}")  # ✅ 추가 로그

        if time.time() > timeout:
            raise HTTPException(status_code=500, detail="Redis Pub/Sub 응답 시간 초과")

        # ✅ "subscribe" 타입이 아닌 실제 메시지만 처리
        if message["type"] != "message":
            continue

        response = json.loads(message["data"])
        print(f"📌 Redis Pub/Sub 최종 인증 응답 수신: {response}")

        if "error" in response:
            raise HTTPException(status_code=401, detail=response["error"])

        return response["user"]  # ✅ user 정보만 반환

    raise HTTPException(status_code=500, detail="Redis 인증 시스템 오류")
