from django.contrib import admin
from .models import Course, Enrollment

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'instructor_email', 'description')
    search_fields = ('name', 'instructor__email')

    def instructor_email(self, obj):
        return obj.instructor.email
    instructor_email.short_description = 'Instructor Email'

admin.site.register(Course, CourseAdmin)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_email', 'course_name', 'enrolled_at')
    search_fields = ('student__user__email', 'course__name')

    def student_email(self, obj):
        return obj.student.user.email
    student_email.short_description = 'Student Email'

    def course_name(self, obj):
        return obj.course.name
    course_name.short_description = 'Course Name'

admin.site.register(Enrollment, EnrollmentAdmin)