import redis
import json
import threading
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

r = redis.Redis(host="localhost", port=6378, decode_responses=True)

class AuthConsumer:
    def __init__(self):
        self.group = "auth_group"
        self.consumer = "auth_service"

        # ✅ 기존 그룹이 존재하면 새로 생성하지 않고 그대로 사용
        try:
            r.xgroup_create("auth_request_stream", self.group, id="0", mkstream=True)
            print("📌 Redis Stream 그룹 생성 완료")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print("📌 Redis Stream 그룹 이미 존재함. 기존 그룹 사용")
            else:
                raise

    def start(self):
        print("🚀 Django Redis Consumer 실행됨!")
        self.process_auth_requests()

    def process_auth_requests(self):
        print("📌 Django Redis Stream 대기 중...")

        while True:
            try:
                # ✅ 메시지를 가져오는 동안 타임아웃을 줄여서 처리 속도 개선
                messages = r.xreadgroup(self.group, self.consumer, {"auth_request_stream": ">"}, count=1, block=5000)
                if messages:
                    print(f"📌 Redis Stream 메시지 수신: {messages}")  # ✅ 수신 로그 확인

                for stream_name, msgs in messages:
                    for msg_id, msg_data in msgs:
                        request_id = msg_data.get("request_id")
                        access_token = msg_data.get("access_token")

                        print(f"📌 Django Redis Consumer 인증 요청 수신: {msg_data}")

                        try:
                            User = get_user_model()
                            token = AccessToken(access_token)
                            user = User.objects.get(id=token["user_id"])

                            response_data = {
                                "request_id": request_id,
                                "user": {
                                    "id": user.id,
                                    "username": user.username
                                }
                            }
                            print(f"✅ Django에서 인증 성공: {response_data}")

                        except Exception as e:
                            response_data = {"request_id": request_id, "error": "인증 실패"}
                            print(f"🚨 Django에서 인증 실패: {response_data}, 예외: {e}")

                        # ✅ Redis Pub/Sub을 통해 응답 전송
                        print(f"📌 Redis Pub/Sub 응답 전송 중: {response_data}")
                        r.publish(f"auth_response_{request_id}", json.dumps(response_data))
                        print(f"📌 Redis Pub/Sub 전송 완료!")

                        # ✅ 메시지 처리 완료 (ACK)
                        r.xack("auth_request_stream", self.group, msg_id)

            except Exception as e:
                print(f"🚨 Redis Consumer Error: {e}")
