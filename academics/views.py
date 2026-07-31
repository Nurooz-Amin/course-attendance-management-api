from django.db.models import Count
from rest_framework import viewsets

from accounts.permissions import is_admin, is_instructor
from .models import Attendance, Course, Enrollment, Student
from .permissions import (
    AttendanceAccessPermission,
    CourseAccessPermission,
    EnrollmentAccessPermission,
    StudentAccessPermission,
)
from .serializers import AttendanceSerializer, CourseSerializer, EnrollmentSerializer, StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [StudentAccessPermission]
    search_fields = ("registration_number", "user__username", "user__first_name", "user__last_name", "user__email")
    ordering_fields = ("registration_number", "joined_on")

    def get_queryset(self):
        queryset = Student.objects.select_related("user", "user__profile")
        user = self.request.user
        if is_admin(user):
            return queryset
        if is_instructor(user):
            return queryset.filter(enrollments__course__instructor=user).distinct()
        return queryset.filter(user=user)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [CourseAccessPermission]
    search_fields = ("code", "title", "description", "instructor__username", "instructor__first_name", "instructor__last_name")
    ordering_fields = ("code", "title", "created_at")

    def get_queryset(self):
        queryset = Course.objects.select_related("instructor", "instructor__profile").annotate(
            enrolled_students_count=Count("enrollments", distinct=True)
        )
        active = self.request.query_params.get("active")
        if active in {"true", "false"}:
            queryset = queryset.filter(is_active=(active == "true"))
        return queryset

    def perform_create(self, serializer):
        if is_instructor(self.request.user):
            serializer.save(instructor=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if is_instructor(self.request.user):
            serializer.save(instructor=self.request.user)
        else:
            serializer.save()


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [EnrollmentAccessPermission]
    search_fields = ("course__code", "course__title", "student__registration_number", "student__user__username")
    ordering_fields = ("enrolled_on", "course__code", "student__registration_number")

    def get_queryset(self):
        queryset = Enrollment.objects.select_related("course", "course__instructor", "student", "student__user")
        user = self.request.user
        if is_admin(user):
            pass
        elif is_instructor(user):
            queryset = queryset.filter(course__instructor=user)
        else:
            queryset = queryset.filter(student__user=user)

        course_id = self.request.query_params.get("course")
        student_id = self.request.query_params.get("student")
        active = self.request.query_params.get("active")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if active in {"true", "false"}:
            queryset = queryset.filter(active=(active == "true"))
        return queryset


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [AttendanceAccessPermission]
    search_fields = (
        "enrollment__course__code", "enrollment__course__title",
        "enrollment__student__registration_number", "enrollment__student__user__username",
    )
    ordering_fields = ("date", "status", "created_at")

    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            "marked_by", "marked_by__profile", "enrollment__course",
            "enrollment__course__instructor", "enrollment__student", "enrollment__student__user",
        )
        user = self.request.user
        if is_admin(user):
            pass
        elif is_instructor(user):
            queryset = queryset.filter(enrollment__course__instructor=user)
        else:
            queryset = queryset.filter(enrollment__student__user=user)

        course_id = self.request.query_params.get("course")
        student_id = self.request.query_params.get("student")
        date = self.request.query_params.get("date")
        status = self.request.query_params.get("status")
        if course_id:
            queryset = queryset.filter(enrollment__course_id=course_id)
        if student_id:
            queryset = queryset.filter(enrollment__student_id=student_id)
        if date:
            queryset = queryset.filter(date=date)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)
