from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.urls import path
from .views import LoginView, LogoutView, get_csrf_token

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 (액세스/리프레시 토큰 발급)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 액세스 토큰 갱신
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # 토큰 검증
    path("csrf-token/", get_csrf_token, name="csrf-token"),
]