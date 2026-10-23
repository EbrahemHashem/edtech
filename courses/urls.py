
from django.urls import path

from .views import (
    CourseListCreateAPIView,
    CourseDetailAPIView,
    EnrollmentListCreateAPIView,
)

urlpatterns = [
    path(
        "courses/",
        CourseListCreateAPIView.as_view(),
        name="course-list-create",
    ),
    path(
        "courses/<int:pk>/",
        CourseDetailAPIView.as_view(),
        name="course-detail",
    ),
    path(
        "enrollments/",
        EnrollmentListCreateAPIView.as_view(),
        name="enrollment-list-create",
    ),
]
