import requests
from fastapi import HTTPException

DJANGO_API_URL = "http://localhost:8000"

def get_user_info(authorization: str ):
    """
    Django의 /api/profile/ 엔드포인트를 호출하여 사용자 정보를 가져옴
    """
    try:
        headers = {"Authorization": f"Bearer {authorization}"}
        response = requests.get(f"{DJANGO_API_URL}/api/users/profile/", headers=headers)
        print(headers)
        print(response)
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail="회원 정보를 가져올 수 없습니다.")
    except Exception as e:
        # 예외 상세 내용 출력
        print("Exception occurred in get_user_info:", e)