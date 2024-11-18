from rest_framework import serializers
from .models import Attendance
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer
from students.models import Student
from courses.models import Course

class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for attendance records, containing detailed information on the attendance status,
    course, student, and date.
    """
    date = serializers.DateField(help_text="The date of attendance.")
    status = serializers.CharField(help_text="Attendance status (e.g., 'Present', 'Absent').")
    course = serializers.PrimaryKeyRelatedField(help_text="Course ID associated with this attendance record.",
                                                read_only=True)
    student = serializers.PrimaryKeyRelatedField(help_text="Student ID associated with this attendance record.",
                                                 read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        course_data = validated_data.pop('course')
        student = Student.objects.get(user__email=student_data['user']['email'])
        course = Course.objects.get(name=course_data['name'])
        attendance = Attendance.objects.create(student=student, course=course, **validated_data)
        return attendance