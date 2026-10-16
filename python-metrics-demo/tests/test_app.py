"""API-level tests using Flask's built-in test client."""

import pytest

from app import create_app
from task_store import TaskStore


@pytest.fixture()
def client():
    app = create_app(TaskStore())
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_and_list_task(client):
    created = client.post("/tasks", json={"title": "Write tests", "description": "Add coverage"})
    assert created.status_code == 201
    task = created.get_json()["task"]
    assert task["title"] == "Write tests"
    assert task["completed"] is False

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.get_json()["tasks"]) == 1


def test_create_task_requires_title(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400
    assert "title" in response.get_json()["error"]


def test_non_object_json_is_rejected(client):
    response = client.post("/tasks", json=["not", "an", "object"])
    assert response.status_code == 400


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/not-a-real-id")
    assert response.status_code == 404


def test_patch_task(client):
    created = client.post("/tasks", json={"title": "Draft"})
    task_id = created.get_json()["task"]["id"]

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True, "title": "Drafted"})
    assert updated.status_code == 200
    assert updated.get_json()["task"]["completed"] is True
    assert updated.get_json()["task"]["title"] == "Drafted"


def test_patch_rejects_unknown_fields(client):
    created = client.post("/tasks", json={"title": "Draft"})
    task_id = created.get_json()["task"]["id"]
    response = client.patch(f"/tasks/{task_id}", json={"admin": True})
    assert response.status_code == 400


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"})
    task_id = created.get_json()["task"]["id"]
    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404

def test_create_task_rejects_non_string_title(client):
    response = client.post("/tasks", json={"title": 123})
    assert response.status_code == 400


def test_create_task_rejects_non_string_description(client):
    response = client.post(
        "/tasks",
        json={"title": "Valid task", "description": 123},
    )
    assert response.status_code == 400


def test_create_task_trims_title_and_description(client):
    response = client.post(
        "/tasks",
        json={"title": "  Valid task  ", "description": "  Details  "},
    )
    assert response.status_code == 201
    task = response.get_json()["task"]
    assert task["title"] == "Valid task"
    assert task["description"] == "Details"