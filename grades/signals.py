import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade

logger = logging.getLogger('grades')

@receiver(post_save, sender=Grade)
def log_grade_update(sender, instance, created, **kwargs):
    student_email = instance.student.user.email
    course_name = instance.course.name
    grade_value = instance.grade
    teacher_email = instance.teacher.email
    if created:
        logger.info(f"Новая оценка: студент {student_email}, курс {course_name}, оценка {grade_value}, преподаватель {teacher_email}")
    else:
        logger.info(f"Обновление оценки: студент {student_email}, курс {course_name}, новая оценка {grade_value}, преподаватель {teacher_email}")