from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
import json
import redis
from users.serializers import UserSerializer  # ✅ `users` 앱의 `UserSerializer` 재사용



r = redis.Redis(host="localhost", port=6378, decode_responses=True)
User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # ✅ 요청 데이터 검증 (JSON 형식 여부 확인)
            if not isinstance(request.data, dict):
                return Response({"error": "잘못된 요청 형식입니다. JSON 데이터를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

            username = request.data.get("username")
            password = request.data.get("password")

            print("🔍 요청된 데이터:", request.data)

            # ✅ 아이디 및 비밀번호가 제공되었는지 확인
            if not username or not password:
                return Response({"error": "아이디와 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ 사용자 존재 여부 확인
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "존재하지 않는 계정입니다."}, status=status.HTTP_404_NOT_FOUND)

            # ✅ 비밀번호 검증
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({"error": "비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

            # ✅ 로그인 성공 - JWT 토큰 발급
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            user_data = UserSerializer(user).data

            # ✅ Redis Stream에 바로 토큰 저장 (FastAPI에서 검증할 수 있도록)
            redis_data = {
                "user_id": user.id,
                "username": user.username,
                "access_token": access_token,
            }
            r.xadd("auth_token_stream", redis_data)

            print(f"📌 Redis Stream에 토큰 저장 완료: {redis_data}")

            return Response({
                "refresh": str(refresh),
                "access": access_token,
                "user": user_data
            }, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "잘못된 JSON 데이터 형식입니다."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"🚨 서버 오류 발생: {str(e)}")
            return Response({"error": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 로그아웃 가능

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")  # ✅ body에서 refresh 토큰 가져오기
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # ✅ Refresh Token을 블랙리스트에 등록하여 무효화

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)