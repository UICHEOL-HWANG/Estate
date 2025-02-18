import requests
from django.conf import settings

FASTAPI_URL = "http://localhost:8008"  # ✅ FastAPI 서버 주소 (환경 변수로 관리 가능)

def get_user_comments(user_id):
    """
    FastAPI에서 특정 사용자가 작성한 댓글을 가져오는 함수
    """
    try:
        response = requests.get(f"{FASTAPI_URL}/comment/user/{user_id}/")
        response.raise_for_status()  # ✅ HTTP 에러 발생 시 예외 처리
        return response.json()
    except requests.RequestException as e:
        print(f"FastAPI 요청 실패: {e}")
        return []
