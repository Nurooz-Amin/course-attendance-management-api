from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """Public portfolio landing page for the API project."""
    context = {
        "project_name": "Course & Attendance Management API",
        "api_root_url": reverse("api-root"),
        "docs_url": reverse("swagger-ui"),
        "redoc_url": reverse("redoc"),
        "admin_url": reverse("admin:index"),
        "health_url": reverse("health-check"),
    }
    return render(request, "home.html", context)


@require_GET
def health_check(request):
    """Small public endpoint used for local checks and deployment monitoring."""
    return JsonResponse(
        {
            "status": "ok",
            "service": "course-attendance-management-api",
            "version": "1.1.0",
            "documentation": request.build_absolute_uri(reverse("swagger-ui")),
        }
    )
