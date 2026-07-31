from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from accounts.permissions import is_admin, is_instructor
from accounts.serializers import UserSummarySerializer
from accounts.models import Profile
from .models import Attendance, Course, Enrollment, Student


class StudentSummarySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ("id", "registration_number", "name")

    def get_name(self, obj: Student) -> str:
        return obj.user.get_full_name() or obj.user.username


class StudentSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
    )

    class Meta:
        model = Student
        fields = ("id", "user", "user_id", "registration_number", "phone", "joined_on")
        read_only_fields = ("id", "joined_on")

    def validate_user_id(self, user):
        profile = getattr(user, "profile", None)
        if not profile or profile.role != Profile.Role.STUDENT:
            raise serializers.ValidationError("The selected user must have the student role.")
        existing_student = getattr(user, "student_profile", None)
        if existing_student and (not self.instance or existing_student.pk != self.instance.pk):
            raise serializers.ValidationError("This user already has a student profile.")
        return user

    def validate_registration_number(self, value):
        queryset = Student.objects.filter(registration_number__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("This registration number is already in use.")
        return value.upper()


class CourseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "code", "title")


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSummarySerializer(read_only=True)
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="instructor",
        write_only=True,
        required=False,
    )
    enrolled_students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "code", "title", "description", "instructor", "instructor_id",
            "is_active", "enrolled_students_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "enrolled_students_count")

    def validate_code(self, value):
        normalized = value.strip().upper()
        queryset = Course.objects.filter(code__iexact=normalized)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A course with this code already exists.")
        return normalized

    def validate_instructor_id(self, user):
        profile = getattr(user, "profile", None)
        if not user.is_staff and (not profile or profile.role not in {Profile.Role.ADMIN, Profile.Role.INSTRUCTOR}):
            raise serializers.ValidationError("The selected user must be an instructor or administrator.")
        return user

    def validate(self, attrs):
        request = self.context.get("request")
        if request and is_instructor(request.user):
            selected = attrs.get("instructor", getattr(self.instance, "instructor", request.user))
            if selected != request.user:
                raise serializers.ValidationError({"instructor_id": "Instructors can only assign courses to themselves."})
        if not self.instance and request and is_admin(request.user) and not attrs.get("instructor"):
            raise serializers.ValidationError({"instructor_id": "This field is required for administrators."})
        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSummarySerializer(read_only=True)
    student = StudentSummarySerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source="course", write_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.select_related("user"), source="student", write_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "course", "course_id", "student", "student_id", "enrolled_on", "active")
        read_only_fields = ("id", "enrolled_on")
        validators = []

    def validate(self, attrs):
        course = attrs.get("course", getattr(self.instance, "course", None))
        student = attrs.get("student", getattr(self.instance, "student", None))
        request = self.context.get("request")

        if course and not course.is_active:
            raise serializers.ValidationError({"course_id": "Students cannot be enrolled in an inactive course."})
        if request and is_instructor(request.user) and course.instructor_id != request.user.id:
            raise serializers.ValidationError("You can only enrol students in courses that you teach.")

        duplicate = Enrollment.objects.filter(course=course, student=student)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError("This student is already enrolled in the selected course.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError("This student is already enrolled in the selected course.") from exc


class AttendanceSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    enrollment_id = serializers.PrimaryKeyRelatedField(
        queryset=Enrollment.objects.select_related("course", "student__user"),
        source="enrollment",
        write_only=True,
    )
    marked_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = (
            "id", "enrollment", "enrollment_id", "date", "status", "marked_by",
            "remarks", "created_at", "updated_at",
        )
        read_only_fields = ("id", "marked_by", "created_at", "updated_at")
        validators = []

    def validate(self, attrs):
        enrollment = attrs.get("enrollment", getattr(self.instance, "enrollment", None))
        date = attrs.get("date", getattr(self.instance, "date", None))
        request = self.context.get("request")

        if enrollment and not enrollment.active:
            raise serializers.ValidationError({"enrollment_id": "Attendance cannot be marked for an inactive enrolment."})
        if date and enrollment and date < enrollment.enrolled_on:
            raise serializers.ValidationError({"date": "Attendance date cannot be before the enrolment date."})
        if date and date > timezone.localdate():
            raise serializers.ValidationError({"date": "Attendance cannot be marked for a future date."})
        if request and is_instructor(request.user) and enrollment.course.instructor_id != request.user.id:
            raise serializers.ValidationError("You can only mark attendance for courses that you teach.")

        duplicate = Attendance.objects.filter(enrollment=enrollment, date=date)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError("Attendance already exists for this student, course and date.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError("Attendance already exists for this student, course and date.") from exc
