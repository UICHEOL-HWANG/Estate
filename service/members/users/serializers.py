from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'profile_pic', 'intro']
        extra_kwargs = {'password': {'write_only': True}}  # 비밀번호는 write-only

    def create(self, validated_data):
        password = validated_data.pop('password')  # 비밀번호 추출
        user = User(**validated_data)
        user.set_password(password)  # 비밀번호 해싱하여 저장
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_current_password(self, value):
        """
        현재 비밀번호가 올바른지 확인
        """
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value

    def update(self, instance, validated_data):
        """
        비밀번호 변경 후 저장
        """
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    """
    회원 정보 조회 전용 Serializer
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic', 'intro']  # ✅ 비밀번호 제외

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "intro"]

    def validate_username(self, value):
        if len(value) > 15:
            raise serializers.ValidationError("닉네임은 15자 이하로 작성해야 합니다.")
        return value

    def validate_intro(self, value):
        if len(value) > 60:
            raise serializers.ValidationError("자기소개는 60자 이하로 작성해야 합니다.")
        return value