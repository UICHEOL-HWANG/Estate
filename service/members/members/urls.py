from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ✅ Swagger 문서 설정
schema_view = get_schema_view(
    openapi.Info(
        title="회원 및 인증 API 문서",
        default_version="v1",
        description="회원가입, 로그인, JWT 인증 API 문서",
        terms_of_service="https://www.yoursite.com/policies",
        contact=openapi.Contact(email="cheorish.hw@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # ✅ 회원 API
    path('api/account/', include('account.urls')),  # ✅ 인증 API

    # ✅ Swagger API 문서
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
