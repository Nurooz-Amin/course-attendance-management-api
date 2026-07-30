from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, CourseViewSet, EnrollmentViewSet, StudentViewSet

router = DefaultRouter()
router.register("students", StudentViewSet, basename="student")
router.register("courses", CourseViewSet, basename="course")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("attendance", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
