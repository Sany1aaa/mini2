from django.core import mail
from django.test import TestCase
from unittest.mock import patch
from users.models import CustomUser
from courses.models import Course
from grades.models import Grade
from attendance.models import Attendance
from students.models import Student
from django.utils import timezone
from notifications.tasks import (send_grade_update_notification, send_weekly_performance_email,
                                 send_daily_report, send_daily_attendance_reminder)


class SendDailyAttendanceReminderTest(TestCase):
    def setUp(self):
        self.student1 = CustomUser.objects.create_user(
            email='student1@example.com',
            username='student1',
            password='password',
            role='student'
        )
        self.student2 = CustomUser.objects.create_user(
            email='student2@example.com',
            username='student2',
            password='password',
            role='student'
        )
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )

    def test_send_daily_attendance_reminder(self):
        send_daily_attendance_reminder()

        self.assertEqual(len(mail.outbox), 2)

        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn('student1@example.com', recipients)
        self.assertIn('student2@example.com', recipients)
        self.assertNotIn('teacher@example.com', recipients)

        for email in mail.outbox:
            self.assertEqual(email.subject, 'Attendance Reminder')
            self.assertEqual(email.body, 'Please mark your attendance for today.')
            self.assertEqual(email.from_email, 'system@kbtu.kz')


class NotificationTasksTest(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com', username='teacher', password='password', role='teacher'
        )

    @patch('notifications.tasks.send_mail')
    def test_send_grade_update_notification(self, mock_send_mail):
        student_email = 'student@example.com'
        course_name = 'Math'
        grade_value = 'A'

        send_grade_update_notification(student_email, course_name, grade_value)

        mock_send_mail.assert_called_once_with(
            f'Обновление оценки по курсу {course_name}',
            f'Ваша оценка по курсу {course_name} была обновлена до {grade_value}.',
            'system@kbtu.kz',
            [student_email],
            fail_silently=False,
        )

    @patch('notifications.tasks.send_mail')
    def test_send_weekly_performance_email(self, mock_send_mail):
        student_user = CustomUser.objects.create_user(
            email='student@example.com', username='student', password='password', role='student'
        )
        student = Student.objects.create(user=student_user)

        course = Course.objects.create(name="Science", description="Science Course", instructor=self.teacher)

        Grade.objects.create(student=student, course=course, grade='B', teacher_id=self.teacher.id)

        send_weekly_performance_email()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Ваши текущие оценки:', email_call_args[1])
        self.assertIn('Science: B', email_call_args[1])

    @patch('notifications.tasks.send_mail')
    def test_send_daily_report(self, mock_send_mail):
        admin_user = CustomUser.objects.create_user(
            email='admin@example.com', username='admin', password='password', role='admin'
        )
        student_user = CustomUser.objects.create_user(
            email='student@example.com', username='student', password='password', role='student'
        )
        student = Student.objects.create(user=student_user)

        course = Course.objects.create(name="Math", description="Math Course", instructor=self.teacher)

        Attendance.objects.create(student=student, course=course, date=timezone.now().date(), status='Present')

        Grade.objects.create(student=student, course=course, grade='A', teacher_id=self.teacher.id)

        send_daily_report()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Ежедневный отчет', email_call_args[0])
        self.assertIn(admin_user.email, email_call_args[3])