from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_email', 'user_username', 'dob', 'registration_date')
    search_fields = ('name', 'user__email', 'user__username')
    list_filter = ('registration_date',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

admin.site.register(Student, StudentAdmin)