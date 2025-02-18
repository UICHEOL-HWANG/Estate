from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    username = models.CharField(
        max_length=15, unique=True,
        error_messages={'unique': '이미 사용중인 닉네임'}
    )
    profile_pic = models.ImageField(
        upload_to="profile_pics/",
        default="default_profile_pic.jpg",  # ✅ 기본 프로필 이미지 설정
        blank=True
    )
    intro = models.CharField(max_length=60, blank=True)

    # ✅ Django 기본 `auth.Group`, `auth.Permission` 충돌 방지
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True
    )


    def __str__(self):
        return self.username
