"""Small Flask task API used to demonstrate Python/GitHub delivery metrics."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

from task_store import TaskStore


def create_app(store: TaskStore | None = None) -> Flask:
    """Create the Flask app; a store can be injected for tests."""
    app = Flask(__name__)
    task_store = store or TaskStore()

    def json_object() -> dict[str, Any] | None:
        body = request.get_json(silent=True)
        return body if isinstance(body, dict) else None

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/tasks")
    def list_tasks():
        return jsonify({"tasks": task_store.list_tasks()}), 200

    @app.post("/tasks")
    def create_task():
        body = json_object()
        if body is None:
            return jsonify({"error": "Request body must be a JSON object."}), 400

        title = body.get("title")
        description = body.get("description", "")
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "'title' must be a non-empty string."}), 400
        if not isinstance(description, str):
            return jsonify({"error": "'description' must be a string."}), 400

        task = task_store.create(title=title.strip(), description=description.strip())
        return jsonify({"task": task}), 201

    @app.get("/tasks/<task_id>")
    def get_task(task_id: str):
        task = task_store.get(task_id)
        if task is None:
            return jsonify({"error": "Task not found."}), 404
        return jsonify({"task": task}), 200

    @app.patch("/tasks/<task_id>")
    def update_task(task_id: str):
        body = json_object()
        if body is None:
            return jsonify({"error": "Request body must be a JSON object."}), 400
        if not body:
            return jsonify({"error": "Provide at least one field to update."}), 400

        allowed = {"title", "description", "completed"}
        unknown = set(body) - allowed
        if unknown:
            return jsonify({"error": f"Unsupported field(s): {', '.join(sorted(unknown))}."}), 400

        if "title" in body and (not isinstance(body["title"], str) or not body["title"].strip()):
            return jsonify({"error": "'title' must be a non-empty string."}), 400
        if "description" in body and not isinstance(body["description"], str):
            return jsonify({"error": "'description' must be a string."}), 400
        if "completed" in body and not isinstance(body["completed"], bool):
            return jsonify({"error": "'completed' must be a boolean."}), 400

        updates = dict(body)
        if "title" in updates:
            updates["title"] = updates["title"].strip()
        if "description" in updates:
            updates["description"] = updates["description"].strip()

        task = task_store.update(task_id, updates)
        if task is None:
            return jsonify({"error": "Task not found."}), 404
        return jsonify({"task": task}), 200

    @app.delete("/tasks/<task_id>")
    def delete_task(task_id: str):
        if not task_store.delete(task_id):
            return jsonify({"error": "Task not found."}), 404
        return "", 204

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)
