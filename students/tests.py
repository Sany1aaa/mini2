from django.test import TestCase
from students.models import Student
from users.models import CustomUser
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course
from rest_framework.exceptions import NotFound

class StudentModelTest(TestCase):
    def setUp(self):
        """
        Create a student and a related user for testing.
        """
        user = CustomUser.objects.create_user(
            email='teststudent@kbtu.kz',
            username='teststudent',
            password='password',
            role='student'
        )
        self.student = Student.objects.create(user=user, dob='2000-01-01')

    def test_student_creation(self):
        """
        Test the creation of a student and verify user role.
        """
        student = Student.objects.get(user__email='teststudent@kbtu.kz')
        self.assertEqual(student.user.role, 'student')
        self.assertEqual(student.dob, '2000-01-01')

    def test_student_str_method(self):
        """
        Test the string representation of the student model.
        """
        self.assertEqual(str(self.student), 'teststudent')

class StudentAPITest(APITestCase):
    def setUp(self):
        """
        Create users for API testing and authenticate admin.
        """
        self.admin_user = CustomUser.objects.create_user(
            email='admin@kbtu.kz',
            username='admin',
            password='password',
            role='admin'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create a student for use in API tests
        self.student_user = CustomUser.objects.create_user(
            email='student@kbtu.kz',
            username='student',
            password='password',
            role='student'
        )
        self.student = Student.objects.create(user=self.student_user, dob='2000-01-01')

        # Create a course for tests involving grades
        self.course = Course.objects.create(name="Calculus", description="A calculus course", instructor=self.admin_user)

    def test_get_students(self):
        """
        Test the GET request for fetching the list of students.
        """
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('teststudent@kbtu.kz', str(response.data))

    def test_student_cannot_access_teacher_endpoints(self):
        """
        Test that a student cannot access teacher-only endpoints, such as creating grades.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('grade-list')
        response = self.client.post(url, data={'grade': 'A'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_grade(self):
        """
        Test that a teacher can create a grade for a student.
        """
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
        course = Course.objects.create(name="Physics", description="Physics course", instructor=teacher_user)

        url = reverse('grade-list')
        data = {
            'student': student.user.email,
            'course': course.name,
            'grade': 'A',
            'teacher': teacher_user.email
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_grade_view(self):
        """
        Test that a student can view their grade.
        """
        grade = Grade.objects.create(student=self.student, course=self.course, grade='B', teacher=self.admin_user)
        url = reverse('grade-detail', kwargs={'pk': grade.id})
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['grade'], 'B')

    def test_invalid_grade_creation(self):
        """
        Test that creating a grade with invalid data (e.g., missing required fields) results in an error.
        """
        url = reverse('grade-list')
        data = {
            'student': 'nonexistentstudent@kbtu.kz',  # Invalid email
            'course': 'Nonexistent Course',
            'grade': 'A',
            'teacher': self.admin_user.email
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_list_caching(self):
        """
        Test that course list responses are cached for performance optimization.
        """
        url = reverse('course-list')
        import time

        start_time = time.time()
        self.client.get(url)
        first_response_time = time.time() - start_time

        start_time = time.time()
        self.client.get(url)
        second_response_time = time.time() - start_time

        # Ensure the second response is faster, indicating caching
        self.assertTrue(second_response_time < first_response_time)

    def test_course_not_found(self):
        """
        Test the scenario where a course is not found, should return 404 error.
        """
        url = reverse('course-detail', kwargs={'pk': 999})  # Nonexistent course ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_teacher_view_assigned_courses(self):
        """
        Test that a teacher can view their assigned courses.
        """
        teacher_user = CustomUser.objects.create_user(
            email='testteacher@kbtu.kz',
            username='testteacher',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=teacher_user)
        course = Course.objects.create(name="History", description="A history course", instructor=teacher_user)

        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(course.name, str(response.data))

    def test_course_creation_by_teacher(self):
        """
        Test that a teacher can create a course.
        """
        teacher_user = CustomUser.objects.create_user(
            email='testteacher3@kbtu.kz',
            username='testteacher3',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=teacher_user)

        url = reverse('course-list')
        data = {
            'name': 'Advanced Mathematics',
            'description': 'A deep dive into advanced mathematics.',
            'instructor': teacher_user.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Advanced Mathematics')
