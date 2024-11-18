from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from users.models import CustomUser
from students.models import Student
from grades.models import Grade
from attendance.models import Attendance


@shared_task
def send_daily_attendance_reminder():
    students = CustomUser.objects.filter(role='student')
    for student in students:
        send_mail(
            'Attendance Reminder',
            'Please mark your attendance for today.',
            'system@kbtu.kz',
            [student.email],
            fail_silently=False,
        )

@shared_task
def send_grade_update_notification(student_email, course_name, grade_value):
    subject = f'Обновление оценки по курсу {course_name}'
    message = f'Ваша оценка по курсу {course_name} была обновлена до {grade_value}.'
    from_email = 'system@kbtu.kz'
    to_email = [student_email]

    send_mail(
        subject,
        message,
        from_email,
        to_email,
        fail_silently=False,
    )

@shared_task
def send_weekly_performance_email():
    students = CustomUser.objects.filter(role='student')
    for student in students:
        grades = Grade.objects.filter(student__user=student)
        message = 'Ваши текущие оценки:\n'
        for grade in grades:
            message += f'{grade.course.name}: {grade.grade}\n'
        send_mail(
            'Еженедельное обновление успеваемости',
            message,
            'system@kbtu.kz',
            [student.email],
            fail_silently=False,
        )


@shared_task
def send_daily_report():
    today = timezone.now().date()
    students = Student.objects.all()

    report_data = []

    for student in students:
        attendance_records = Attendance.objects.filter(student=student, date=today)
        attendance_status = attendance_records[0].status if attendance_records else 'Нет данных'

        grades = Grade.objects.filter(student=student)

        student_data = {
            'student_name': student.user.get_full_name(),
            'student_email': student.user.email,
            'attendance_status': attendance_status,
            'grades': grades,
        }

        report_data.append(student_data)

    subject = f'Ежедневный отчет за {today.strftime("%d.%m.%Y")}'
    from_email = 'system@kbtu.kz'
    to_emails = [admin.email for admin in CustomUser.objects.filter(role='admin')]

    message = render_to_string('daily_report_email.html', {'report_data': report_data, 'date': today})

    send_mail(
        subject,
        '',
        from_email,
        to_emails,
        html_message=message,
        fail_silently=False,
    )