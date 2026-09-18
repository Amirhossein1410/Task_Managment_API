from jose import jwt
from uuid import uuid4
from datetime import timedelta
from app.models.models import User
from app.core.config import SECRET_KEY
from app.core.security import ALGORITHM,create_access_token

def test_register_success(client):
    username = f"register_{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == username
    assert data["email"] == email
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert "id" in data
    assert "created_at" in data
    assert data["is_active"] is True

    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/auth/register",
        json={
            "username": test_user["username"],
            "email": f"{uuid4().hex}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword"
        }
    )

    assert response.status_code == 409


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/auth/register",
        json={
            "username": f"register_{uuid4().hex[:8]}",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword"
        }
    )

    assert response.status_code == 409


def test_register_missing_required_field(client):
    response = client.post(
        "/auth/register",
        json={
            "username": f"register_{uuid4().hex[:8]}",
            "email": f"{uuid4().hex}@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 422


def test_register_invalid_password_type(client):
    response = client.post(
        "/auth/register",
        json={
            "username": f"register_{uuid4().hex[:8]}",
            "email": f"{uuid4().hex}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": 12345
        }
    )

    assert response.status_code == 422

def test_login_success(client, test_user):
    response = client.post(
        "/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/token",
        data={
            "username": test_user["username"],
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_wrong_username(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "non_existing_user",
            "password": "testpassword"
        }
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_inactive_user(client, test_user, db_session):
    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    assert user is not None

    user.is_active = False
    db_session.commit()

    try:
        response = client.post(
            "/auth/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )

        assert response.status_code == 401

    finally:
        user.is_active = True
        db_session.commit()

def test_valid_token(client, test_user):
    login_response = client.post(
        "/auth/token",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_invalid_token(client):
    response = client.get(
        "/tasks/",
        headers={
            "Authorization": "Bearer fake.invalid.token"
        }
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token(client, test_user, db_session):
    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    assert user is not None

    token = create_access_token(
        user_name=user.username,
        user_id=user.id,
        expires_delta=timedelta(seconds=-1)
    )

    response = client.get(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_missing_token(client):
    response = client.get("/tasks/")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_token_with_missing_claims(client):


    token = jwt.encode(
        {
            "sub": "testuser"
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

def test_register_response_does_not_expose_password(client):
    username = f"security_{uuid4().hex[:8]}"

    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "first_name": "Security",
            "last_name": "Test",
            "password": "supersecret"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "password" not in data
    assert "hashed_password" not in data