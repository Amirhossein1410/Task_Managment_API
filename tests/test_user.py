import uuid

def test_get_all_users(client, auth_headers, test_user):
    response = client.get(
        "/users/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["username"] == test_user["username"]


def test_get_users_does_not_expose_password(
        client,
        auth_headers
):
    response = client.get(
        "/users/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert "hashed_password" not in data[0]

def test_get_user_by_id(
        client,
        auth_headers,
        db_session,
        test_user
):
    from app.models.models import User

    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    response = client.get(
        f"/users/{user.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user.id)
    assert data["username"] == test_user["username"]
    assert "hashed_password" not in data


def test_get_user_by_invalid_id(
        client,
        auth_headers
):
    invalid_id = uuid.uuid4()

    response = client.get(
        f"/users/{invalid_id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_other_user(
        client,
        auth_headers,
        db_session,
        user_b
):
    from app.models.models import User

    other_user = (
        db_session.query(User)
        .filter(User.username == user_b["username"])
        .first()
    )

    response = client.get(
        f"/users/{other_user.id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_update_user(
        client,
        auth_headers,
        db_session,
        test_user
):
    from app.models.models import User

    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    response = client.patch(
        f"/users/{user.id}",
        headers=auth_headers,
        json={
            "first_name": "Updated"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "Updated"


def test_update_user_multiple_fields(
        client,
        auth_headers,
        db_session,
        test_user
):
    from app.models.models import User

    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    response = client.patch(
        f"/users/{user.id}",
        headers=auth_headers,
        json={
            "first_name": "New",
            "last_name": "Name"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "New"
    assert data["last_name"] == "Name"


def test_update_other_user(
        client,
        auth_headers,
        db_session,
        user_b
):
    from app.models.models import User

    other_user = (
        db_session.query(User)
        .filter(User.username == user_b["username"])
        .first()
    )

    response = client.patch(
        f"/users/{other_user.id}",
        headers=auth_headers,
        json={
            "first_name": "Hacked"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You can only update your own account"
    )


def test_update_user_with_invalid_id(
        client,
        auth_headers
):
    invalid_id = uuid.uuid4()

    response = client.patch(
        f"/users/{invalid_id}",
        headers=auth_headers,
        json={
            "first_name": "Updated"
        }
    )

    assert response.status_code == 403


def test_update_user_without_fields(
        client,
        auth_headers,
        db_session,
        test_user
):
    from app.models.models import User

    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    response = client.patch(
        f"/users/{user.id}",
        headers=auth_headers,
        json={}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_update_user_invalid_type(
        client,
        auth_headers,
        db_session,
        test_user
):
    from app.models.models import User

    user = (
        db_session.query(User)
        .filter(User.username == test_user["username"])
        .first()
    )

    response = client.patch(
        f"/users/{user.id}",
        headers=auth_headers,
        json={
            "is_active": "invalid"
        }
    )

    assert response.status_code == 422

def test_delete_user(
        client,
        db_session
):
    from app.models.models import User
    from app.routers.auth import bcrypt_context

    username = "delete_test_user"
    password = "password"

    user = User(
        username=username,
        email="delete_test@example.com",
        first_name="Delete",
        last_name="Test",
        hashed_password=bcrypt_context.hash(password)
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user_id = user.id

    login_response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.delete(
        f"/users/{user_id}",
        headers=headers
    )

    assert response.status_code == 204

    deleted_user = (
        db_session.query(User)
        .filter(User.id == user_id)
        .first()
    )

    assert deleted_user is None


def test_delete_other_user(
        client,
        auth_headers,
        db_session,
        user_b
):
    from app.models.models import User

    other_user = (
        db_session.query(User)
        .filter(User.username == user_b["username"])
        .first()
    )

    response = client.delete(
        f"/users/{other_user.id}",
        headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You can only delete your own account"
    )


def test_delete_user_with_invalid_id(
        client,
        auth_headers
):
    invalid_id = uuid.uuid4()

    response = client.delete(
        f"/users/{invalid_id}",
        headers=auth_headers
    )

    assert response.status_code == 403