from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.permissions import is_admin, is_instructor


class StudentAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return is_admin(request.user)


class CourseAccessPermission(BasePermission):
    message = "You can only modify courses that you teach."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return is_admin(request.user) or is_instructor(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return is_admin(request.user) or obj.instructor_id == request.user.id


class EnrollmentAccessPermission(BasePermission):
    message = "You can only manage enrolments for courses that you teach."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return is_admin(request.user) or is_instructor(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return is_admin(request.user) or obj.course.instructor_id == request.user.id


class AttendanceAccessPermission(BasePermission):
    message = "You can only manage attendance for courses that you teach."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return is_admin(request.user) or is_instructor(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return is_admin(request.user) or obj.enrollment.course.instructor_id == request.user.id
