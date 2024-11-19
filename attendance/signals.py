import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Attendance

logger = logging.getLogger('attendance')

@receiver(post_save, sender=Attendance)
def log_attendance_marking(sender, instance, created, **kwargs):
    student_email = instance.student.user.email
    course_name = instance.course.name
    date = instance.date
    status = instance.status

    if created:
        logger.info(f"Attendance marked: Student {student_email}, Course {course_name}, Date {date}, Status {status}.")
    else:
        logger.info(f"Attendance updated: Student {student_email}, Course {course_name}, Date {date}, Status {status}.")
