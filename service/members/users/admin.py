from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'is_staff')  # ✅ 회원 목록에서 보이는 필드 설정
    search_fields = ('username', 'email')  # ✅ 검색 기능 추가
    list_filter = ('is_active', 'is_staff')  # ✅ 필터 추가