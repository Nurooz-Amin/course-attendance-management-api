from rest_framework.permissions import BasePermission

from .models import Profile


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
        return Profile.Role.ADMIN
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", None)


def is_admin(user):
    return get_user_role(user) == Profile.Role.ADMIN


def is_instructor(user):
    return get_user_role(user) == Profile.Role.INSTRUCTOR


def is_student(user):
    return get_user_role(user) == Profile.Role.STUDENT


class IsAdmin(BasePermission):
    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return is_admin(request.user)


class IsAdminOrInstructor(BasePermission):
    message = "Only administrators or instructors can perform this action."

    def has_permission(self, request, view):
        return is_admin(request.user) or is_instructor(request.user)
