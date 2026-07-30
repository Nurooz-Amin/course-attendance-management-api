from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("instructor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="courses_taught", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("registration_number", models.CharField(max_length=40, unique=True)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("joined_on", models.DateField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["registration_number"]},
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("enrolled_on", models.DateField(auto_now_add=True)),
                ("active", models.BooleanField(default=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="academics.course")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="academics.student")),
            ],
            options={"ordering": ["-enrolled_on", "course__code"]},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late"), ("excused", "Excused")], max_length=10)),
                ("remarks", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="academics.enrollment")),
                ("marked_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attendance_marked", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date", "enrollment__course__code", "enrollment__student__registration_number"]},
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["instructor", "is_active"], name="course_teacher_active_idx"),
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(fields=("course", "student"), name="unique_course_student_enrollment"),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["course", "active"], name="enrol_course_active_idx"),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(fields=["student", "active"], name="enrol_student_active_idx"),
        ),
        migrations.AddConstraint(
            model_name="attendance",
            constraint=models.UniqueConstraint(fields=("enrollment", "date"), name="unique_daily_attendance"),
        ),
        migrations.AddIndex(
            model_name="attendance",
            index=models.Index(fields=["date", "status"], name="attendance_date_status_idx"),
        ),
    ]
