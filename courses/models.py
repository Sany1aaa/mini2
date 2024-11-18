from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from users.models import CustomUser
from students.models import Student

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='courses')

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


@receiver([post_save, post_delete], sender=Course)
def clear_course_cache(sender, instance, **kwargs):
    cache.delete('course_list')
    cache_key = f'course_detail_{instance.pk}'
    cache.delete(cache_key)

@receiver([post_save, post_delete], sender=Enrollment)
def clear_enrollment_cache(sender, instance, **kwargs):
    cache_key = f'enrollments_for_student_{instance.student.pk}'
    cache.delete(cache_key)
    cache_key = f'enrollments_for_course_{instance.course.pk}'
    cache.delete(cache_key)