from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course
from users.models import CustomUser
import time

class CourseAPITests(APITestCase):
    def setUp(self):
        # Create a teacher user and authenticate
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=self.teacher)

    def test_create_course(self):
        # Test the creation of a course
        url = reverse('course-list')
        data = {
            'name': 'Physics',
            'description': 'Physics Course',
            'instructor': self.teacher.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_update_course(self):
        # Test updating an existing course
        course = Course.objects.create(
            name='Math',
            description='Math Course',
            instructor=self.teacher
        )
        url = reverse('course-detail', args=[course.id])
        data = {'name': 'Advanced Math'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, 'Advanced Math')

    def test_delete_course(self):
        # Test deleting a course
        course = Course.objects.create(
            name='Chemistry',
            description='Chemistry Course',
            instructor=self.teacher
        )
        url = reverse('course-detail', args=[course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


class CoursePermissionsTests(APITestCase):
    def setUp(self):
        # Create teacher and student users
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.student = CustomUser.objects.create_user(
            email='student@example.com',
            username='student',
            password='password',
            role='student'
        )
        # Create a course assigned to the teacher
        self.course = Course.objects.create(
            name='Biology',
            description='Biology Course',
            instructor=self.teacher
        )

    def test_student_cannot_create_course(self):
        # Ensure students cannot create a course
        self.client.force_authenticate(user=self.student)
        url = reverse('course-list')
        data = {
            'name': 'History',
            'description': 'History Course',
            'instructor': self.teacher.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_course(self):
        # Ensure teachers can create a course
        self.client.force_authenticate(user=self.teacher)
        url = reverse('course-list')
        data = {
            'name': 'Geography',
            'description': 'Geography Course',
            'instructor': self.teacher.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CourseCachingTests(APITestCase):
    def setUp(self):
        # Create a teacher user and a sample course
        self.teacher = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=self.teacher)
        Course.objects.create(
            name='Art',
            description='Art Course',
            instructor=self.teacher
        )

    def test_course_list_caching(self):
        # Test caching for the course list endpoint
        url = reverse('course-list')

        # First request (uncached, should take longer)
        start_time = time.time()
        response1 = self.client.get(url)
        first_duration = time.time() - start_time

        # Second request (cached, should be faster)
        start_time = time.time()
        response2 = self.client.get(url)
        second_duration = time.time() - start_time

        self.assertEqual(response1.data, response2.data)
        self.assertTrue(second_duration <= first_duration)
