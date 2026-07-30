from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Profile
from academics.models import Attendance, Course, Enrollment, Student


class PublicEndpointTests(APITestCase):
    def test_homepage_is_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Course &amp; Attendance Management API")
        self.assertContains(response, "Explore Swagger API")

    def test_health_check_is_public(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "course-attendance-management-api")

    def test_api_documentation_is_available(self):
        schema_response = self.client.get("/api/schema/")
        swagger_response = self.client.get("/api/docs/")
        redoc_response = self.client.get("/api/redoc/")

        self.assertEqual(schema_response.status_code, status.HTTP_200_OK)
        self.assertEqual(swagger_response.status_code, status.HTTP_200_OK)
        self.assertEqual(redoc_response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_list_courses(self):
        response = self.client.get("/api/courses/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseAttendanceAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="StrongAdminPass123"
        )
        self.admin.profile.role = Profile.Role.ADMIN
        self.admin.profile.save()

        self.instructor = User.objects.create_user(
            username="instructor", email="instructor@example.com", password="StrongPass123"
        )
        self.instructor.profile.role = Profile.Role.INSTRUCTOR
        self.instructor.profile.save()

        self.other_instructor = User.objects.create_user(
            username="other_instructor", email="other@example.com", password="StrongPass123"
        )
        self.other_instructor.profile.role = Profile.Role.INSTRUCTOR
        self.other_instructor.profile.save()

        self.student_user = User.objects.create_user(
            username="student", email="student@example.com", password="StrongPass123"
        )
        self.student_user.profile.role = Profile.Role.STUDENT
        self.student_user.profile.save()
        self.student = Student.objects.create(
            user=self.student_user, registration_number="STU-001"
        )

        self.other_student_user = User.objects.create_user(
            username="other_student", email="otherstudent@example.com", password="StrongPass123"
        )
        self.other_student_user.profile.role = Profile.Role.STUDENT
        self.other_student_user.profile.save()
        self.other_student = Student.objects.create(
            user=self.other_student_user, registration_number="STU-002"
        )

        self.course = Course.objects.create(
            code="DJ-101", title="Django REST Framework", instructor=self.instructor
        )
        self.other_course = Course.objects.create(
            code="PY-201", title="Advanced Python", instructor=self.other_instructor
        )
        self.enrollment = Enrollment.objects.create(course=self.course, student=self.student)
        self.other_enrollment = Enrollment.objects.create(
            course=self.other_course, student=self.other_student
        )

    def authenticate(self, username, password="StrongPass123"):
        response = self.client.post(
            "/api/auth/token/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    def test_student_registration_creates_user_profile(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newstudent",
                "email": "newstudent@example.com",
                "password": "SecurePass!234",
                "first_name": "New",
                "last_name": "Student",
                "registration_number": "stu-003",
                "phone": "+92-300-1111111",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newstudent")
        self.assertEqual(response.data["role"], Profile.Role.STUDENT)
        self.assertTrue(Student.objects.filter(registration_number="STU-003").exists())

    def test_duplicate_registration_values_are_rejected(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "student",
                "email": "student@example.com",
                "password": "SecurePass!234",
                "registration_number": "STU-001",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("registration_number", response.data)

    def test_jwt_authentication_returns_access_and_refresh_tokens(self):
        tokens = self.authenticate("instructor")

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "instructor")
        self.assertEqual(response.data["role"], Profile.Role.INSTRUCTOR)

    def test_instructor_can_create_own_course_without_instructor_id(self):
        self.authenticate("instructor")
        response = self.client.post(
            "/api/courses/",
            {
                "code": "api-301",
                "title": "Production APIs",
                "description": "API design, testing and deployment.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Course.objects.get(code="API-301")
        self.assertEqual(created.instructor, self.instructor)

    def test_instructor_cannot_assign_course_to_another_instructor(self):
        self.authenticate("instructor")
        response = self.client.post(
            "/api/courses/",
            {
                "code": "SEC-301",
                "title": "API Security",
                "instructor_id": self.other_instructor.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("instructor_id", response.data)

    def test_admin_must_select_instructor_when_creating_course(self):
        self.authenticate("admin", "StrongAdminPass123")
        response = self.client.post(
            "/api/courses/",
            {"code": "ADM-101", "title": "Admin-created Course"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("instructor_id", response.data)

    def test_duplicate_enrollment_is_rejected(self):
        self.authenticate("instructor")
        response = self.client.post(
            "/api/enrollments/",
            {"course_id": self.course.id, "student_id": self.student.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already enrolled", str(response.data).lower())

    def test_instructor_can_create_attendance(self):
        self.authenticate("instructor")
        response = self.client.post(
            "/api/attendance/",
            {
                "enrollment_id": self.enrollment.id,
                "date": timezone.localdate().isoformat(),
                "status": Attendance.Status.PRESENT,
                "remarks": "Participated in the practical session.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attendance = Attendance.objects.get(enrollment=self.enrollment)
        self.assertEqual(attendance.marked_by, self.instructor)
        self.assertEqual(attendance.status, Attendance.Status.PRESENT)

    def test_duplicate_attendance_record_is_rejected(self):
        Attendance.objects.create(
            enrollment=self.enrollment,
            date=timezone.localdate(),
            status=Attendance.Status.PRESENT,
            marked_by=self.instructor,
        )
        self.authenticate("instructor")
        response = self.client.post(
            "/api/attendance/",
            {
                "enrollment_id": self.enrollment.id,
                "date": timezone.localdate().isoformat(),
                "status": Attendance.Status.ABSENT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Attendance.objects.filter(enrollment=self.enrollment).count(), 1)
        self.assertIn("already exists", str(response.data).lower())

    def test_future_attendance_date_is_rejected(self):
        self.authenticate("instructor")
        tomorrow = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            "/api/attendance/",
            {
                "enrollment_id": self.enrollment.id,
                "date": tomorrow.isoformat(),
                "status": Attendance.Status.PRESENT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("future", str(response.data).lower())

    def test_instructor_cannot_mark_attendance_for_another_course(self):
        self.authenticate("instructor")
        response = self.client.post(
            "/api/attendance/",
            {
                "enrollment_id": self.other_enrollment.id,
                "date": timezone.localdate().isoformat(),
                "status": Attendance.Status.PRESENT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("courses that you teach", str(response.data).lower())

    def test_student_cannot_create_attendance(self):
        self.authenticate("student")
        response = self.client.post(
            "/api/attendance/",
            {
                "enrollment_id": self.enrollment.id,
                "date": timezone.localdate().isoformat(),
                "status": Attendance.Status.PRESENT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_only_view_own_attendance(self):
        Attendance.objects.create(
            enrollment=self.enrollment,
            date=timezone.localdate(),
            status=Attendance.Status.LATE,
            marked_by=self.instructor,
        )
        Attendance.objects.create(
            enrollment=self.other_enrollment,
            date=timezone.localdate(),
            status=Attendance.Status.PRESENT,
            marked_by=self.other_instructor,
        )

        self.authenticate("student")
        response = self.client.get("/api/attendance/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], Attendance.Status.LATE)
        self.assertEqual(
            response.data["results"][0]["enrollment"]["student"]["registration_number"],
            self.student.registration_number,
        )
