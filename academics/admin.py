from django.contrib import admin

from .models import Attendance, Course, Enrollment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("registration_number", "user", "phone", "joined_on")
    search_fields = ("registration_number", "user__username", "user__email")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "instructor", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "title", "instructor__username")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_on", "active")
    list_filter = ("active", "course")
    search_fields = ("student__registration_number", "course__code")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "date", "status", "marked_by")
    list_filter = ("status", "date", "enrollment__course")
    search_fields = ("enrollment__student__registration_number", "enrollment__course__code")
