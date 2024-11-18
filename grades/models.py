from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from students.models import Student
from courses.models import Course
from users.models import CustomUser

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    grade = models.CharField(max_length=2)
    date = models.DateField(auto_now_add=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='given_grades')

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} got {self.grade} in {self.course}"



@receiver([post_save, post_delete], sender=Grade)
def clear_grade_cache(sender, instance, **kwargs):
    cache.delete('grade_list')
    cache_key = f'grade_detail_{instance.pk}'
    cache.delete(cache_key)


@receiver(post_save, sender=Grade)
def notify_grade_update(sender, instance, created, **kwargs):
    from notifications.tasks import send_grade_update_notification
    student_email = instance.student.user.email
    course_name = instance.course.name
    grade_value = instance.grade

    send_grade_update_notification.delay(student_email, course_name, grade_value)