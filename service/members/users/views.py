from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, ChangePasswordSerializer, UserDetailSerializer, UpdateProfileSerializer
from rest_framework import generics
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .permissions import IsOwner

from .service import get_user_comments

import redis
import json

CACHE_EXPIRE_TIME_USER = 300  # ✅ 5분 캐싱
r = redis.Redis(host="localhost", port=6378, decode_responses=True)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserUpdateView(generics.RetrieveUpdateAPIView):
    """
    회원 정보 조회 및 수정 API
    """
    queryset = User.objects.all()
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]  # ✅ 인증된 사용자 & 본인만 수정 가능

    def get_object(self):
        return self.request.user  # ✅ 현재 로그인한 유저 객체 반환


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 접근 가능

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)

            # ✅ 모든 Refresh Token을 블랙리스트에 등록 (로그아웃 처리)
            RefreshToken.for_user(request.user).blacklist()

            return Response({"message": "비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    """
    ✅ 현재 로그인한 사용자의 정보를 Redis에서 캐싱하여 빠르게 조회
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # ✅ 현재 로그인한 사용자 반환

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        cache_key = f"user_profile:{user.id}"

        # ✅ 1️⃣ Redis 캐시 확인
        cached_user_data = r.get(cache_key)
        if cached_user_data:
            print(f"📌 Redis 캐시에서 사용자 {user.id} 정보 조회")
            user_data = json.loads(cached_user_data)
        else:
            # ✅ 2️⃣ 캐시에 없으면 DB에서 가져오기
            serializer = self.get_serializer(user)
            user_data = serializer.data

            # ✅ 3️⃣ Redis에 캐싱 (5분 TTL)
            r.setex(cache_key, CACHE_EXPIRE_TIME_USER, json.dumps(user_data))
            print(f"📌 Redis에 사용자 {user.id} 정보 캐싱 완료 (TTL: {CACHE_EXPIRE_TIME_USER}초)")

        # ✅ 4️⃣ 댓글 데이터 가져오기 (Redis + FastAPI)
        comments = get_user_comments(user.id)

        # ✅ 5️⃣ 최종 응답 반환
        return Response({
            "user": user_data,
            "comments": comments
        })
class UserDeleteView(APIView):
    """
    현재 로그인한 사용자가 회원 탈퇴하는 API
    """
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 가능

    def delete(self, request):
        user = request.user
        user.delete()  # ✅ 회원 계정을 완전히 삭제

        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)