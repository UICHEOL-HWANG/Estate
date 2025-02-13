from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, ChangePasswordSerializer, UserDetailSerializer
from rest_framework import generics
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .permissions import IsOwner


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
    serializer_class = UserSerializer
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
    현재 로그인한 사용자의 정보를 조회하는 API
    """
    serializer_class = UserDetailSerializer  # ✅ UserDetailSerializer 사용
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 접근 가능

    def get_object(self):
        return self.request.user  # ✅ 현재 로그인한 사용자 반환


class UserDeleteView(APIView):
    """
    현재 로그인한 사용자가 회원 탈퇴하는 API
    """
    permission_classes = [IsAuthenticated]  # ✅ 인증된 사용자만 가능

    def delete(self, request):
        user = request.user
        user.delete()  # ✅ 회원 계정을 완전히 삭제

        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)