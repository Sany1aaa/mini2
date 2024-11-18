from django.test import TestCase
from students.models import Student
from users.models import CustomUser
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course


class StudentModelTest(TestCase):
    def setUp(self):
        user = CustomUser.objects.create_user(
            email='teststudent@kbtu.kz',
            username='teststudent',
            password='password',
            role='student'
        )
        Student.objects.create(user=user, dob='2000-01-01')

    def test_student_creation(self):
        student = Student.objects.get(user__email='teststudent@kbtu.kz')
        self.assertEqual(student.user.role, 'student')

class StudentAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='admin@kbtu.kz',
            username='admin',
            password='password',
            role='admin'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_students(self):
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_access_teacher_endpoints(self):
        student_user = CustomUser.objects.create_user(
            email='student@kbtu.kz',
            username='student',
            password='password',
            role='student'
        )
        self.client.force_authenticate(user=student_user)
        url = reverse('grade-list')
        response = self.client.post(url, data={'grade': 'A'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_grade(self):
        teacher_user = CustomUser.objects.create_user(
            email='testteacher2@kbtu.kz',
            username='testteacher2',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=teacher_user)

        student_user = CustomUser.objects.create_user(
            email='teststudent2@kbtu.kz',
            username='teststudent2',
            password='password',
            role='student'
        )
        student = Student.objects.create(user=student_user, dob='2000-01-01')
        course = Course.objects.create(name="Test Course", description="A test course", instructor=teacher_user)

        url = reverse('grade-list')
        data = {
            'student': student.user.email,
            'course': course.name,
            'grade': 'A',
            'teacher': teacher_user.email
        }

        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_list_caching(self):
        url = reverse('course-list')
        import time

        start_time = time.time()
        self.client.get(url)
        first_response_time = time.time() - start_time

        start_time = time.time()
        self.client.get(url)
        second_response_time = time.time() - start_time

        self.assertTrue(second_response_time < first_response_time)