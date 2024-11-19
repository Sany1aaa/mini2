from django.core import mail
from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone
from users.models import CustomUser
from courses.models import Course
from grades.models import Grade
from attendance.models import Attendance
from students.models import Student
from notifications.tasks import (
    send_grade_update_notification,
    send_weekly_performance_email,
    send_daily_report,
    send_daily_attendance_reminder
)


class SendDailyAttendanceReminderTest(TestCase):
    def setUp(self):
        """
        Create test users for attendance reminder tests.
        """
        self.student_one = CustomUser.objects.create_user(
            email='student1@example.com',
            username='student_one',
            password='password',
            role='student'
        )
        self.student_two = CustomUser.objects.create_user(
            email='student2@example.com',
            username='student_two',
            password='password',
            role='student'
        )
        self.instructor = CustomUser.objects.create_user(
            email='instructor@example.com',
            username='instructor',
            password='password',
            role='teacher'
        )

    def test_send_daily_attendance_reminder(self):
        """
        Test that attendance reminder emails are sent only to students.
        """
        send_daily_attendance_reminder()

        # Check that emails are sent to the correct number of recipients
        self.assertEqual(len(mail.outbox), 2)

        # Verify that emails are sent to students, not to the instructor
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn('student1@example.com', recipients)
        self.assertIn('student2@example.com', recipients)
        self.assertNotIn('instructor@example.com', recipients)

        # Verify email contents
        for email in mail.outbox:
            self.assertEqual(email.subject, 'Attendance Reminder')
            self.assertEqual(email.body, 'Please mark your attendance for today.')
            self.assertEqual(email.from_email, 'system@kbtu.kz')


class NotificationTasksTest(TestCase):
    def setUp(self):
        """
        Create a test instructor for use in notification task tests.
        """
        self.instructor = CustomUser.objects.create_user(
            email='instructor@example.com', username='instructor', password='password', role='teacher'
        )

    @patch('notifications.tasks.send_mail')
    def test_send_grade_update_notification(self, mock_send_mail):
        """
        Test that grade update notification emails are sent correctly.
        """
        student_email = 'student@example.com'
        course_title = 'Calculus'
        new_grade = 'A'

        send_grade_update_notification(student_email, course_title, new_grade)

        mock_send_mail.assert_called_once_with(
            f'Grade Update for {course_title}',
            f'Your grade for the course {course_title} has been updated to {new_grade}.',
            'system@kbtu.kz',
            [student_email],
            fail_silently=False,
        )

    @patch('notifications.tasks.send_mail')
    def test_send_weekly_performance_email(self, mock_send_mail):
        """
        Test that weekly performance emails include the correct grades for students.
        """
        student_user = CustomUser.objects.create_user(
            email='student@example.com', username='student', password='password', role='student'
        )
        student_record = Student.objects.create(user=student_user)
        course_record = Course.objects.create(name="Physics", description="Physics Course", instructor=self.instructor)
        Grade.objects.create(student=student_record, course=course_record, grade='B', teacher_id=self.instructor.id)

        send_weekly_performance_email()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Your current grades:', email_call_args[1])
        self.assertIn('Physics: B', email_call_args[1])

    @patch('notifications.tasks.send_mail')
    def test_send_daily_report(self, mock_send_mail):
        """
        Test that daily report emails are sent to admins with the correct data.
        """
        admin_user = CustomUser.objects.create_user(
            email='admin@example.com', username='admin', password='password', role='admin'
        )
        student_user = CustomUser.objects.create_user(
            email='student@example.com', username='student', password='password', role='student'
        )
        student_record = Student.objects.create(user=student_user)
        course_record = Course.objects.create(name="Calculus", description="Calculus Course", instructor=self.instructor)
        Attendance.objects.create(student=student_record, course=course_record, date=timezone.now().date(), status='Present')
        Grade.objects.create(student=student_record, course=course_record, grade='A', teacher_id=self.instructor.id)

        send_daily_report()

        self.assertTrue(mock_send_mail.called)
        email_call_args = mock_send_mail.call_args[0]
        self.assertIn('Daily Report', email_call_args[0])  # Subject check
        self.assertIn(admin_user.email, email_call_args[3])  # Admin recipient check
