import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

from app.main import app
from app.database.connenction import Base, get_db


TEST_DATABASE_URL = config("TEST_DATABASE_URL")


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def test_user():
    db = TestingSessionLocal()

    from app.models.models import User
    from app.routers.auth import bcrypt_context

    username = "testuser"
    password = "testpassword"

    user = User(
        username=username,
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return {
        "username": username,
        "password": password
    }
@pytest.fixture
def auth_headers(client, test_user):
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def test_task(client, auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Test Task",
            "description": "This is a test task"
        }
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture(scope="session")
def user_b():
    db = TestingSessionLocal()

    from app.models.models import User
    from app.routers.auth import bcrypt_context

    username = "testuser_b"
    password = "testpassword_b"

    user = User(
        username=username,
        email="testuser_b@example.com",
        first_name="Test",
        last_name="User B",
        hashed_password=bcrypt_context.hash(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.close()

    return {
        "username": username,
        "password": password
    }


@pytest.fixture
def user_b_headers(client, user_b):
    login_response = client.post(
        "/auth/token",
        data={
            "username": user_b["username"],
            "password": user_b["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }