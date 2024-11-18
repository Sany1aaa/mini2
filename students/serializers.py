from rest_framework import serializers
from .models import Student
from users.serializers import CustomUserCreateSerializer
from users.models import CustomUser


class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserCreateSerializer()
    enrollments = serializers.SerializerMethodField()
    grades = serializers.SerializerMethodField()
    attendance_records = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'dob', 'registration_date', 'enrollments', 'grades', 'attendance_records']

    def get_enrollments(self, obj):
        enrollments = obj.enrollments.all()
        return [
            {
                'id': enrollment.id,
                'course_id': enrollment.course.id,
                'course_name': enrollment.course.name,
                'enrolled_at': enrollment.enrolled_at
            }
            for enrollment in enrollments
        ]

    def get_grades(self, obj):
        grades = obj.grades.all()
        return [
            {
                'id': grade.id,
                'course_id': grade.course.id,
                'course_name': grade.course.name,
                'grade': grade.grade,
                'date': grade.date
            }
            for grade in grades
        ]

    def get_attendance_records(self, obj):
        attendance_records = obj.attendance_records.all()
        return [
            {
                'id': attendance.id,
                'course_id': attendance.course.id,
                'course_name': attendance.course.name,
                'date': attendance.date,
                'status': attendance.status
            }
            for attendance in attendance_records
        ]

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance