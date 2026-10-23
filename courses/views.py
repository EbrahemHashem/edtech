from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer


class CourseListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        courses = Course.objects.filter(is_published=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can create courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CourseSerializer(data=request.data)

        if serializer.is_valid():
            course = serializer.save()
            return Response(
                CourseSerializer(course).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class CourseDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        return get_object_or_404(
            Course.objects.filter(is_published=True),
            pk=pk,
        )

    def get(self, request, pk):
        course = self.get_object(pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can update courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(
            course,
            data=request.data,
        )

        if serializer.is_valid():
            course = serializer.save()
            return Response(
                CourseSerializer(course).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can update courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            course = serializer.save()
            return Response(
                CourseSerializer(course).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can delete courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, pk=pk)

        try:
            course.delete()
        except Exception:
            return Response(
                {"detail": "Course could not be deleted."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class EnrollmentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            student=request.user
        ).select_related("course")

        serializer = EnrollmentSerializer(
            enrollments,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EnrollmentSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            enrollment = serializer.save()
            return Response(
                EnrollmentSerializer(enrollment).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
