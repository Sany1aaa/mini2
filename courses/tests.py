from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from courses.models import Course
from users.models import CustomUser
import time

class CourseViewSetTest(APITestCase):
    def setUp(self):
        self.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=self.teacher_user)

    def test_create_course(self):
        url = reverse('course-list')
        data = {
            'name': 'Physics',
            'description': 'Physics Course',
            'instructor': self.teacher_user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)

    def test_update_course(self):
        course = Course.objects.create(
            name='Math',
            description='Math Course',
            instructor=self.teacher_user
        )
        url = reverse('course-detail', args=[course.id])
        data = {'name': 'Advanced Math'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, 'Advanced Math')

    def test_delete_course(self):
        course = Course.objects.create(
            name='Chemistry',
            description='Chemistry Course',
            instructor=self.teacher_user
        )
        url = reverse('course-detail', args=[course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)


class CoursePermissionsTest(APITestCase):
    def setUp(self):
        self.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.student_user = CustomUser.objects.create_user(
            email='student@example.com',
            username='student',
            password='password',
            role='student'
        )
        self.course = Course.objects.create(
            name='Biology',
            description='Biology Course',
            instructor=self.teacher_user
        )

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('course-list')
        data = {
            'name': 'History',
            'description': 'History Course',
            'instructor': self.teacher_user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_course(self):
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('course-list')
        data = {
            'name': 'Geography',
            'description': 'Geography Course',
            'instructor': self.teacher_user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CourseCachingTest(APITestCase):
    def setUp(self):
        self.teacher_user = CustomUser.objects.create_user(
            email='teacher@example.com',
            username='teacher',
            password='password',
            role='teacher'
        )
        self.client.force_authenticate(user=self.teacher_user)
        Course.objects.create(
            name='Art',
            description='Art Course',
            instructor=self.teacher_user
        )

    def test_course_list_caching(self):
        url = reverse('course-list')

        # First request (should be slower)
        start_time = time.time()
        response1 = self.client.get(url)
        first_duration = time.time() - start_time

        # Second request (should be faster due to caching)
        start_time = time.time()
        response2 = self.client.get(url)
        second_duration = time.time() - start_time

        self.assertEqual(response1.data, response2.data)
        self.assertTrue(second_duration <= first_duration)