from rest_framework import serializers
from .models import Grade
from students.models import Student
from courses.models import Course
from users.models import CustomUser

class GradeSerializer(serializers.ModelSerializer):
    """
    Serializer for grade records, containing information on the grade value, date,
    course, and student.
    """
    student = serializers.SlugRelatedField(
        slug_field='user__email',
        queryset=Student.objects.all()
    )
    course = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Course.objects.all()
    )
    teacher = serializers.SlugRelatedField(
        slug_field='email',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Grade
        fields = '__all__'

    def create(self, validated_data):
        return Grade.objects.create(**validated_data)