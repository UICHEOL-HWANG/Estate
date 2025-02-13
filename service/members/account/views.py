from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import UserSerializer  # ✅ `users` 앱의 `UserSerializer` 재사용

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "아이디와 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)  # ✅ 사용자 존재 여부 확인
        except User.DoesNotExist:
            return Response({"error": "존재하지 않는 계정입니다."}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=username, password=password)  # ✅ 비밀번호 검증

        if user is None:
            return Response({"error": "비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ 로그인 성공 - JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data
        }, status=status.HTTP_200_OK)

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