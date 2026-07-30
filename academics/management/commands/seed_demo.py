from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from academics.models import Attendance, Course, Enrollment, Student


class Command(BaseCommand):
    help = "Create demo users and sample course/attendance data."

    @transaction.atomic
    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "first_name": "System", "last_name": "Admin"},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("AdminPass123")
        admin.save()
        admin.profile.role = Profile.Role.ADMIN
        admin.profile.save()

        instructor, _ = User.objects.get_or_create(
            username="instructor",
            defaults={"email": "instructor@example.com", "first_name": "Sara", "last_name": "Khan"},
        )
        instructor.set_password("InstructorPass123")
        instructor.save()
        instructor.profile.role = Profile.Role.INSTRUCTOR
        instructor.profile.save()

        student_user, _ = User.objects.get_or_create(
            username="student",
            defaults={"email": "student@example.com", "first_name": "Ali", "last_name": "Ahmed"},
        )
        student_user.set_password("StudentPass123")
        student_user.save()
        student_user.profile.role = Profile.Role.STUDENT
        student_user.profile.save()

        student, _ = Student.objects.get_or_create(
            user=student_user,
            defaults={"registration_number": "STU-001", "phone": "+92-300-0000000"},
        )
        course, _ = Course.objects.get_or_create(
            code="DJ-101",
            defaults={
                "title": "Django REST Framework",
                "description": "Build secure and testable REST APIs with Django REST Framework.",
                "instructor": instructor,
            },
        )
        enrollment, _ = Enrollment.objects.get_or_create(course=course, student=student)
        demo_enrolled_on = timezone.localdate() - timedelta(days=7)
        Enrollment.objects.filter(pk=enrollment.pk).update(enrolled_on=demo_enrolled_on)
        enrollment.refresh_from_db()
        Attendance.objects.get_or_create(
            enrollment=enrollment,
            date=timezone.localdate() - timedelta(days=1),
            defaults={"status": Attendance.Status.PRESENT, "marked_by": instructor, "remarks": "Demo attendance record."},
        )

        self.stdout.write(self.style.SUCCESS("Demo data created or refreshed."))
        self.stdout.write("Admin: admin / AdminPass123")
        self.stdout.write("Instructor: instructor / InstructorPass123")
        self.stdout.write("Student: student / StudentPass123")
