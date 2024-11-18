from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import CustomUser

class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(help_text="The user's email address.")
    username = serializers.CharField(help_text="The user's username.")
    password = serializers.CharField(write_only=True, help_text="The user's password.")
    role = serializers.CharField(help_text="The role of the user (e.g., 'student', 'teacher', 'admin').")

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'role')

class CustomUserSerializer(UserSerializer):
    email = serializers.EmailField(help_text="The user's email address.")
    username = serializers.CharField(help_text="The user's username.")
    role = serializers.CharField(help_text="The role of the user (e.g., 'student', 'teacher', 'admin').")

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'username', 'role')