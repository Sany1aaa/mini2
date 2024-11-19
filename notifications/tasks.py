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
    """
    Task to send a daily attendance reminder email to all students.
    """
    students = CustomUser.objects.filter(role='student')
    for student in students:
        send_mail(
            subject='Attendance Reminder',
            message='Please mark your attendance for today.',
            from_email='system@kbtu.kz',
            recipient_list=[student.email],
            fail_silently=False,
        )

@shared_task
def send_grade_update_notification(student_email, course_name, grade_value):
    """
    Task to send an email notification to a student about a grade update.
    """
    subject = f'Grade Update for {course_name}'
    message = f'Your grade for the course {course_name} has been updated to {grade_value}.'
    from_email = 'system@kbtu.kz'
    recipient_list = [student_email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )

@shared_task
def send_weekly_performance_email():
    """
    Task to send a weekly email to each student with their current grades.
    """
    students = CustomUser.objects.filter(role='student')
    for student in students:
        grades = Grade.objects.filter(student__user=student)
        message = 'Your current grades:\n'
        for grade in grades:
            message += f'{grade.course.name}: {grade.grade}\n'
        
        send_mail(
            subject='Weekly Performance Update',
            message=message,
            from_email='system@kbtu.kz',
            recipient_list=[student.email],
            fail_silently=False,
        )

@shared_task
def send_daily_report():
    """
    Task to send a daily report email to all admins with students' attendance and grades.
    """
    today = timezone.now().date()
    students = Student.objects.all()

    report_data = []

    for student in students:
        attendance_records = Attendance.objects.filter(student=student, date=today)
        attendance_status = attendance_records[0].status if attendance_records else 'No data available'

        grades = Grade.objects.filter(student=student)

        student_data = {
            'student_name': student.user.get_full_name(),
            'student_email': student.user.email,
            'attendance_status': attendance_status,
            'grades': grades,
        }

        report_data.append(student_data)

    subject = f'Daily Report for {today.strftime("%d.%m.%Y")}'
    from_email = 'system@kbtu.kz'
    recipient_list = [admin.email for admin in CustomUser.objects.filter(role='admin')]

    message = render_to_string('daily_report_email.html', {'report_data': report_data, 'date': today})

    send_mail(
        subject=subject,
        message='',
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=message,
        fail_silently=False,
    )
