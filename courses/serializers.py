from rest_framework import serializers

from .models import Course, Enrollment, Payment

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "price",
            "is_published",
            "created_at",
        ]
        read_only_fields = ["id", "is_published", "created_at"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Course price must be greater than zero."
            )
        return value

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "course",
            "status",
            "enrolled_at",
        ]
        read_only_fields = ["id", "status", "enrolled_at"]

    def validate_course(self, course):
        if not course.is_published:
            raise serializers.ValidationError(
                "You can only enroll in published courses."
            )

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            already_enrolled = Enrollment.objects.filter(
                student=request.user,
                course=course,
            ).exists()

            if already_enrolled:
                raise serializers.ValidationError(
                    "You are already enrolled in this course."
                )

        return course

    def create(self, validated_data):
        request = self.context["request"]

        return Enrollment.objects.create(
            student=request.user,
            **validated_data,
        )
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "enrollment",
            "amount",
            "status",
            "provider_transaction_id",
            "created_at",
        ]
        read_only_fields = fields


