
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer


class CourseListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        courses = Course.objects.filter(is_published=True)
        serializer = CourseSerializer(courses, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.save(instructor=request.user)

        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_201_CREATED,
        )


class CourseDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_object(self, pk):
        return get_object_or_404(
            Course.objects.filter(is_published=True),
            pk=pk,
        )

    def get(self, request, pk):
        course = self.get_object(pk)
        serializer = CourseSerializer(course)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk)

        serializer = CourseSerializer(
            course,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        course = serializer.save()

        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)

        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        course = serializer.save()

        return Response(
            CourseSerializer(course).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        course.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


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

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = EnrollmentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        enrollment = serializer.save()

        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )
