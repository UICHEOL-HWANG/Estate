from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(
        max_length=15, unique=True, null=True,
        error_messages={'unique': '이미 사용중인 닉네임'}
    )
    profile_pic = models.ImageField(
        default="default_profile_pic.jpg", upload_to="profile_pics", blank=True
    )
    intro = models.CharField(max_length=60, blank=True)

    # related_name 추가하여 충돌 방지
    groups = models.ManyToManyField(
        "auth.Group",  # ✅ Django 기본 `auth.Group`을 사용
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",  # ✅ Django 기본 `auth.Permission`을 사용
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.username
