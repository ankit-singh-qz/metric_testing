# Installation and Use — Python Metrics Bundle

## 1. Copy files into your repository

Extract the ZIP. Copy `python-metrics-demo/`, `.github/`, `docs/`, `AI_USAGE.md`, and this file into the root of your existing Git repository.

If `.github/` or `docs/` already exists, **merge** the new files into those folders; do not replace existing workflows, templates, or documentation. The code stays in `python-metrics-demo/` so it does not overwrite your main application's files.

## 2. Install dependencies on Windows PowerShell

Open a terminal at `python-metrics-demo/`. If you already have a Python virtual environment, activate it and skip creating another environment. For a new environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If your current `.venv` is in the parent repository folder, you can activate it from the repository root first, then `cd python-metrics-demo` and install requirements from there.

## 3. Test and run

```powershell
python -m pytest -q
python app.py
```

Open `http://127.0.0.1:5000/health` in your browser. This is a local demo; task data resets when the app stops.

## 4. Push via a branch

From the **repository root**:

```powershell
git checkout -b feature/python-metrics-demo
git add python-metrics-demo .github docs AI_USAGE.md INSTALL_AND_USE.md
git commit -m "Add AI-assisted Python metrics demo"
git push -u origin feature/python-metrics-demo
```

Open a pull request on GitHub, link it to an issue, disclose AI assistance, and request a real review. Review, throughput, rework, lead-time, and attribution metrics should come from actual activity; do not fabricate events to improve the results.

## 5. Deployment

`.github/workflows/deploy-python-example.yml.example` is intentionally inactive. Configure your chosen hosting provider, credentials, and an actual deployment command before renaming it to a `.yml` workflow file. Do not call a CI test run a deployment.
