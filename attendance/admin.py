from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student_email', 'course_name', 'date', 'status')
    search_fields = ('student__user__email', 'course__name', 'status')

    def student_email(self, obj):
        return obj.student.user.email
    student_email.short_description = 'Student Email'

    def course_name(self, obj):
        return obj.course.name
    course_name.short_description = 'Course Name'

admin.site.register(Attendance, AttendanceAdmin)