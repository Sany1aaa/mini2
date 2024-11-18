from django.contrib import admin
from .models import Grade

class GradeAdmin(admin.ModelAdmin):
    list_display = ('student_email', 'course_name', 'grade', 'date', 'teacher_email')
    search_fields = ('student__user__email', 'course__name', 'grade', 'teacher__email')

    def student_email(self, obj):
        return obj.student.user.email
    student_email.short_description = 'Student Email'

    def course_name(self, obj):
        return obj.course.name
    course_name.short_description = 'Course Name'

    def teacher_email(self, obj):
        return obj.teacher.email
    teacher_email.short_description = 'Teacher Email'

admin.site.register(Grade, GradeAdmin)