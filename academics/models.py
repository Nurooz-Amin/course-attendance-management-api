from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Profile


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    registration_number = models.CharField(max_length=40, unique=True)
    phone = models.CharField(max_length=30, blank=True)
    joined_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["registration_number"]

    def clean(self):
        profile = getattr(self.user, "profile", None)
        if profile and profile.role != Profile.Role.STUDENT:
            raise ValidationError({"user": "The selected user must have the student role."})

    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name() or self.user.username}"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, related_name="courses_taught")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        indexes = [models.Index(fields=["instructor", "is_active"], name="course_teacher_active_idx")]

    def clean(self):
        profile = getattr(self.instructor, "profile", None)
        allowed_roles = {Profile.Role.ADMIN, Profile.Role.INSTRUCTOR}
        if not self.instructor.is_staff and (not profile or profile.role not in allowed_roles):
            raise ValidationError({"instructor": "The selected user must be an instructor or administrator."})

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_on = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-enrolled_on", "course__code"]
        constraints = [
            models.UniqueConstraint(fields=["course", "student"], name="unique_course_student_enrollment"),
        ]
        indexes = [
            models.Index(fields=["course", "active"], name="enrol_course_active_idx"),
            models.Index(fields=["student", "active"], name="enrol_student_active_idx"),
        ]

    def __str__(self):
        return f"{self.student.registration_number} in {self.course.code}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    marked_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="attendance_marked")
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "enrollment__course__code", "enrollment__student__registration_number"]
        constraints = [
            models.UniqueConstraint(fields=["enrollment", "date"], name="unique_daily_attendance"),
        ]
        indexes = [
            models.Index(fields=["date", "status"], name="attendance_date_status_idx"),
        ]

    def __str__(self):
        return f"{self.enrollment} - {self.date}: {self.status}"
