from django.urls import path
from .views import (RegisterView,
                    UserUpdateView,
                    ChangePasswordView,
                    UserDetailView,
                    UserDeleteView
                    )
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 회원가입 API
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),  # ✅
    path('profile/update/', UserUpdateView.as_view(), name='user_update'),
    path('profile/', UserDetailView.as_view(), name='user_detail'),
    path('resign/', UserDeleteView.as_view(), name='user_delete'),
]
