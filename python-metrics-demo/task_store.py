"""Thread-safe in-memory task storage for the sample API."""

from __future__ import annotations

from threading import RLock
from uuid import uuid4
from typing import Any


class TaskStore:
    """Minimal in-memory store. Data resets when the process restarts."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    def create(self, title: str, description: str = "") -> dict[str, Any]:
        task = {
            "id": str(uuid4()),
            "title": title,
            "description": description,
            "completed": False,
        }
        with self._lock:
            self._tasks[task["id"]] = task
            return dict(task)

    def list_tasks(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(task) for task in self._tasks.values()]

    def get(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            return dict(task) if task is not None else None

    def update(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task.update(updates)
            return dict(task)

    def delete(self, task_id: str) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
