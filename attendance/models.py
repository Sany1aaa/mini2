from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from students.models import Student
from courses.models import Course

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student} was {self.status} on {self.date} in {self.course}"


@receiver([post_save, post_delete], sender=Attendance)
def clear_attendance_cache(sender, instance, **kwargs):
    cache.delete('attendance_list')
    cache_key = f'attendance_detail_{instance.pk}'
    cache.delete(cache_key)