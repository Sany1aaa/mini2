from students.models import Student
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attendance
from .serializers import AttendanceSerializer
from users.permissions import IsTeacher, IsAdmin, IsStudent
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger('attendance')

class AttendancePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AttendancePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course__name', 'date', 'status']
    search_fields = ['student__user__email', 'course__name']
    ordering_fields = ['date', 'course__name', 'status']

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
            return Attendance.objects.all()
        user = self.request.user
        if user.role == 'student':
            student = Student.objects.get(user=user)
            return Attendance.objects.filter(student=student)
        elif user.role == 'teacher':
            return Attendance.objects.filter(course__instructor=user)
        return Attendance.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        attendance = serializer.instance
        logger.info(
            f"Teacher {self.request.user.email} marked attendance for student {attendance.student.user.email} in course {attendance.course.name} on {attendance.date} with status {attendance.status}"
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        attendance = serializer.instance
        logger.info(
            f"Teacher {self.request.user.email} updated attendance for student {attendance.student.user.email} in course {attendance.course.name} on {attendance.date} with status {attendance.status}"
        )

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(
            f"Teacher {self.request.user.email} deleted attendance record for student {instance.student.user.email} in course {instance.course.name} on {instance.date}"
        )

    @swagger_auto_schema(
        operation_description="Retrieve a list of attendance records with optional filters.",
        responses={200: AttendanceSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Results per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('course__name', openapi.IN_QUERY, description="Filter by course name", type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date", type=openapi.FORMAT_DATE),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific attendance record by ID.",
        responses={200: AttendanceSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new attendance record.",
        request_body=AttendanceSerializer,
        responses={201: AttendanceSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update an attendance record.",
        request_body=AttendanceSerializer,
        responses={200: AttendanceSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update an attendance record.",
        request_body=AttendanceSerializer,
        responses={200: AttendanceSerializer()}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an attendance record.",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
