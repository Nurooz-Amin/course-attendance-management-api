# Publish the Project on GitHub

## 1. Run and verify the project

From the extracted project directory:

```bash
chmod +x setup.sh run.sh verify.sh
./setup.sh
./verify.sh
./run.sh
```

Open these pages:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/api/docs/
http://127.0.0.1:8000/api/health/
```

The setup script runs migrations, creates demo accounts, performs Django checks, and runs the automated tests before you publish.

## 2. Create the GitHub repository

Create a new **public** repository named:

```text
course-attendance-management-api
```

Use this description:

```text
Role-based Course and Attendance Management REST API built with Django REST Framework, JWT, validation, tests, Swagger, Postman and GitHub Actions.
```

Recommended topics:

```text
django django-rest-framework python rest-api jwt authentication attendance-management swagger postman github-actions backend portfolio-project
```

Do not initialize the remote repository with another README, `.gitignore`, or license because this project already includes them.

## 3. Create the first commit

```bash
git init
git branch -M main
git status
git add .
git commit -m "feat: build course and attendance management REST API"
```

## 4. Connect and push

```bash
git remote add origin https://github.com/Nurooz-Amin/course-attendance-management-api.git
git push -u origin main
```

Confirm the remote:

```bash
git remote -v
```

## 5. Add a development branch

```bash
git checkout -b develop
git push -u origin develop
git checkout main
```

## 6. Improve the visible repository

After pushing:

1. Add the repository description and topics shown above.
2. Pin the repository on your GitHub profile.
3. Add a screenshot of the homepage and Swagger UI to the README.
4. Confirm that the GitHub Actions workflow is green.
5. Create a release named `v1.1.0`.
6. Add the repository to your CV and LinkedIn projects section.

## Suggested CV entry

```text
Course and Attendance Management REST API — Django, DRF, JWT, SQLite
Built a role-based REST API for courses, student enrolments and daily attendance. Implemented JWT authentication, serializer and database validation, object-level permissions, automated API tests, Swagger documentation, Postman requests, Docker support and GitHub Actions CI.
```

## Suggested interview demonstration

1. Open the homepage at `/`.
2. Open Swagger UI at `/api/docs/`.
3. Log in using the instructor demo account.
4. Authorize Swagger with the returned access token.
5. List the seeded course, student, and enrolment.
6. Create an attendance record.
7. Repeat it to show duplicate-record prevention.
8. Submit a future date to show serializer validation.
9. Log in as the student and show that creating attendance returns `403`.
10. Show the tests and GitHub Actions workflow.

## Demo credentials

```text
Admin:      admin / AdminPass123
Instructor: instructor / InstructorPass123
Student:    student / StudentPass123
```

These accounts are for local demonstration only.
