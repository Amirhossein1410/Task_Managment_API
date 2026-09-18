# Task Management API

A production-oriented RESTful Task Management API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **JWT authentication**, **Docker**, **Docker Compose**, and **GitHub Actions**.

The project demonstrates a practical backend development and deployment workflow, including authentication, database management, API validation, automated testing, containerization, health checks, and automated Docker image publishing.

---

## Features

* User registration
* User authentication
* JWT-based authentication
* Password hashing with bcrypt
* User management
* Task CRUD operations
* User-owned tasks
* Request and response validation with Pydantic
* PostgreSQL database
* SQLAlchemy ORM
* Database migrations with Alembic
* Automated testing with Pytest
* Dockerized application
* Docker Compose
* PostgreSQL persistent storage with Docker volumes
* PostgreSQL and API health checks
* Container restart policy
* Gunicorn with Uvicorn workers
* GitHub Actions CI
* Automated Docker image publishing to Docker Hub

---

## Tech Stack

| Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| Python 3.11      | Programming language           |
| FastAPI          | Web framework                  |
| Pydantic         | Data validation and schemas    |
| PostgreSQL 16    | Relational database            |
| SQLAlchemy       | ORM                            |
| Alembic          | Database migrations            |
| JWT              | Authentication                 |
| Passlib / bcrypt | Password hashing               |
| Pytest           | Automated testing              |
| Uvicorn          | ASGI server                    |
| Gunicorn         | Production process manager     |
| Docker           | Containerization               |
| Docker Compose   | Multi-container application    |
| GitHub Actions   | CI and Docker image publishing |
| Docker Hub       | Container image registry       |

---

## Project Structure

```text
Task_Managment_API/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   └── connenction.py
│   │
│   ├── models/
│   │   └── models.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── users.py
│   │
│   ├── schemas/
│   │   ├── Auth.py
│   │   ├── Task.py
│   │   └── User.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_task.py
│   └── test_user.py
│
├── alembec/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Architecture

The application follows a modular backend structure:

```text
Client
  │
  ▼
FastAPI
  │
  ├── Routers
  │     ├── Authentication
  │     ├── Users
  │     └── Tasks
  │
  ├── Schemas
  │     └── Request / Response Validation
  │
  ├── Security
  │     └── JWT + Password Hashing
  │
  ├── Database Layer
  │     └── SQLAlchemy
  │
  ▼
PostgreSQL
```

When running with Docker Compose:

```text
┌──────────────────────┐
│      API Container   │
│  FastAPI + Gunicorn  │
└──────────┬───────────┘
           │
           │ Database Connection
           ▼
┌──────────────────────┐
│ PostgreSQL Container │
│      PostgreSQL 16   │
└──────────┬───────────┘
           │
           ▼
     Docker Volume
```

---

## Authentication

The API uses **JWT-based authentication**.

Authentication flow:

```text
Register
   ↓
Password Hashing
   ↓
User Stored in PostgreSQL
   ↓
Login
   ↓
Credentials Validation
   ↓
JWT Access Token
   ↓
Authenticated Requests
```

Protected endpoints require a valid access token.

Passwords are never stored as plain text. Passwords are hashed before being stored in the database.

---

## Database

The project uses **PostgreSQL 16** as its relational database.

**SQLAlchemy** is used as the ORM layer between the application and PostgreSQL.

The main database entities are:

### User

Contains information such as:

* Username
* Email
* First name
* Last name
* Hashed password
* Active status
* Creation timestamp

### Task

Contains information such as:

* Title
* Description
* Completion status
* Owner
* Creation timestamp
* Update timestamp

Each task belongs to a specific user.

---

## Database Migrations

Database schema changes are managed using **Alembic**.

Apply the latest migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

---

## Environment Variables

Sensitive configuration is provided through environment variables.

Typical configuration includes:

```text
DATABASE_URL
TEST_DATABASE_URL
SECRET_KEY
```

Environment files containing secrets are intentionally excluded from Git.

Do not commit:

```text
.env
docker-compose.env
```

For local development, create the required environment files and provide the appropriate database connection and secret configuration.

---

# Running Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd Task_Managment_API
```

## 2. Create a virtual environment

```bash
python3.11 -m venv .venv
```

Activate it:

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a local `.env` file and provide the required configuration.

A PostgreSQL instance must be available for the application.

## 5. Apply database migrations

```bash
alembic upgrade head
```

## 6. Start the API

For development:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Running with Docker Compose

Docker Compose runs the API and PostgreSQL as separate containers.

Start the application:

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```

Expected services:

```text
api       → healthy
postgres  → healthy
```

Stop the services:

```bash
docker compose stop
```

Start them again:

```bash
docker compose start
```

Recreate or start the stack:

```bash
docker compose up -d
```

If the database schema has not been migrated yet, run:

```bash
docker compose exec api alembic upgrade head
```

---

## PostgreSQL Persistence

PostgreSQL uses a Docker named volume:

```text
postgres_data
```

The named volume allows PostgreSQL data to persist when the PostgreSQL container is removed and recreated.

Avoid using:

```bash
docker compose down -v
```

unless you intentionally want to remove the database volume and its data.

---

## Health Checks

### API

The root endpoint is used as the API health endpoint:

```http
GET /
```

Expected response:

```json
{
  "status": "Ok"
}
```

Docker Compose uses this endpoint for the API container health check.

### PostgreSQL

PostgreSQL uses `pg_isready` to verify that the database is ready to accept connections.

The API service is configured to wait for PostgreSQL to become healthy before starting.

---

# API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Tests cover:

* Authentication
* User operations
* Task operations

The test suite uses a separate PostgreSQL database configuration.

The GitHub Actions workflow also runs the automated test suite against PostgreSQL.

---

# Production Server

The Docker container runs the application using:

```text
Gunicorn
    +
Uvicorn Worker
```

Gunicorn manages multiple Uvicorn worker processes.

The current Docker configuration uses two workers.

For machine-learning model serving, worker count should be chosen carefully because separate worker processes can result in multiple copies of an in-memory model.

---

# Docker

The application is containerized using Docker.

Build the image manually:

```bash
docker build -t task-management-api .
```

Run the container:

```bash
docker run -p 8000:8000 task-management-api
```

Docker Compose is recommended for running the complete application because it also provides the PostgreSQL service, persistent storage, environment configuration, and health checks.

---

# CI/CD — GitHub Actions

GitHub Actions automatically validates the project whenever changes are pushed to the `master` branch or a Pull Request targets the `master` branch.

The workflow performs the following steps:

```text
Git Push / Pull Request
          ↓
   GitHub Actions
          ↓
    Ubuntu Runner
          ↓
    Start PostgreSQL
          ↓
   Install Dependencies
          ↓
   Run Alembic Migrations
          ↓
       Run Pytest
          ↓
    Build Docker Image
          ↓
 Authenticate with Docker Hub
          ↓
    Push Docker Image
```

The Docker build and Docker Hub publishing job runs only after the test job succeeds.

The pipeline verifies that:

* Dependencies can be installed successfully.
* Database migrations work correctly.
* Automated tests pass.
* The Docker image can be built successfully.
* The Docker image can be published to Docker Hub.

The workflow configuration is located at:

```text
.github/workflows/ci.yml
```

The current pipeline provides:

* **Continuous Integration (CI)**
* **Automated Docker image building**
* **Automated Docker image publishing to Docker Hub**

A full Continuous Deployment step is not currently configured because the project does not use a VPS or cloud server.

---

# Docker Hub

The project Docker image is automatically published to Docker Hub through GitHub Actions after the test job succeeds.

The workflow is:

```text
Git Push
   ↓
GitHub Actions
   ↓
Run Tests
   ↓
Build Docker Image
   ↓
Authenticate with Docker Hub
   ↓
Push Image
```

Docker image repository:

```text
amirhossein1410/task-management-api
```

The workflow publishes two tags:

```text
latest
<git-commit-sha>
```

The commit SHA tag provides a unique reference to the Docker image built from a specific Git commit.

Docker Hub credentials are stored as **GitHub Actions Secrets** and are not included directly in the repository or workflow configuration.

---

# Security

The project follows several basic security practices:

* Passwords are hashed before storage.
* JWT is used for authenticated requests.
* Sensitive configuration is provided through environment variables.
* Secret environment files are excluded from Git.
* Dependencies are defined in `requirements.txt`.
* API input is validated using Pydantic.
* Database operations are handled through SQLAlchemy and parameterized database operations.

Never commit real credentials, passwords, API keys, JWT secrets, database credentials, or other sensitive configuration to the repository.

---

# Development Workflow

The development workflow is:

```text
Create / Modify Feature
        ↓
Run Tests Locally
        ↓
Git Commit
        ↓
Git Push
        ↓
GitHub Actions
        ↓
Start PostgreSQL
        ↓
Run Alembic Migrations
        ↓
Run Pytest
        ↓
Build Docker Image
        ↓
Push Image to Docker Hub
```

This workflow provides automated validation and Docker image delivery for successful pushes to the `master` branch.

---

# Project Goals

This project is designed to demonstrate practical backend and software-engineering skills relevant to production-oriented Python and AI/ML engineering workflows.

It provides practical experience with:

* REST API development
* Authentication and JWT
* Relational databases
* SQLAlchemy ORM
* Database migrations with Alembic
* Automated testing with Pytest
* Containerization with Docker
* Multi-container applications with Docker Compose
* PostgreSQL persistence with Docker volumes
* API health checks
* Production API serving with Gunicorn and Uvicorn workers
* Git and GitHub
* GitHub Actions
* Automated Docker image delivery to Docker Hub

The architecture also provides a foundation for a future **ML/DL model-serving API**, where a trained machine-learning model can be exposed through FastAPI, containerized with Docker, and eventually deployed to a production server.

---

## License

No open-source license has been added to this repository yet.
