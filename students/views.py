import logging

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Student
from .serializers import StudentSerializer
from users.permissions import IsStudent, IsAdmin
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger('students')


class StudentViewSet(viewsets.ModelViewSet):
    """
    retrieve:
    Return the given student.

    list:
    Return a list of all students.

    create:
    Create a new student.

    update:
    Update an existing student.

    partial_update:
    Partially update an existing student.

    destroy:
    Delete a student.
    """


    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['registration_date']
    search_fields = ['user__email', 'user__username']
    ordering_fields = ['registration_date', 'user__email']

    def get_permissions(self):
        if self.action in ['retrieve', 'update']:
            permission_classes = [IsAuthenticated, IsStudent | IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.all()

        user = self.request.user
        if user.role == 'student':
            return Student.objects.filter(user=user)
        return Student.objects.all()

    @method_decorator(cache_page(60 * 15, key_prefix='student_list'))
    @swagger_auto_schema(
        operation_description="Retrieve a list of students",
        responses={200: StudentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15, key_prefix='student_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        student = serializer.instance
        logger.info(f"Студент {student.user.email} обновил свой профиль")