import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment

logger = logging.getLogger('courses')

@receiver(post_save, sender=Enrollment)
def log_course_enrollment(sender, instance, created, **kwargs):
    if created:
        student_email = instance.student.user.email
        course_name = instance.course.name
        logger.info(f"Студент {student_email} зачислен на курс {course_name}")