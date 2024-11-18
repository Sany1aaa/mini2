from students.models import Student
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

logger = logging.getLogger('grades')

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
            student = Student.objects.get(user=user)
            return Grade.objects.filter(student=student)
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
        """
        Returns a paginated list of grades.
        Accessible to authenticated Admin and Teacher users.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific grade by its ID.",
        responses={200: GradeSerializer()}
    )
    @method_decorator(cache_page(60 * 15, key_prefix='grade_detail'))
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific grade.
        Accessible to students, teachers, and admins.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new grade entry.",
        request_body=GradeSerializer,
        responses={201: GradeSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new grade for a student.
        Only accessible to authenticated teachers or admins.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an existing grade entry.",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()}
    )
    def update(self, request, *args, **kwargs):
        """
        Update an existing grade.
        Only accessible to authenticated teachers or admins.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an existing grade entry.",
        request_body=GradeSerializer,
        responses={200: GradeSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing grade.
        Only accessible to authenticated teachers or admins.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a grade entry by its ID.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a grade.
        Only accessible to authenticated teachers or admins.
        """
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        grade = serializer.instance
        logger.info(
            f"Преподаватель {self.request.user.email} выставил оценку {grade.grade} студенту {grade.student.user.email} по курсу {grade.course.name}")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        grade = serializer.instance
        logger.info(
            f"Преподаватель {self.request.user.email} обновил оценку студенту {grade.student.user.email} по курсу {grade.course.name} на {grade.grade}")

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            f"Преподаватель {self.request.user.email} удалил оценку студенту {instance.student.user.email} по курсу {instance.course.name}")