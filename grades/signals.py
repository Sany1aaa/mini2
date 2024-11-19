import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade

logger = logging.getLogger('grades')

@receiver(post_save, sender=Grade)
def log_grade_update(sender, instance, created, **kwargs):
    """
    Signal handler to log grade updates or creations.
    """
    student_email = instance.student.user.email
    course_name = instance.course.name
    grade_value = instance.grade
    teacher_email = instance.teacher.email

    if created:
        logger.info(
            f"New grade assigned: Student {student_email}, Course {course_name}, Grade {grade_value}, Teacher {teacher_email}"
        )
    else:
        logger.info(
            f"Grade updated: Student {student_email}, Course {course_name}, Updated Grade {grade_value}, Teacher {teacher_email}"
        )
