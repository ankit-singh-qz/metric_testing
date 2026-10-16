# Python Metrics Demo

A small Flask task-management API intended as a real, testable example for a GitHub engineering-metrics repository. It is separate from the repository's main application.

## Requirements

- Python 3.10 or later
- pip

## Run on Windows PowerShell

From this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python app.py
```

If your repository already has a working `.venv`, activate that environment and skip creating another one. The API listens at `http://127.0.0.1:5000` by default.

## Endpoints

- `GET /health` — health check
- `GET /tasks` — list tasks; optionally filter with `?completed=true` or
  `?completed=false`, and search titles/descriptions with `?q=keyword`.
  Filters can be combined, for example `/tasks?completed=false&q=report`.
- `POST /tasks` — create a task (`{"title":"Example","description":"Optional"}`)
- `GET /tasks/<id>` — get a task
- `PATCH /tasks/<id>` — update `title`, `description`, and/or `completed`
- `DELETE /tasks/<id>` — delete a task

Storage is in memory and resets when the process restarts. This demo is not intended to be a production service.
