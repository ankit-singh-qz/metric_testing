"""Unit tests for task storage."""

from task_store import TaskStore


def test_create_and_get_task():
    store = TaskStore()
    created = store.create("Example", "Description")
    fetched = store.get(created["id"])
    assert fetched == created
    assert fetched is not None
    assert fetched["description"] == "Description"


def test_update_missing_task_returns_none():
    assert TaskStore().update("missing", {"completed": True}) is None


def test_delete_task_returns_boolean():
    store = TaskStore()
    task = store.create("Example")
    assert store.delete(task["id"]) is True
    assert store.delete(task["id"]) is False
