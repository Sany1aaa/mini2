import logging
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserCreateSerializer
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger('users')

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Create a new user with the provided data.",
        request_body=CustomUserCreateSerializer,
        responses={201: CustomUserSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an existing user's data.",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific user by their ID.",
        responses={200: CustomUserSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing user's data.",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve the list of all users.",
        responses={200: CustomUserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a user by their ID.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
