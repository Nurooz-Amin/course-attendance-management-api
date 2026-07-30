from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        INSTRUCTOR = "instructor", "Instructor"
        STUDENT = "student", "Student"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
