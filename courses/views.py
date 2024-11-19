from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from users.permissions import IsTeacher, IsAdmin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

logger = logging.getLogger('courses')


class CoursePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instructor.email']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'instructor.email']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial.update', 'destroy']:
            permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @method_decorator(cache_page(60 * 15, key_prefix='course.list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15, key_prefix='course.detail'))
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        CourseView.objects.create(
            course=instance,
            user=request.user if request.user.is_authenticated else None
        )
        return super().retrieve(request, *args, **kwargs)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial.update', 'delete']:
            permission_classes = [IsAuthenticated, IsTeacher | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        logger.info(f'Student {serializer.instance.student} enrolled in course {serializer.instance.course}')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        logger.info(f'Student {instance.student} unsubscribed from course {instance.course}')

    @method_decorator(cache_page(60 * 30, key_prefix='enrollmen.list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
