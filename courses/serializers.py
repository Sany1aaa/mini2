from rest_framework import serializers
from .models import Course, Enrollment
from users.serializers import CustomUserSerializer
from students.serializers import StudentSerializer
from users.models import CustomUser
from students.models import Student

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='teacher'))

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()

    class Meta:
        model = Enrollment
        fields = '__all__'

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        course_data = validated_data.pop('course')
        student = Student.objects.get(user__email=student_data['user']['email'])
        course = Course.objects.get(name=course_data['name'])
        enrollment = Enrollment.objects.create(student=student, course=course, **validated_data)
        return enrollment