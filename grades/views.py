from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Grade
from .serializers import GradeSerializer
from users.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

class GradePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = GradePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course__name', 'grade', 'date']
    search_fields = ['student__user__email', 'course__name', 'grade']
    ordering_fields = ['date', 'grade', 'course__name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdmin | IsTeacher]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsStudent | IsTeacher | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Grade.objects.all()

        user = self.request.user
        if user.role == 'student':
            student_profile = Student.objects.get(user=user)
            return Grade.objects.filter(student=student_profile)
        elif user.role == 'teacher':
            return Grade.objects.filter(teacher=user)
        return Grade.objects.all()

    @swagger_auto_schema(
        operation_description="List all grades with filtering, searching, and pagination.",
        responses={200: GradeSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('course__name', openapi.IN_QUERY, description="Filter by course name",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('grade', openapi.IN_QUERY, description="Filter by grade", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date", type=openapi.FORMAT_DATE),
        ]
    )
    @method_decorator(cache_page(60 * 15, key_prefix='grade_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific grade by its ID.",
        responses={200: GradeSerializer()}
    )
    @method_decorator(cache_page(60 * 15, key_prefix='grade_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new grade entry.",
        request_body=GradeSerializer,
        responses={201: GradeSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing grade entry.",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an existing grade entry.",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a grade entry by its ID.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        grade_entry = serializer.instance
        logger.info(
            f"Teacher {self.request.user.email} assigned grade {grade_entry.grade} to student {grade_entry.student.user.email} for course {grade_entry.course.name}")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        grade_entry = serializer.instance
        logger.info(
            f"Teacher {self.request.user.email} updated grade for student {grade_entry.student.user.email} in course {grade_entry.course.name} to {grade_entry.grade}")

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            f"Teacher {self.request.user.email} deleted grade for student {instance.student.user.email} in course {instance.course.name}")
