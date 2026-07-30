# Interview Notes

## Project introduction

I developed a Course and Attendance Management REST API using Django and Django REST Framework. The system manages courses, students, enrolments and daily attendance. I used Django ORM relationships, JWT authentication, role-based permissions and serializer validation. I also wrote API tests for authentication, attendance creation and duplicate-record prevention. I managed development through Git feature branches and tested the endpoints using Postman.

## 30-second explanation

The API has three roles: admin, instructor and student. Administrators can manage all records, instructors can manage their own courses, enrolments and attendance, while students can only view their own academic information. Attendance references an enrolment rather than a student directly, which ensures that attendance can only be marked for a valid student-course relationship. Duplicate attendance is prevented at both serializer and database levels.

## Architecture explanation

```text
Client / Postman / Swagger
          ↓
Django URL routing
          ↓
DRF ViewSets and permission classes
          ↓
Serializers and validation
          ↓
Django ORM models and constraints
          ↓
SQLite database
```

JWT authentication identifies the requester. Permission classes decide whether the action is allowed. Role-filtered querysets ensure the requester cannot retrieve another user's protected records. Serializers validate input before saving, and database constraints provide a second layer of protection.

## Strong technical points

- `select_related()` reduces repeated database queries for related objects.
- `annotate()` provides the course enrolment count efficiently.
- `UniqueConstraint` protects integrity even if serializer validation is bypassed.
- JWT handles authentication while custom permission classes handle authorization.
- Querysets are role-filtered to prevent accidental data exposure.
- Instructor ownership is enforced during both create and update operations.
- Public health and homepage endpoints make the repository easy to demonstrate.
- Automated tests verify successful workflows and expected failures.
- GitHub Actions runs checks, migration validation, and tests automatically.

## Common interview questions

### Why did you use an Enrollment model?

It represents the many-to-many relationship between students and courses and stores relationship-specific information such as enrolment date and active status. Attendance can then reference a valid enrolment.

### Why not connect Attendance directly to Student and Course?

Using separate student and course foreign keys would allow invalid combinations. Referencing `Enrollment` guarantees that the student belongs to the selected course and keeps the model normalized.

### How do you prevent duplicate attendance?

The serializer checks whether a record already exists, and the database enforces a unique constraint on `enrollment` and `date`. The serializer gives a readable response, while the database protects against direct writes and race conditions.

### What is the difference between authentication and authorization?

Authentication confirms who the user is through JWT. Authorization determines what the authenticated user can do using roles, permissions, object ownership and filtered querysets.

### Why did you use serializer validation?

Serializer validation returns clear API errors before invalid data reaches the database. It validates user roles, course ownership, active enrolments, future dates and duplicate records.

### How do object-level permissions work here?

An instructor may pass the general permission check, but the object-level permission verifies that the selected course belongs to that instructor. The queryset is also filtered, so unauthorized records are not exposed during retrieval.

### Why use both permission classes and filtered querysets?

Permission classes block unauthorized actions. Filtered querysets prevent users from even seeing records outside their scope. Using both provides defense in depth.

### Why use JWT?

JWT works well for REST APIs because clients send a bearer token with each request. Access tokens are short-lived and refresh tokens are used to obtain new access tokens without sending credentials repeatedly.

### How did you test the project?

I used DRF's `APITestCase` to test public endpoints, registration, JWT login, course ownership, duplicate enrolments, attendance creation, duplicate prevention, future-date validation and student access restrictions. I also tested requests manually in Postman and Swagger UI.

### How would you scale this project?

I would move to PostgreSQL, introduce bulk attendance operations, cache reports with Redis, use Celery for notifications, add proper observability, and deploy behind Gunicorn and a reverse proxy or managed cloud platform.

## Live demonstration sequence

1. Show the homepage at `http://127.0.0.1:8000/`.
2. Open Swagger at `/api/docs/`.
3. Obtain an instructor JWT token.
4. Authorize Swagger using `Bearer <access-token>`.
5. Display the seeded course and enrolment.
6. Mark attendance.
7. Submit the same record again to show duplicate validation.
8. Submit tomorrow's date to show future-date validation.
9. Log in as a student and show the `403` write restriction.
10. Run `python manage.py test` and show the GitHub Actions workflow.

## Honest improvement discussion

The portfolio version uses SQLite for simplicity. For production, I would use PostgreSQL, separate development and production settings, move secrets to a secure environment, use a production application server, configure CORS for the real frontend, and add monitoring and rate limiting.
