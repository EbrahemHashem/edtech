
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Course, Enrollment


User = get_user_model()


class CourseAPITests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="TestPassword123!",
        )
        self.staff = User.objects.create_user(
            username="staff1",
            password="TestPassword123!",
            is_staff=True,
        )

        self.published_course = Course.objects.create(
        title="Python Basics",
        description="Learn Python",
        price=100,
        is_published=True,
        instructor=self.staff,  # Add this
        )

        self.unpublished_course = Course.objects.create(
            title="Advanced Python",
            description="Advanced topics",
            price=200,
            is_published=False,
            instructor=self.staff,  # Add this
        )

        self.client = APIClient()

    def test_list_published_courses(self):
        response = self.client.get(reverse("course-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Python Basics")

    def test_unpublished_course_is_not_visible(self):
        response = self.client.get(
            reverse(
                "course-detail",
                kwargs={"pk": self.unpublished_course.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_staff_can_create_course(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("course-list-create"),
            {
                "title": "REST API Development",
                "description": "Build REST APIs",
                "price": "600.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Course.objects.filter(
                title="REST API Development"
            ).exists()
        )

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("course-list-create"),
            {
                "title": "Unauthorized Course",
                "description": "Test",
                "price": "300.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_negative_course_price_is_rejected(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.post(
            reverse("course-list-create"),
            {
                "title": "Invalid Course",
                "description": "Test",
                "price": "-100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_student_cannot_enroll_without_authentication(self):
        response = self.client.post(
            reverse("enrollment-list-create"),
            {"course": self.published_course.pk},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_student_can_enroll(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("enrollment-list-create"),
            {"course": self.published_course.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student,
                course=self.published_course,
            ).exists()
        )

    def test_student_cannot_enroll_twice(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.published_course,
        )
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            reverse("enrollment-list-create"),
            {"course": self.published_course.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            Enrollment.objects.filter(
                student=self.student,
                course=self.published_course,
            ).count(),
            1,
        )

    def test_student_sees_only_own_enrollments(self):
        another_student = User.objects.create_user(
            username="student2",
            password="TestPassword123!",
        )

        Enrollment.objects.create(
            student=self.student,
            course=self.published_course,
        )
        Enrollment.objects.create(
            student=another_student,
            course=self.unpublished_course,
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.get(
            reverse("enrollment-list-create")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["course"],
            self.published_course.pk,
        )
