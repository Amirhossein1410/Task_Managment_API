import uuid

def test_create_task(client, auth_headers):
    created_task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Test Task",
            "description": "This is a test task"
        }
    )

    assert created_task_response.status_code == 201

    data = created_task_response.json()

    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["completed"] is False
    assert "user_id" in data

def test_get_all_tasks(client, auth_headers, test_task):
    task_id = test_task["id"]

    get_task_response = client.get("/tasks/", headers=auth_headers)

    assert get_task_response.status_code == 200

    data = get_task_response.json()

    task = next(
        (task for task in data if task["id"] == task_id),
        None
    )

    assert task is not None
    assert task["id"] == task["id"]
    assert task["title"] == "Test Task"
    assert task["description"] == "This is a test task"
    assert task["completed"] is False
    assert "user_id" in task

def test_get_task_by_id(client, auth_headers, test_task):
    task_id = test_task["id"]

    get_task_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert get_task_response.status_code == 200

    data = get_task_response.json()

    assert data is not None
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["completed"] is False
    assert "user_id" in data

def test_get_task_by_invalid_id(client, auth_headers):
    invalid_id = uuid.uuid4()

    get_task_response = client.get(
        f"/tasks/{invalid_id}",
        headers=auth_headers
    )

    assert get_task_response.status_code == 404
    assert get_task_response.json() == {"detail": "Task is not found"}

def test_update_task(client, auth_headers, test_task):
    task_id = test_task["id"]

    updated_task_response = client.patch(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={
            "title": "Test updated task",
            "description": "This is a updated task",
            "completed": True
        }
    )

    assert updated_task_response.status_code == 204

    get_task_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert get_task_response.status_code == 200

    data = get_task_response.json()

    assert data["id"] == task_id
    assert data["title"] == "Test updated task"
    assert data["description"] == "This is a updated task"
    assert data["completed"] is True
    assert "user_id" in data

def test_update_task_by_invalid_id(client, auth_headers):
    invalid_id = uuid.uuid4()

    updated_task_response = client.patch(
        f"/tasks/{invalid_id}",
        headers=auth_headers,
        json={
            "title": "Test updated task",
            "description": "This is an updated task"
        }
    )

    assert updated_task_response.status_code == 404
    assert updated_task_response.json() == {"detail": "Task is not found"}

def test_delete_task(client, auth_headers, test_task):
    task_id = test_task["id"]

    delete_task_response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert delete_task_response.status_code == 204

    get_task_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert get_task_response.status_code == 404
    assert get_task_response.json() == {"detail": "Task is not found"}

def test_delete_task_by_invalid_id(client, auth_headers):
    invalid_id = uuid.uuid4()

    delete_task_response = client.delete(
        f"/tasks/{invalid_id}",
        headers=auth_headers
    )

    assert delete_task_response.status_code == 404
    assert delete_task_response.json() == {"detail": "Task is not found"}

def test_get_task_ownership(client, test_task ,user_b_headers):
    task_id = test_task["id"]

    user_b_response = client.get(
        f"/tasks/{task_id}",
        headers=user_b_headers
    )
    assert user_b_response.status_code == 404

def test_update_task_ownership(client, test_task ,user_b_headers):
    task_id = test_task["id"]
    user_b_response = client.patch(
        f"/tasks/{task_id}",
        headers=user_b_headers,
        json={
            "title": "Test updated task by user B",
            "description": "This is an updated task by user B",
            "completed": True

        }
    )

    assert user_b_response.status_code == 404
    assert user_b_response.json() == {"detail": "Task is not found"}

def test_delete_task_ownership(client,auth_headers, test_task ,user_b_headers):
    task_id = test_task["id"]

    user_b_response = client.delete(
        f"/tasks/{task_id}",
        headers=user_b_headers
    )

    assert user_b_response.status_code == 404
    assert user_b_response.json() == {"detail": "Task is not found"}

    user_a_response = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers
    )

    assert user_a_response.status_code == 200

def test_create_task_without_title(client,auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "description": "This is a test task"
        }
    )

    assert response.status_code == 422

def test_create_task_without_description(client,auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "This is a test task"
        }
    )

    assert response.status_code == 422

def test_create_task_with_invalid_title_type(client,auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": 1,
            "description": "This is a test task"
        }
    )

    assert response.status_code == 422

def test_create_task_with_invalid_description_type(client,auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "This is a test task",
            "description": 1
        }
    )

    assert response.status_code == 422

def test_update_task_with_invalid_completed_type(client,auth_headers,test_task):
    response = client.patch(
        f"/tasks/{test_task['id']}",
        headers=auth_headers,
        json={
            "title": "Test updated task",
            "description": "This is an updated task",
            "completed": "Invalid type"
        }
    )

    assert response.status_code == 422

def test_create_task_with_empty_title(client,auth_headers):
    response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "",
            "description": "This is a test task"
        }
    )

    assert response.status_code == 422