from django.apps import AppConfig
import threading
import sys

class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account"

    def ready(self):
        """
        Django 서버 실행 시 Redis Stream Consumer를 실행 (runserver일 때만)
        """
        print("📌 Django `ready()` 함수 실행됨")  # ✅ 이 로그가 찍히는지 확인
        if "runserver" not in sys.argv:
            return  # ✅ `runserver` 실행이 아닐 경우 Redis Consumer 실행 방지

        threading.Thread(target=self.start_redis_consumer, daemon=True).start()

    def start_redis_consumer(self):
        """
        ✅ Django 앱이 완전히 로드된 후 Redis Consumer 실행
        """
        from django.conf import settings
        if not settings.configured:
            print("🚨 Django 설정이 로드되지 않음")
            return

        from django.db import connection
        if not connection.settings_dict:
            print("🚨 Django 데이터베이스 연결이 설정되지 않음")
            return

        from .redis_consumer import AuthConsumer
        print("🚀 Django Redis Consumer 실행 준비 완료!")  # ✅ 로그 추가
        auth_consumer = AuthConsumer()
        auth_consumer.start()
        print("✅ Django Redis Consumer 실행됨")
